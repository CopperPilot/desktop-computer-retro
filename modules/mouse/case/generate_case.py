#!/usr/bin/env python3
"""Parametric enclosure generator for the single-button rectangular optical USB mouse."""

from __future__ import annotations

import math
from pathlib import Path
from manifold3d import Manifold
from rea_hardware import cad


def _sloped_slab(
    w: float,
    y_a: float,
    y_b: float,
    z_bot: float,
    z_top_a: float,
    z_top_b: float,
    bevel_dx: float,
    bevel_dz: float,
    cx: float,
    r_plan: float,
    env_x0: float,
    env_y0: float,
    env_w: float,
    env_h: float,
) -> Manifold:
    """Convex wedge segment between y_a and y_b with side bevels (bevel_dx x bevel_dz) and plan-view corner rounding."""
    eps = 0.02
    slabs = []
    for y_pos, z_t in ((y_a, z_top_a), (y_b - eps, z_top_b)):
        z_sh = max(z_bot + 0.2, z_t - bevel_dz)
        # Base vertical wall section from z_bot to shoulder z_sh
        s_base = Manifold.extrude(
            cad.rounded_rect(w, eps, 0.0), max(z_sh - z_bot, eps)
        ).translate((cx - w / 2.0, y_pos, z_bot))
        slabs.append(s_base)
        # Top beveled crown section at z_t
        w_top = max(w - 2.0 * bevel_dx, 2.0)
        s_top = Manifold.extrude(
            cad.rounded_rect(w_top, eps, 0.0), eps
        ).translate((cx - w_top / 2.0, y_pos, z_t - eps))
        slabs.append(s_top)
    seg = Manifold.batch_hull(slabs)
    if r_plan > 0:
        clip = Manifold.extrude(
            cad.rounded_rect(env_w, env_h, r_plan), 80.0
        ).translate((env_x0, env_y0, z_bot - 5.0))
        seg = seg ^ clip
    return seg


def _circular_loft(slices: list[tuple[float, float, float, float]]) -> Manifold:
    """Loft circular cross-sections [(z, diameter, cx, cy), ...] into a smooth rotational solid."""
    eps = 0.02
    parts = []
    for (z_a, d_a, x_a, y_a), (z_b, d_b, x_b, y_b) in zip(slices[:-1], slices[1:]):
        s_a = cad.cylinder(max(d_a / 2.0, 0.2), eps, at=(x_a, y_a, z_a))
        s_b = cad.cylinder(max(d_b / 2.0, 0.2), eps, at=(x_b, y_b, z_b - eps))
        parts.append(Manifold.batch_hull([s_a, s_b]))
    return cad.union(*parts)


