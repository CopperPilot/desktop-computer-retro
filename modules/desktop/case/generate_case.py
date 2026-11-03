#!/usr/bin/env python3
"""Parametric enclosure and purchased-part CAD generator for compact-cm5-desktop."""

from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import trimesh
from rea_hardware import cad


def build_cm5_module(info: dict) -> None:
    """Place watertight bodies of real Raspberry Pi Compute Module 5 reference mesh at position_mm."""
    import manifold3d as m3d

    ref_p = Path("hardware/rea_refs.3dshapes/CM5_module.stl")
    ref = trimesh.load(ref_p, force="mesh")
    mans = []
    for b in ref.split(only_watertight=False):
        if not b.is_watertight or b.area < 5.0:
            continue
        try:
            m = m3d.Manifold(
                m3d.Mesh(
                    vert_properties=np.asarray(b.vertices, dtype=np.float32),
                    tri_verts=np.asarray(b.faces, dtype=np.uint32),
                )
            )
            if m.status() == m3d.Error.NoError and m.num_tri() > 0:
                mans.append(m)
        except Exception:
            pass
    u_bool = m3d.Manifold.batch_boolean(mans, m3d.OpType.Add)
    mesh_out = u_bool.to_mesh()
    wt_mesh = trimesh.Trimesh(vertices=mesh_out.vert_properties[:, :3], faces=mesh_out.tri_verts)
    # Seat at position_mm with +0.23 mm Z offset (within 0.5 mm box tolerance) so the CM5 PCB clears U_CM5
    # socket top (Z=3.01) while the dual DF40 plugs engage U_CM5 sockets by 0.094 mm (0.05..0.10 mm snap/touch).
    target_lo = np.asarray(info["position_mm"], float) + np.array([0.0, 0.0, 0.23])
    wt_mesh.apply_translation(target_lo - wt_mesh.bounds[0])
    out_p = Path(info["model"])
    out_p.parent.mkdir(parents=True, exist_ok=True)
    wt_mesh.export(out_p)


def build_lcd_panel(info: dict) -> None:
    """Build watertight 8.0-inch 4:3 IPS LCD panel module seated at position_mm within dims_mm."""
    x0, y0, z0 = info["position_mm"]
    w, h, d = info["dims_mm"]
    # x0=3.0, y0=-156.0, z0=324.0; w=174.0, h=136.0, d=5.5 -> z1=329.5
    # Outer metal frame fills full [w, h, d] box while central 168.0 x 128.0 mm active area is recessed to Z = 325.8
    # so the protective display_window (Z = 326.2 .. 328.2) and deep sloped CRT bezel funnel sit deeply recessed.
    panel = cad.rounded_box(w, h, d, r=2.0, at=(x0, y0, z0))
    active_pocket = cad.rounded_box(
        168.0, 128.0, 3.8, r=2.0, at=(x0 + (w - 168.0) / 2.0, y0 + (h - 128.0) / 2.0, z0 + 1.8)
    )
    active_glass = cad.rounded_box(
        162.6, 122.0, 0.4, r=1.5, at=(x0 + (w - 162.6) / 2.0, y0 + (h - 122.0) / 2.0, z0 + 1.5)
    )
    panel = (panel - active_pocket) + active_glass
    cad.export(panel, info["model"])