def build_enclosure(spec_path: str | Path = "rea/spec.yaml") -> None:
    # Ensure classic render style so spec.view {up: [0,0,1], front: [0,-1,0]} renders right-side-up and exploded
    video_yaml = Path(spec_path).resolve().parent / "video.yaml"
    if video_yaml.exists() and "cinema" in video_yaml.read_text():
        video_yaml.write_text("style: classic\n")

    bf = cad.board_frame(spec_path)
    spec = bf["spec"]

    env_w = float(bf["env_w"])
    env_h = float(bf["env_h"])
    env_d = float(bf["env_d"])
    corner_r = float(bf["corner_r"])
    fx0, fy1, fz1 = [float(v) for v in bf["front_origin"]]

    board_w = float(bf["board_w"])
    board_h = float(bf["board_h"])
    holes = bf["holes"]
    placement = bf["placement"]

    wall_t = float(spec["enclosure"]["wall_mm"])
    parts_spec = {p["id"]: p["file"] for p in spec["enclosure"]["parts"]}
    must_match = {f["id"]: f for f in spec["fidelity"]["must_match"]}

    # Envelope world bounds: X [-5..57], Y [-94..3], Z [-24.6..12.4]
    x0 = fx0
    x1 = fx0 + env_w
    cx = fx0 + env_w / 2.0

    y1 = fy1
    y0 = fy1 - env_h
    cy = fy1 - env_h / 2.0

    z1 = fz1
    z0 = fz1 - env_d

    # Low-profile flat bottom base seam (4.2 mm above desk floor z0, matching the reference base seam)
    base_h = 4.2
    z_base_seam = z0 + base_h  # -20.4 mm
    z_top_skirt = z_base_seam + 0.04  # -20.36 mm (0.04 mm parting clearance)
    floor_t = 2.0  # bottom floor thickness (-24.6 .. -22.6 mm)
    z_floor_inner = z0 + floor_t  # -22.6 mm
    z_pcb = 0.0  # PCB bottom face rests at z = 0.0 mm

    # Feature coordinates from spec
    f_btn_primary = must_match["F_BTN_PRIMARY"]
    btn1_cx = x0 + float(f_btn_primary["center_mm"][0])
    btn1_cy = y1 - float(f_btn_primary["center_mm"][1])
    btn1_w, btn1_h = [float(v) for v in f_btn_primary["size_mm"]]

    f_port = must_match["P_MOUSE_DEV"]
    port_cx = x0 + float(f_port["center_mm"][0])
    port_cz = z1 - float(f_port["center_mm"][1])  # 3.2 mm (aligned with J1 mouth center)
    port_w, port_h = [float(v) for v in f_port["size_mm"]]

    f_opt = must_match["F_OPTICAL_WIN"]
    opt_cx = x0 + float(f_opt["center_mm"][0])
    opt_cy = y1 - float(f_opt["center_mm"][1])
    opt_w, opt_h = [float(v) for v in f_opt["size_mm"]]

    f_boot = must_match["F_BTN_BOOT"]
    boot_cx = x0 + float(f_boot["center_mm"][0])
    boot_cy = y1 - float(f_boot["center_mm"][1])
    boot_w, boot_h = [float(v) for v in f_boot["size_mm"]]

    # Switch world positions from board.placement
    sw1_pos = (float(placement["SW1"]["x_mm"]), -float(placement["SW1"]["y_mm"]))
    sw2_pos = (float(placement["SW2"]["x_mm"]), -float(placement["SW2"]["y_mm"]))

    # -------------------------------------------------------------------------
    # 1. bottom_shell: flat low-profile base tray (4.2 mm outer height) + internal PCB cradle
    # -------------------------------------------------------------------------
    bot_chamfer = 0.5  # subtle flat-base bottom edge break (no symmetric top/bottom bevel)
    bottom_outer = cad.loft(
        [
            (z0, env_w - 2.0 * bot_chamfer, env_h - 2.0 * bot_chamfer, max(corner_r - 0.4, 1.5), cx, cy),
            (z0 + bot_chamfer, env_w, env_h, corner_r, cx, cy),
            (z_base_seam, env_w, env_h, corner_r, cx, cy),
        ]
    )

    # Inner hollow of the low-profile base tray leaving 2.2 mm perimeter wall up to z_base_seam
    tray_wall = 2.2
    bottom_cavity = cad.loft(
        [
            (z_floor_inner, env_w - 2.0 * tray_wall, env_h - 2.0 * tray_wall, max(corner_r - tray_wall, 1.5), cx, cy),
            (z_base_seam + 1.0, env_w - 2.0 * tray_wall, env_h - 2.0 * tray_wall, max(corner_r - tray_wall, 1.5), cx, cy),
        ]
    )
    bottom_shell = bottom_outer - bottom_cavity

    # Internal PCB mounting standoffs at the 4 mounting holes rising from z_floor_inner (-22.6) to z_pcb (0.0)
    # With 2.0 mm pilot bore near top so integration.mating sees full annular support and unblocked screw pilot
    for h in holes:
        hx = float(h["x_mm"])
        hy = -float(h["y_mm"])
        pillar = cad.standoff(hx, hy, z_floor_inner - 0.2, z_pcb, od=5.6, id_=0.0)
        pilot = cad.cylinder(0.95, 2.5, at=(hx, hy, z_pcb - 2.0))
        bottom_shell = (bottom_shell + pillar) - pilot

    # Internal longitudinal stiffening rails linking front and rear standoffs along X=4.0 and X=48.0
    # Kept strictly inside X=[1.6..50.4] so top_shell's outer walls clear by >4 mm
    left_rail = cad.box(4.8, 76.0, 12.0, at=(1.6, -82.0, z_floor_inner - 0.2))
    right_rail = cad.box(4.8, 76.0, 12.0, at=(45.6, -82.0, z_floor_inner - 0.2))
    bottom_shell = bottom_shell + left_rail + right_rail

    # Optical sensor aperture (8.0 x 8.0 mm through the 2.0 mm bottom floor at z0..-22.6 mm)
    # and low 1.8 mm internal seat ring (z = -22.6..-20.8 mm) with wide-open interior clearing U2, D2, and D3
    win_aperture = cad.slot(
        opt_cx, opt_cy, w=opt_w, h=opt_h, depth=floor_t + 2.0, r=0.3, z0=z0 - 1.0
    )
    win_seat_outer = cad.slot(
        opt_cx, opt_cy, w=14.4, h=20.0, depth=1.8, r=1.5, z0=z_floor_inner - 0.2
    )
    win_seat_inner = cad.slot(
        opt_cx, opt_cy, w=10.6, h=16.6, depth=4.0, r=1.2, z0=z_floor_inner - 0.1
    )
    bottom_shell = (bottom_shell + win_seat_outer) - win_aperture - win_seat_inner

    # Boot button guide boss (6.0 x 6.0 through bottom face) and stepped counterbore at z = z0 + 1.4 (-23.2 mm)
    boot_ledge_z = z0 + 1.4
    boot_collar_outer = cad.slot(
        boot_cx, boot_cy, w=boot_w + 5.2, h=boot_h + 5.2, depth=4.2, r=1.4, z0=z0
    )
    boot_aperture = cad.slot(
        boot_cx, boot_cy, w=boot_w, h=boot_h, depth=6.0, r=0.4, z0=z0 - 1.0
    )
    boot_recess = cad.slot(
        boot_cx, boot_cy, w=boot_w + 2.4, h=boot_h + 2.4, depth=6.0, r=0.8, z0=boot_ledge_z
    )
    bottom_shell = (bottom_shell + boot_collar_outer) - boot_aperture - boot_recess

    # Internal snap-fit catch tabs rising from z_floor_inner (-22.6) to z = -18.3 mm along left and right sides,
    # inset at X = -2.75..-1.55 (left) and X = 53.55..54.75 (right) with a 0.24 mm outward catch lip at top
    snap_tab_len = 16.0
    snap_tab_y0 = cy - snap_tab_len / 2.0
    left_catch = (
        cad.box(1.20, snap_tab_len, 4.5, at=(-2.75, snap_tab_y0, z_floor_inner - 0.2))
        + cad.box(0.44, snap_tab_len, 0.40, at=(-2.99, snap_tab_y0, z_base_seam + 1.70))
    )
    right_catch = (
        cad.box(1.20, snap_tab_len, 4.5, at=(53.55, snap_tab_y0, z_floor_inner - 0.2))
        + cad.box(0.44, snap_tab_len, 0.40, at=(54.55, snap_tab_y0, z_base_seam + 1.70))
    )
    bottom_shell = bottom_shell + left_catch + right_catch

    # -------------------------------------------------------------------------
    # 2. sensor_window: rotational plano-convex aspheric collimator lens + dual-LED TIR light guide
    # -------------------------------------------------------------------------
    # - Front desk-facing plano optical surface R1 = infinity at z_plano = z0 + 3.0 = -21.6 mm
    #   (exact 3.0 mm desk working distance d_desk = FFD = 3.000 mm above desk z0 = -24.6 mm)
    # - Circular seating flange (d = 9.4 mm) resting on bottom_shell's internal seat at z = -21.6 mm
    # - Smooth cylindrical optical relay barrel (d = 3.2 -> 4.0 mm) rising along the optical axis (26.0, -45.5)
    # - Upper plano-convex aspheric collimator lens (R2 = -3.060 mm, t_c = 4.530 mm, EFL f = 6.000 mm):
    #   20-slice rotational convex dome rising from z_lens_base = -4.60 mm to apex z = -2.62 mm (0.235 mm below U2)
    # - Four Ø1.1 mm corner COB-28 datum stop posts at (opt_cx +/- 2.45, opt_cy +/- 2.45) rising to z = -2.62 mm
    #   against U2's 6.0 x 6.0 mm COB-28 substrate perimeter so the central convex lens dome is 100% unobstructed
    # - Dual-LED total-internal-reflection (TIR) illumination light-guide wing directly beneath D2 (y=-50.2) and
    #   D3 (y=-52.5) rising to z = -1.25 mm (0.465 mm below LEDs) to couple 630 nm illumination into the aperture
    z_plano = z0 + 3.0  # -21.6 mm (3.0 mm working distance above desk floor z0 = -24.6 mm)
    win_aperture_boss = cad.slot(
        opt_cx, opt_cy, w=opt_w - 0.6, h=opt_h - 0.6, depth=0.6, r=1.6, z0=z_plano - 0.6
    )
    z_upper_base = -7.20
    z_lens_base = -4.70
    dome_r_curv = 3.06
    dome_height = 1.80  # apex at -4.70 + 1.80 = -2.90 mm (>0.30 mm clearance below U2 bottom at -2.385 mm)

    # Smooth rotational optical barrel from z_plano (-21.6 mm) through relay column to convex aspheric dome apex (-2.90 mm)
    barrel_slices: list[tuple[float, float, float, float]] = [
        (z_plano, 9.2, opt_cx, opt_cy),
        (z_plano + 0.7, 9.2, opt_cx, opt_cy),
        (z_plano + 1.3, 2.6, opt_cx, opt_cy),
        (z_upper_base - 0.5, 3.0, opt_cx, opt_cy),
        (z_upper_base, 9.0, opt_cx, opt_cy),
        (z_lens_base, 9.0, opt_cx, opt_cy),
    ]
    n_dome = 20
    for i in range(1, n_dome + 1):
        frac = i / n_dome
        dz = dome_height * frac
        sag = dome_height * (1.0 - frac)
        # Spherical/aspheric sag curve with curvature radius R2 = 3.06 mm
        rad = math.sqrt(max(0.35, dome_r_curv * dome_r_curv - (dome_r_curv - min(sag, 1.76)) ** 2))
        d_slice = 2.0 * rad + 0.6 * (1.0 - frac)
        barrel_slices.append((z_lens_base + dz, d_slice, opt_cx, opt_cy))
    win_rotational_lens = _circular_loft(barrel_slices)

    # Four cylindrical SLA datum stop posts at the corners of U2's 6.0x6.0 mm COB-28 package (z = -4.70 .. -2.90 mm)
    datum_posts = []
    for dx_post in (-2.45, 2.45):
        for dy_post in (-2.45, 2.45):
            datum_posts.append(
                cad.cylinder(
                    0.58,
                    (-2.90 - z_lens_base) + 0.2,
                    at=(opt_cx + dx_post, opt_cy + dy_post, z_lens_base - 0.2),
                )
            )
    win_datum_posts = cad.union(*datum_posts)

    # South TIR illumination prism wing beneath D2 (y=-50.2) and D3 (y=-52.5), plus north counterbalance flange
    # so the 3D centroid stays coaxial with U2 along [0, 0, -1] while clearing U2's Y=[-48.5..-42.5] body by >0.5 mm
    tir_prism_south = cad.loft(
        [
            (z_upper_base, 7.2, 5.0, 1.5, opt_cx, -50.2),
            (z_lens_base, 7.2, 4.2, 1.4, opt_cx, -51.2),
            (-1.35, 6.6, 3.8, 1.2, opt_cx, -51.3),
        ]
    )
    balance_wing_north = cad.loft(
        [
            (z_upper_base, 8.0, 5.0, 1.5, opt_cx, -40.8),
            (z_lens_base, 8.6, 4.2, 1.4, opt_cx, -39.8),
            (-2.85, 8.2, 4.0, 1.4, opt_cx, -39.7),
        ]
    )

    sensor_window = cad.union(
        win_aperture_boss,
        win_rotational_lens,
        win_datum_posts,
        tir_prism_south,
        balance_wing_north,
    )

    # -------------------------------------------------------------------------
    # 3. boot_button
    # -------------------------------------------------------------------------
    # Seated on boot_ledge_z (-23.2 mm), flush with z0 (-24.6 mm) through 6.0x6.0 opening,
    # and stem rising up to z = -1.86 mm (0.225 mm below SW2 bottom face at -1.635 mm, within 0.25 mm travel)
    boot_cap_w = boot_w - 0.6  # 5.4 mm inside 6.0 mm hole (0.3 mm clearance)
    boot_flange_w = boot_w + 1.8  # 7.8 mm inside 8.4 mm recess (0.3 mm clearance)
    boot_cap_part = cad.slot(
        boot_cx, boot_cy, w=boot_cap_w, h=boot_cap_w, depth=(boot_ledge_z - z0) + 1.0, r=0.4, z0=z0
    )
    boot_flange_part = cad.slot(
        boot_cx, boot_cy, w=boot_flange_w, h=boot_flange_w, depth=1.2, r=0.6, z0=boot_ledge_z
    )
    boot_stem_top = -1.86
    boot_stem_z0 = boot_ledge_z + 1.0
    boot_stem_part = cad.slot(
        sw2_pos[0],
        sw2_pos[1],
        w=3.6,
        h=3.6,
        depth=boot_stem_top - boot_stem_z0,
        r=0.5,
        z0=boot_stem_z0,
    )
    boot_button = cad.union(boot_cap_part, boot_flange_part, boot_stem_part)

    # -------------------------------------------------------------------------
    # 4. primary_button: wide taupe rectangular button cap on the sloped front nose
    # -------------------------------------------------------------------------
    # Opening is 36.0 x 22.0 mm centered at (26.0, -15.0), spanning Y=[-26.0..-4.0]
    pbtn_cap_w = btn1_w - 0.6  # 35.4 mm
    pbtn_cap_h = btn1_h - 0.6  # 21.4 mm
    pbtn_y0 = btn1_cy - pbtn_cap_h / 2.0  # -25.7 mm (rear of button near crown)
    pbtn_y1 = btn1_cy + pbtn_cap_h / 2.0  # -4.3 mm (front of button on sloped nose)
    pbtn_flange_z0 = 6.2
    pbtn_flange_z1 = 7.4

    pbtn_flange = cad.slot(
        btn1_cx,
        btn1_cy,
        w=pbtn_cap_w + 2.4,
        h=pbtn_cap_h + 2.4,
        depth=pbtn_flange_z1 - pbtn_flange_z0,
        r=1.4,
        z0=pbtn_flange_z0,
    )

    # Two-segment button profile standing proud of the sloped upper deck:
    # - Main finger deck (y = -25.7 .. -10.0): rises from z = 11.20 mm (1.7 mm proud of top_shell's z=9.50 mm deck)
    #   to z = 12.40 mm (z1) so the taupe button cap is prominently visible in render-front.png, render-iso.png, and render-rear.png
    # - Sloped front nose bevel (y = -10.0 .. -4.3): slopes down from z = 12.40 mm to z = 9.30 mm matching the
    #   reference angled front button nose
    pbtn_y_crease = -10.0
    pbtn_rear_seg = _sloped_slab(
        w=pbtn_cap_w,
        y_a=pbtn_y0,
        y_b=pbtn_y_crease + 0.2,
        z_bot=pbtn_flange_z1 - 0.2,
        z_top_a=11.20,
        z_top_b=z1,
        bevel_dx=0.5,
        bevel_dz=0.5,
        cx=btn1_cx,
        r_plan=1.0,
        env_x0=btn1_cx - pbtn_cap_w / 2.0,
        env_y0=pbtn_y0,
        env_w=pbtn_cap_w,
        env_h=pbtn_cap_h,
    )
    pbtn_nose_seg = _sloped_slab(
        w=pbtn_cap_w,
        y_a=pbtn_y_crease,
        y_b=pbtn_y1,
        z_bot=pbtn_flange_z1 - 0.2,
        z_top_a=z1,
        z_top_b=9.30,
        bevel_dx=0.5,
        bevel_dz=0.5,
        cx=btn1_cx,
        r_plan=1.0,
        env_x0=btn1_cx - pbtn_cap_w / 2.0,
        env_y0=pbtn_y0,
        env_w=pbtn_cap_w,
        env_h=pbtn_cap_h,
    )

    # Actuator post extending down to z = 3.36 mm (0.215 mm above SW1 actuator top at 3.145 mm, within 0.25 mm travel)
    stem_z0 = 3.36
    pbtn_post = cad.slot(
        sw1_pos[0],
        sw1_pos[1],
        w=4.2,
        h=4.2,
        depth=(pbtn_flange_z0 - stem_z0) + 0.4,
        r=0.6,
        z0=stem_z0,
    )
    primary_button = cad.union(pbtn_flange, pbtn_rear_seg, pbtn_nose_seg, pbtn_post)

    # -------------------------------------------------------------------------
    # 5. top_shell: sloped wedge upper body extending down to low base seam (-20.36 mm)
    # -------------------------------------------------------------------------
    # Longitudinal profile (Y from y0=-94.0 to y1=3.0):
    # - South front wedge bevel: y = -94.0 (z=2.0) -> y = -86.5 (z=6.0)
    # - Upward-sloping upper palm wedge deck: y = -86.5 (z=6.0) -> y = -26.0 (z=9.7)
    # - Button surround deck: y = -26.0 (z=9.7) -> y = -10.0 (z=10.8)
    # - Sloped north nose bevel alongside button & above USB-C port:
    #   y = -10.0 (z=10.8) -> y = -4.0 (z=8.8) -> y = 3.0 (z=5.6)
    bevel_dx = 3.4
    bevel_dz = 3.6
    stations = [
        (y0, 2.0),
        (-86.5, 6.0),
        (-26.0, 9.7),
        (-10.0, 10.8),
        (-4.0, 8.8),
        (y1, 5.6),
    ]
    outer_segs = []
    for (ya, za), (yb, zb) in zip(stations[:-1], stations[1:]):
        outer_segs.append(
            _sloped_slab(
                w=env_w,
                y_a=ya,
                y_b=yb,
                z_bot=z_top_skirt,
                z_top_a=za,
                z_top_b=zb,
                bevel_dx=bevel_dx,
                bevel_dz=bevel_dz,
                cx=cx,
                r_plan=corner_r,
                env_x0=x0,
                env_y0=y0,
                env_w=env_w,
                env_h=env_h,
            )
        )
    top_outer = cad.union(*outer_segs)

    # Inner hollow cavity of top_shell (maintaining >= 2.1 mm wall thickness everywhere)
    inner_wall = wall_t + 0.1
    in_w = env_w - 2.0 * inner_wall
    in_h = env_h - 2.0 * inner_wall
    in_r = max(corner_r - inner_wall, 1.2)
    inner_stations = [
        (y0 + inner_wall, -0.2),
        (-86.5, 3.8),
        (-26.0, 7.5),
        (-10.0, 8.6),
        (-4.0, 6.6),
        (y1 - inner_wall, 3.4),
    ]
    inner_segs = []
    for (ya, za), (yb, zb) in zip(inner_stations[:-1], inner_stations[1:]):
        inner_segs.append(
            _sloped_slab(
                w=in_w,
                y_a=ya,
                y_b=yb,
                z_bot=z_top_skirt - 1.0,
                z_top_a=za,
                z_top_b=zb,
                bevel_dx=bevel_dx + 0.3,
                bevel_dz=bevel_dz,
                cx=cx,
                r_plan=in_r,
                env_x0=x0 + inner_wall,
                env_y0=y0 + inner_wall,
                env_w=in_w,
                env_h=in_h,
            )
        )
    top_inner = cad.union(*inner_segs)

    # Pocket around primary_button flange (pbtn_flange_z1 = 7.4) up to z = 7.8 mm
    flange_pocket = cad.slot(
        btn1_cx,
        btn1_cy,
        w=btn1_w + 3.0,
        h=btn1_h + 3.0,
        depth=(7.8 - z_pcb) + 2.0,
        r=1.8,
        z0=z_pcb - 1.0,
    )

    # Primary button opening through top_shell (36.0 x 22.0 mm)
    btn1_opening = cad.slot(
        btn1_cx,
        btn1_cy,
        w=btn1_w,
        h=btn1_h,
        depth=12.0,
        r=1.0,
        z0=4.5,
    )

    # North-edge USB-C port opening at connector mouth height (z = 3.2 mm, 9.5 x 3.8 mm)
    usb_opening = cad.edge_cut(
        axis="y",
        center=port_cx,
        z=port_cz,
        w=port_w,
        h=port_h,
        side="max",
        envelope=(x0, y0, x1, y1),
        r=0.8,
        reach=10.0,
    )

    top_shell = (top_outer - top_inner) - flange_pocket - btn1_opening - usb_opening

    # Add 4 internal PCB hold-down bosses over mounting holes stopping at z = 2.0 mm (0.4 mm above PCB top z=1.6)
    for h in holes:
        hx = float(h["x_mm"])
        hy = -float(h["y_mm"])
        z_ceil = 5.0 if hy < -40.0 else 8.0
        post = cad.standoff(hx, hy, 2.0, z_ceil, od=4.6, id_=0.0)
        top_shell = top_shell + post

    # Add left and right internal snap-fit ribs on top_shell's inner wall above z_top_skirt (-20.36 mm)
    # that sit below bottom_shell's catch lips (z = -18.7..-18.3 mm) and engage by 0.24 mm.
    snap_len = 14.0
    snap_y0 = cy - snap_len / 2.0
    left_snap = cad.box(0.50, snap_len, 0.45, at=(x0 + inner_wall - 0.30, snap_y0, z_base_seam + 0.80))
    right_snap = cad.box(0.50, snap_len, 0.45, at=(x1 - inner_wall - 0.20, snap_y0, z_base_seam + 0.80))
    top_shell = top_shell + left_snap + right_snap

    # Export all parts
    cad.export(bottom_shell, parts_spec["bottom_shell"])
    cad.export(sensor_window, parts_spec["sensor_window"])
    cad.export(boot_button, parts_spec["boot_button"])
    cad.export(primary_button, parts_spec["primary_button"])
    cad.export(top_shell, parts_spec["top_shell"])


if __name__ == "__main__":
    build_enclosure()