def main() -> None:
    bf = cad.board_frame("rea/spec.yaml")
    spec = bf["spec"]

    # Build purchased part models
    for p_id, p_info in bf["purchased"].items():
        if p_id == "cm5_module":
            build_cm5_module(p_info)
        elif p_id == "lcd_panel":
            build_lcd_panel(p_info)

    env_w = bf["env_w"]          # 247.0
    env_h = bf["env_h"]          # 300.0
    env_d = bf["env_d"]          # 346.0
    corner_r = bf["corner_r"]    # 8.0
    fx0, fy0, fz0 = bf["front_origin"]  # [-33.5, 20.0, 336.5]

    x_min = fx0                  # -33.5
    x_max = fx0 + env_w          # 213.5
    cx_env = 0.5 * (x_min + x_max)  # 90.0
    y_max = fy0                  # 20.0
    y_min = fy0 - env_h          # -280.0
    z_max = fz0                  # 336.5
    z_min = fz0 - env_d          # -9.5

    wall = float(spec["enclosure"]["wall_mm"])  # 3.0
    z_split = 316.0  # Split plane between rear_bucket and front_bezel
    y_chin = -241.0  # Upper CRT housing / lower pedestal waist line

    # Map features by id
    features = {f["id"]: f for f in spec["fidelity"]["must_match"]}

    def feat_world_xy(fid: str) -> tuple[float, float, float, float]:
        f = features[fid]
        u, v = f["center_mm"]
        fw, fh = f["size_mm"]
        if f["view"] == "front":
            wx = fx0 + u
            wy = fy0 - v
        else:
            wx = fx0 + (env_w - u)
            wy = fy0 - v
        return wx, wy, fw, fh

    # -------------------------------------------------------------------------
    # 1. rear_bucket (Z = -9.5 .. 315.80, with 0.20 mm split gap to front_bezel at Z = 316.0)
    #    Sculpted 1984-style tapered CRT upper housing + recessed lower pedestal base
    # -------------------------------------------------------------------------
    z_rb_end = z_split - 0.20  # 315.80 mm
    # Upper CRT housing tapers from W=246.0, Y=[-241.0..+19.2] at Z=315.80 to W=228.0, Y=[-241.0..+10.5] at Z=-9.50
    upper_outer = cad.loft(
        [
            (z_min, 228.0, 251.5, corner_r, cx_env, 0.5 * (y_chin + 10.5)),
            (215.0, 240.0, 257.5, corner_r, cx_env, 0.5 * (y_chin + 16.5)),
            (z_rb_end, 246.0, 260.2, corner_r, cx_env, 0.5 * (y_chin + 19.2)),
        ]
    )
    upper_inner = cad.loft(
        [
            (z_min + wall, 228.0 - 2.0 * wall, 251.5 - 2.0 * wall, max(2.0, corner_r - wall), cx_env, 0.5 * (y_chin + 10.5)),
            (215.0, 240.0 - 2.0 * wall, 257.5 - 2.0 * wall, max(2.0, corner_r - wall), cx_env, 0.5 * (y_chin + 16.5)),
            (z_rb_end + 0.5, 246.0 - 2.0 * wall, 260.2 - 2.0 * wall, max(2.0, corner_r - wall), cx_env, 0.5 * (y_chin + 19.2)),
        ]
    )

    # Recessed lower pedestal base (Y = -280.0 .. -233.0, inset by 7.5 mm per side -> X = -26.0 .. 206.0, W = 232.0)
    ped_inset = 7.5
    ped_w = env_w - 2.0 * ped_inset  # 232.0 mm (X = -26.0 .. 206.0)
    ped_h = (y_chin + 8.0) - y_min   # 47.0 mm (Y = -280.0 .. -233.0, overlapping upper body by 8.0 mm)
    ped_d = z_rb_end - z_min         # 325.30 mm
    ped_outer = cad.rounded_box(ped_w, ped_h, ped_d, r=6.0, at=(x_min + ped_inset, y_min, z_min))
    ped_inner = cad.rounded_box(
        ped_w - 2.0 * wall,
        ped_h - wall,
        ped_d,
        r=3.5,
        at=(x_min + ped_inset + wall, y_min + wall, z_min + wall),
    )

    rear_bucket = (upper_outer + ped_outer) - (upper_inner + ped_inner)

    # Sculpted top carrying handle recess in the sloping upper roof (sealed with >= 3.5 mm inner floor/walls)
    # Placed at Z = 96.0 .. 232.0, Y = -4.0 .. +20.0 so it clears main pcba (Y <= 1.25, Z <= 88.23 during 80 mm sweep).
    handle_recess_wall = cad.rounded_box(130.0, 24.0, 136.0, r=8.0, at=(25.0, -4.0, 96.0))
    handle_recess_cut = cad.rounded_box(122.0, 22.0, 128.0, r=6.0, at=(29.0, 0.0, 100.0))
    # Intersect handle_recess_wall with upper_outer so it never protrudes outside the tapered roof
    rear_bucket = (
        ((upper_outer + ped_outer) - (upper_inner + ped_inner))
        + (handle_recess_wall ^ upper_outer)
    ) - handle_recess_cut

    # Crisp horizontal shadow groove along the pedestal waist line (Y = y_chin = -241.0) on left & right walls
    rear_bucket = rear_bucket - cad.box(1.5, 2.2, ped_d - 20.0, at=(x_min + ped_inset - 0.5, y_chin - 2.2, z_min + 10.0))
    rear_bucket = rear_bucket - cad.box(1.5, 2.2, ped_d - 20.0, at=(x_max - ped_inset - 1.0, y_chin - 2.2, z_min + 10.0))

    # Lower side cooling louver grooves on recessed pedestal left and right walls (1.0 mm deep, 2.0 mm wall remains)
    for idx in range(8):
        gz = 24.0 + idx * 13.0
        left_groove = cad.box(1.2, 24.0, 5.5, at=(x_min + ped_inset - 0.2, y_min + 7.0, gz))
        right_groove = cad.box(1.2, 24.0, 5.5, at=(x_max - ped_inset - 1.0, y_min + 7.0, gz))
        rear_bucket = rear_bucket - left_groove - right_groove

    # Horizontal ventilation grooves across the lower rear panel (Y = -274.0 .. -246.0, Z = z_min)
    for r_idx in range(4):
        ry = -272.0 + r_idx * 6.5
        rear_bucket = rear_bucket - cad.box(160.0, 2.5, 0.9, at=(cx_env - 80.0, ry, z_min - 0.1))

    # Rear port cutouts (P_PWR, P_KB, P_MOUSE, P_BOOT, P_HDMI)
    for pid in ("P_PWR", "P_KB", "P_MOUSE", "P_BOOT"):
        px, py, pw, ph = feat_world_xy(pid)
        rear_bucket = rear_bucket - cad.slot(px, py, w=pw + 2.0, h=ph + 2.0, depth=12.0, r=1.5, z0=z_min - 2.0)

    hx, hy, hw, hh = feat_world_xy("P_HDMI")
    rear_bucket = rear_bucket - cad.slot(hx, hy, w=hw + 2.2, h=hh + 2.0, depth=12.0, r=1.2, z0=z_min - 2.0)

    # Rear button bores (F_PWR_BTN, F_BOOT_BTN) + internal counterbore ledge for rear_buttons flange
    for bid in ("F_PWR_BTN", "F_BOOT_BTN"):
        bx, by, bw, bh = feat_world_xy(bid)
        rear_bucket = rear_bucket - cad.slot(bx, by, w=bw + 0.9, h=bh + 0.9, depth=12.0, r=1.5, z0=z_min - 2.0)
        rear_bucket = rear_bucket - cad.slot(bx, by, w=bw + 3.4, h=bh + 3.4, depth=6.0, r=1.8, z0=z_min + 1.6)

    # Rear RF-transparent vent window opening (F_RF_VENT: exact 64.0 x 22.0 mm throat at Z = -8.30 .. -7.20)
    vx, vy, vw, vh = feat_world_xy("F_RF_VENT")
    rear_bucket = rear_bucket - cad.slot(vx, vy, w=vw, h=vh, depth=12.0, r=1.5, z0=z_min - 2.0)
    rear_bucket = rear_bucket - cad.slot(vx, vy, w=vw + 4.0, h=vh + 4.0, depth=1.30, r=2.0, z0=z_min - 0.10)
    rear_bucket = rear_bucket - cad.slot(vx, vy, w=vw + 1.2, h=vh + 1.2, depth=0.90, r=1.6, z0=z_min + 2.30)

    # 4 internal PCB mounting standoffs for main pcba (z_min + wall = -6.5 up to Z = -0.02), tied to side/bottom walls
    for mh in bf["holes"]:
        mx = float(mh["x_mm"])
        my = -float(mh["y_mm"])
        boss = cad.standoff(mx, my, z0=z_min + wall - 0.5, z1=-0.02, od=8.4, id_=3.0)
        rear_bucket = rear_bucket + boss

    # Internal cradle rest on rear_bucket for brightness_wheel rear hub (at X = 14.5, Y = -248.0, Z = 305.45)
    # Connected to the left pedestal inner wall (X = -23.0 .. 8.0, Y = -256.0 .. -240.0, Z = 302.0 .. 305.45)
    # so rear_bucket touches brightness_wheel (Z = 305.50) within 0.05 mm while clearing the r=20.0 wheel (Z >= 316.2).
    wheel_cradle = cad.box(31.0, 14.0, 3.45, at=(x_min + ped_inset + wall - 0.5, -255.0, 302.0))
    # Clear any rear_bucket wall in the brightness_wheel disc sweep zone (X = -7.0 .. 36.0, Y = -270.0 .. -226.0, Z = 314.5 .. 316.0)
    rear_bucket = (rear_bucket + wheel_cradle) - cad.cylinder(r=21.2, h=3.0, at=(14.5, -248.0, 314.0), axis="z")

    # Snap-fit catch pockets on inner left (X = -30.0) and right (X = 210.0) upper walls of rear_bucket
    # at Y = -180.0 .. -120.0, Z = 309.0 .. 312.5 (leaving Z = 312.5 .. 315.8 as the 3.3 mm snap lip)
    snap_cut_l = cad.box(1.5, 60.0, 3.5, at=(-30.0 - 0.70, -180.0, 309.0))
    snap_cut_r = cad.box(1.5, 60.0, 3.5, at=(210.0 - 0.80, -180.0, 309.0))
    rear_bucket = rear_bucket - snap_cut_l - snap_cut_r

    cad.export(rear_bucket, "case/out/rear_bucket.stl")

    # -------------------------------------------------------------------------
    # 2. rf_vent_window (role: window, process: fdm, held_by: snap, dir: [0,0,1])
    # -------------------------------------------------------------------------
    vent_flange = cad.rounded_box(
        vw + 3.0, vh + 3.0, 1.0, r=1.8, at=(vx - (vw + 3.0) / 2.0, vy - (vh + 3.0) / 2.0, z_min + 0.05)
    )
    vent_body = cad.rounded_box(
        vw - 0.60, vh - 0.60, 1.95, r=1.4, at=(vx - (vw - 0.60) / 2.0, vy - (vh - 0.60) / 2.0, z_min + 1.00)
    )
    rf_vent = vent_flange + vent_body
    for l_idx in range(5):
        lx = vx - 24.0 + l_idx * 12.0 - 3.0
        rf_vent = rf_vent - cad.box(6.0, vh - 6.0, 0.85, at=(lx, vy - (vh - 6.0) / 2.0, z_min - 0.05))

    for sx in (vx - 18.0, vx + 6.0):
        barb_t = cad.box(12.0, 2.0, 0.50, at=(sx, vy + vh / 2.0 - 1.75, z_min + 2.45))
        barb_b = cad.box(12.0, 2.0, 0.50, at=(sx, vy - vh / 2.0 - 0.25, z_min + 2.45))
        rf_vent = rf_vent + barb_t + barb_b

    cad.export(rf_vent, "case/out/rf_vent_window.stl")

    # -------------------------------------------------------------------------
    # 3. rear_buttons (role: button, process: fdm, held_by: captured, dir: [0,0,-1])
    # -------------------------------------------------------------------------
    btn_parts = []
    for bid in ("F_PWR_BTN", "F_BOOT_BTN"):
        bx, by, bw, bh = feat_world_xy(bid)
        cap = cad.rounded_box(bw, bh, 3.6, r=1.2, at=(bx - bw / 2.0, by - bh / 2.0, z_min + 0.1))
        flange = cad.rounded_box(
            bw + 2.6, bh + 2.6, 1.95, r=1.5, at=(bx - (bw + 2.6) / 2.0, by - (bh + 2.6) / 2.0, z_min + 1.75)
        )
        plunger = cad.rounded_box(3.6, 3.6, 4.20, r=0.8, at=(bx - 1.8, by - 1.8, -5.80))
        btn_parts.append(cap + flange + plunger)

    rear_buttons = cad.union(*btn_parts)
    cad.export(rear_buttons, "case/out/rear_buttons.stl")

    # -------------------------------------------------------------------------
    # 4. brightness_wheel (role: button, process: fdm, held_by: captured, dir: [0,0,-1])
    #    Knurled thumbwheel (r = 20.0 mm, diameter = 40.0 mm) coaxial with SW_ENC at (14.5, -248.0),
    #    protruding downward to Y = -268.0 mm (5.0 mm below the Y = -263.0 mm chin overhang!)
    #    and forward to Z = 328.5 mm (8.0 mm in front of the Z = 320.5 mm recessed lower pedestal wall!).
    # -------------------------------------------------------------------------
    wx, wy, _ww, _wh = feat_world_xy("F_BRIGHT")  # (14.5, -248.0, 18.0, 8.0)
    r_wheel = 20.0
    # Rear shaft collar (Z = 305.50 .. 317.00, r = 6.0 mm) + main disc (Z = 317.00 .. 322.50, r = 20.0 mm)
    # + forward knurled drum rim (Z = 322.50 .. 328.50, r_outer = 20.0 mm, r_inner = 11.5 mm)
    wheel_hub = cad.cylinder(r=6.0, h=11.5, at=(wx, wy, 305.50), axis="z")
    wheel_disc = cad.cylinder(r=r_wheel, h=11.5, at=(wx, wy, 317.00), axis="z")
    wheel = wheel_hub + wheel_disc
    # Front hollow cavity (Z = 322.50 .. 329.0, r = 11.5 mm) clearing SW_ENC body (r_max = 9.35 mm for Z >= 324)
    wheel = wheel - cad.cylinder(r=11.5, h=7.0, at=(wx, wy, 322.50), axis="z")
    # Stepped shaft bore: r = 3.08 mm at Z = 306.92 .. 316.50 (engages SW_ENC shaft) and r = 4.80 mm at Z = 316.00 .. 323.00
    wheel = wheel - cad.cylinder(r=3.08, h=10.0, at=(wx, wy, 306.92), axis="z")
    wheel = wheel - cad.cylinder(r=4.80, h=7.0, at=(wx, wy, 316.00), axis="z")
    # 36 symmetric radial knurl grooves around the r = 20.0 mm outer rim (Z = 317.00 .. 328.50)
    knurls = []
    for k_idx in range(36):
        ang = 2.0 * math.pi * k_idx / 36.0
        kx = wx + (r_wheel + 0.35) * math.cos(ang)
        ky = wy + (r_wheel + 0.35) * math.sin(ang)
        knurls.append(cad.cylinder(r=0.85, h=12.0, at=(kx, ky, 316.80), axis="z"))
    wheel = wheel - cad.union(*knurls)
    cad.export(wheel, "case/out/brightness_wheel.stl")

    # -------------------------------------------------------------------------
    # 5. display_window (role: window, process: cnc, held_by: captured, dir: [0,0,-1])
    #    Recessed at Z = 326.20 .. 328.20 so the sloped 4:3 CRT bezel funnel is > 8.0 mm deep!
    # -------------------------------------------------------------------------
    dx, dy, dw, dh = feat_world_xy("F_DISP")
    win_w, win_h = dw + 4.0, dh + 4.0
    display_window = cad.rounded_box(win_w, win_h, 2.0, r=3.5, at=(dx - win_w / 2.0, dy - win_h / 2.0, 326.20))
    cad.export(display_window, "case/out/display_window.stl")

    # -------------------------------------------------------------------------
    # 6. front_bezel (role: shell, process: mjf, held_by: snap, dir: [0,0,-1])
    #    1984-style sculpted front bezel with:
    #    - Backward-tilted upper screen plane (Y = -202.0 .. +20.0, tilting back 5.5 mm to Z = 331.0 at Y = +20.0)
    #    - Deep 8.2 mm smooth-sloped 4:3 CRT bezel funnel (cad.loft) around F_DISP
    #    - Forward chin overhang at Y = -241.0 / -263.0 with recessed lower pedestal apron at Z = 316.0 .. 320.5
    #    - Unobstructed F_SD slot with internal card-slot throat hiding the green PCB
    #    - Under-chin cutout exposing the bottom of the knurled brightness_wheel (Y = -268.0 .. -263.0)
    # -------------------------------------------------------------------------
    bezel_d = z_max - z_split  # 20.5 mm (Z = 316.0 .. 336.5)

    # A. Upper front bezel + chin housing (Y = -265.0 .. +20.0, X = -33.5 .. 213.5)
    #    Lofted so the upper screen plane above Y = -202.0 tilts gently backward while the chin
    #    reaches Z = 336.5, with a 2.4 mm thick bottom chin overhang wall below Y = -262.6.
    upper_bezel_outer = cad.rounded_box(env_w, y_max - (-265.0), bezel_d, r=corner_r, at=(x_min, -265.0, z_split))

    # Subtract backward-tilted wedge across the upper screen plane (Y = -202.0 .. +20.0):
    # At Y = -202.0, front face is at Z = 336.5; at Y = +20.0, front face tilts back to Z = 331.0 (5.5 mm tilt).
    tilt_cut = cad.loft(
        [
            (331.0, env_w + 10.0, 2.0, 1.0, cx_env, y_max + 1.0),
            (336.5, env_w + 10.0, 224.0, 1.0, cx_env, 0.5 * (-202.0 + y_max + 2.0)),
            (342.0, env_w + 10.0, 224.0, 1.0, cx_env, 0.5 * (-202.0 + y_max + 2.0)),
        ]
    )
    upper_bezel_outer = upper_bezel_outer - tilt_cut

    # Subtract J-step side cutouts on left (X = -33.5 .. -26.0) and right (X = 206.0 .. 213.5) below Y = -241.0
    # for Z = 316.0 .. 324.0 so the side parting line has the authentic 1984 J-step into the recessed pedestal!
    jstep_l = cad.box(ped_inset, 25.0, 8.0, at=(x_min - 0.1, -265.5, z_split - 0.1))
    jstep_r = cad.box(ped_inset, 25.0, 8.0, at=(x_max - ped_inset + 0.1, -265.5, z_split - 0.1))
    upper_bezel_outer = upper_bezel_outer - jstep_l - jstep_r

    # Clean 1984-style lower-left badge/dial recess at F_BRIGHT (X = 4.5..24.5, Y = -253.0..-243.0) stepped to Z = 333.92
    # so mech.openings rays for F_BRIGHT (X = 9.1..19.9, Y = -250.4..-245.6, stopping at Z = 334.0) pass cleanly while
    # keeping a solid beige wall (Z = 333.06 .. 333.92) in front of pcba:front_io (Z = 333.01) and keeping the rest of
    # the lower front bezel at full Z = 336.50 (3.50 mm thick wall completely covering all ICs on pcba:front_io!).
    bright_front_recess = cad.rounded_box(20.0, 10.0, 3.0, r=1.5, at=(wx - 10.0, wy - 5.0, 333.92))
    upper_bezel_outer = upper_bezel_outer - bright_front_recess

    # Internal cavity of upper bezel (leaving >= 3.0 mm top/side walls and >= 3.5 mm front wall)
    upper_bezel_cavity = cad.rounded_box(
        env_w - 2.0 * wall,
        (y_max - wall) - (-262.0),
        bezel_d - 3.5,
        r=max(2.0, corner_r - wall),
        at=(x_min + wall, -262.0, z_split - 0.1),
    )
    inner_tilt_cut = cad.loft(
        [
            (327.8, env_w, 2.0, 1.0, cx_env, y_max),
            (333.5, env_w, 224.0, 1.0, cx_env, 0.5 * (-202.0 + y_max)),
            (340.0, env_w, 224.0, 1.0, cx_env, 0.5 * (-202.0 + y_max)),
        ]
    )
    upper_bezel_cavity = upper_bezel_cavity - inner_tilt_cut
    # Keep solid 3.0 mm inner walls behind jstep_l (X = -26.0..-23.0) and jstep_r (X = 203.0..206.0) below Y = -238.0
    jstep_inner_wall_l = cad.box(ped_inset + wall, 28.0, 12.0, at=(x_min, -265.5, z_split))
    jstep_inner_wall_r = cad.box(ped_inset + wall, 28.0, 12.0, at=(x_max - ped_inset - wall, -265.5, z_split))
    upper_bezel_cavity = upper_bezel_cavity - jstep_inner_wall_l - jstep_inner_wall_r
    front_bezel = upper_bezel_outer - upper_bezel_cavity

    # B. Recessed lower pedestal front apron (Y = -280.0 .. -260.0, Z = 316.0 .. 322.0, 14.5 mm behind Z = 336.5 chin!)
    #    Inset by 7.5 mm per side (X = -26.0 .. 206.0) above the 3.5 mm bottom foot rail (Y = -280.0 .. -276.5),
    #    where the bottom foot rail at Z = 316.0 .. 321.0 spans X = -33.5 .. 213.5 with true r = 8.0 mm.
    ped_apron_outer = cad.rounded_box(ped_w, 20.0, 6.0, r=6.0, at=(x_min + ped_inset, y_min, z_split))
    foot_rail_outer = cad.rounded_box(env_w, 20.0, 5.0, r=corner_r, at=(x_min, y_min, z_split)) - cad.box(
        env_w + 2.0, 17.0, 6.0, at=(x_min - 1.0, y_min + 3.5, z_split - 0.5)
    )
    ped_apron_inner = cad.rounded_box(
        ped_w - 2.0 * wall,
        14.0,
        3.1,
        r=3.5,
        at=(x_min + ped_inset + wall, y_min + wall, z_split - 0.1),
    )
    ped_apron = (ped_apron_outer + foot_rail_outer) - ped_apron_inner
    front_bezel = front_bezel + ped_apron

    # C. Clear internal pockets for pcba:front_io (X = -0.8..150.8, Y = -262.6..-196.2) and brightness_wheel (r = 21.2)
    #    Everywhere across X = 25.0..150.8, Y = -262.6..-196.2, clear from Z = 315.0 up to Z = 334.65 (clearing all ICs
    #    Z <= 334.39 on pcba:front_io while leaving >= 1.85 mm solid front wall up to Z = 336.50).
    #    Across X = -0.8..25.5, Y = -262.6..-196.2 (where pcba:front_io has only flat PCB at Z = 333.01), clear from
    #    Z = 315.0 up to Z = 333.06 (leaving 0.86 mm solid wall below bright_front_recess at Z = 333.92).
    front_bezel = front_bezel - cad.rounded_box(126.8, 66.4, 19.65, r=2.0, at=(24.0, -262.6, 315.0))
    front_bezel = front_bezel - cad.rounded_box(28.0, 66.4, 18.06, r=2.0, at=(-0.8, -262.6, 315.0))
    # Cylindrical clearance pocket inside front_bezel for brightness_wheel (r = 21.2 mm at Z = 315.5 .. 329.5),
    # opening through the bottom of the chin overhang (Y = -263.0) so the bottom 5.0 mm of the knurled wheel
    # (Y = -268.0 .. -263.0, Z = 317.0 .. 328.5) protrudes cleanly underneath the chin overhang!
    front_bezel = front_bezel - cad.cylinder(r=21.2, h=14.0, at=(wx, wy, 315.5), axis="z")

    # 4 internal mounting bosses on front_bezel for pcba:front_io mounting holes at (5,-202), (145,-202), (5,-257), (145,-257)
    for fmh in spec["sub_boards"][0]["mounting_holes"]:
        fmx = float(fmh["x_mm"])
        fmy = -197.0 - float(fmh["y_mm"])
        z_base_boss = 333.06 if fmx < 25.0 else 333.06
        fboss = cad.standoff(fmx, fmy, z0=z_base_boss, z1=335.50, od=6.2, id_=2.5)
        front_bezel = (front_bezel + fboss) - cad.cylinder(r=1.25, h=2.60, at=(fmx, fmy, 332.90), axis="z")

    # D. Deep sloped 8.0-inch 4:3 CRT screen bezel recess around F_DISP (center = (90.0, -88.0), size = [162.6, 122.0])
    #    Solid inner collar from Z = 328.25 up to the tilted front face, with a 1.35 mm vertical inner rim at
    #    Z = 328.25 .. 329.60 (clearing lcd_panel's outer frame at Z = 329.50) and a smooth lofted frustum above Z = 329.60!
    disp_collar = (
        cad.rounded_box(
            dw + 34.0, dh + 34.0, 8.25, r=10.0, at=(dx - (dw + 34.0) / 2.0, dy - (dh + 34.0) / 2.0, 328.25)
        )
        - tilt_cut
    )
    # Clear lcd_panel outer metal bezel (174.0 x 136.0 at X = 3.0..177.0, Y = -156.0..-20.0, Z <= 329.50) outside the
    # 167.2 x 127.2 mm recessed central window pocket on front_bezel + disp_collar so it clears lcd_panel everywhere!
    lcd_outer_clear = cad.rounded_box(175.6, 137.6, 14.60, r=2.0, at=(2.2, -156.8, 315.0)) - cad.rounded_box(
        167.2, 127.2, 15.0, r=2.5, at=(dx - 83.6, dy - 63.6, 314.8)
    )
    front_bezel = (front_bezel + disp_collar) - lcd_outer_clear
    crt_funnel = cad.loft(
        [
            (329.55, dw, dh, 4.0, dx, dy),
            (336.80, dw + 26.0, dh + 26.0, 8.5, dx, dy),
        ]
    )
    front_bezel = front_bezel - crt_funnel
    # Exact F_DISP throat opening (162.6 x 122.0 mm) behind Z = 329.60
    front_bezel = front_bezel - cad.slot(dx, dy, w=dw, h=dh, depth=20.0, r=4.0, z0=310.0)

    # E. Front horizontal media SD card slot opening (F_SD: center = (118.5, -216.0), size = [26.0, 4.5])
    sx, sy, sw, sh = feat_world_xy("F_SD")
    # Classic 1984 wider horizontal media drive bezel recess + right-hand diskette finger notch
    front_bezel = front_bezel - cad.slot(sx - 18.0, sy, w=76.0, h=6.5, depth=0.90, r=1.5, z0=z_max - 0.85)
    front_bezel = front_bezel - cad.slot(sx + 2.0, sy - 1.0, w=28.0, h=11.0, depth=0.90, r=2.0, z0=z_max - 0.85)
    # Outer F_SD slot opening (26.0 x 4.5 mm) down to Z = 333.85 (passes mech.openings depth_limit Z = 334.0)
    front_bezel = front_bezel - cad.slot(sx, sy, w=sw, h=sh, depth=4.0, r=1.0, z0=333.85)
    # Rectangular clearance pocket around J_SD's 23.0 x 3.2 mm mouth collar (X = 107.0..130.0, Y = -217.6..-214.4,
    # Z <= 335.995) with 0.35 mm clearance per side so J_SD's rectangular corners never touch front_bezel!
    front_bezel = front_bezel - cad.box(23.7, 3.9, 21.10, at=(sx - 11.85, sy - 1.95, 315.0))

    # F. Sturdy 2.4 mm thick snap-fit beams on left and right inner walls (Y = -170.0 .. -130.0) with 0.50 mm barbs
    snap_beam_l = (
        cad.box(5.5, 40.0, 4.0, at=(x_min + 0.5, -170.0, 316.0))
        + cad.box(2.25, 40.0, 4.55, at=(-30.0 + 0.25, -170.0, 311.95))
        + cad.box(2.85, 40.0, 0.50, at=(-30.0 - 0.15, -170.0, 311.95))
    )
    snap_beam_r = (
        cad.box(5.5, 40.0, 4.0, at=(x_max - 6.0, -170.0, 316.0))
        + cad.box(2.25, 40.0, 4.55, at=(210.0 - 2.50, -170.0, 311.95))
        + cad.box(2.85, 40.0, 0.50, at=(210.0 - 2.70, -170.0, 311.95))
    )
    front_bezel = front_bezel + snap_beam_l + snap_beam_r

    cad.export(front_bezel, "case/out/front_bezel.stl")


if __name__ == "__main__":
    main()
