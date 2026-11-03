#!/usr/bin/env python3
"""Parametric enclosure generator for the compact 58-key mechanical desktop keyboard."""

from __future__ import annotations

import math
import re
from pathlib import Path

from rea_hardware import cad


def _parse_key_legend(notes: str, name: str) -> str:
    """Extract the keycap legend string from the spec feature notes or name."""
    m = re.search(r"keycap\([0-9.]+,\s*'((?:\\'|[^'])*)'\)", notes or "")
    if m:
        return m.group(1).replace("\\'", "'").replace("\\\\", "\\")
    m2 = re.search(r"\((.+?)\)\s*\([0-9.]+u\)", name or "")
    return m2.group(1) if m2 else ""


def _xz_corner_chamfer(xmin: float, xmax: float, ymin: float, ymax: float, z_corner: float, c: float, top: bool, right: bool) -> cad.Manifold:
    """Build a 45-degree longitudinal chamfer cutter along Y at an (X, Z) corner."""
    eps = 2.0
    t = 0.01
    x_edge = xmax if right else xmin
    dx = -1.0 if right else 1.0
    dz = -1.0 if top else 1.0
    ly = (ymax - ymin) + 4.0
    y0 = ymin - 2.0
    pts = [
        (x_edge + dx * c, z_corner),
        (x_edge, z_corner + dz * c),
        (x_edge + dx * c, z_corner - dz * eps),
        (x_edge - dx * eps, z_corner + dz * c),
        (x_edge - dx * eps, z_corner - dz * eps),
    ]
    boxes = [cad.box(t, ly, t, at=(px - t / 2.0, y0, pz - t / 2.0)) for px, pz in pts]
    return cad.hull(*boxes)


def build_enclosure(spec_path: str | Path = "rea/spec.yaml") -> None:
    bf = cad.board_frame(spec_path)
    spec = bf["spec"]

    env_w = float(bf["env_w"])          # 338.0
    env_h = float(bf["env_h"])          # 148.0
    env_d = float(bf["env_d"])          # 48.0
    corner_r = float(bf["corner_r"])    # 5.0
    board_w = float(bf["board_w"])      # 310.0
    board_h = float(bf["board_h"])      # 132.0
    board_t = float(bf["board_t"])      # 1.6
    x0, y0, z0 = [float(v) for v in bf["front_origin"]]  # [-14.0, 2.0, 34.0]

    xmin, xmax = x0, x0 + env_w         # -14.0 .. 324.0
    ymin, ymax = y0 - env_h, y0         # -146.0 .. 2.0
    zmin, zmax = z0 - env_d, z0         # -14.0 .. 34.0
    wall = max(float(spec["enclosure"].get("wall_mm", 2.5)), 3.0)

    features = {f["id"]: f for f in spec["fidelity"]["must_match"]}
    usb_feat = features["P_KB_DEV"]
    bootsel_feat = features["F_BOOTSEL"]

    usb_cx = xmin + float(usb_feat["center_mm"][0])
    usb_cz = zmax - float(usb_feat["center_mm"][1])
    usb_w, usb_h = [float(v) for v in usb_feat["size_mm"]]

    bs_cx = xmin + float(bootsel_feat["center_mm"][0])
    bs_cy = ymax - float(bootsel_feat["center_mm"][1])
    bs_w, bs_h = [float(v) for v in bootsel_feat["size_mm"]]

    z_split = -2.0
    z_bot_top = z_split - 0.04  # -2.04 mm (0.04 mm split-line gap avoids coplanar mesh overlap)
    z_floor_top = zmin + 3.2    # -10.8 mm (3.2 mm floor)

    # -------------------------------------------------------------------------
    # 1. bottom_shell: lower pan (Z = -14.0 .. -2.04 mm) + PCB standoffs to Z=0
    # -------------------------------------------------------------------------
    bottom_outer = cad.rounded_box(
        env_w, env_h, z_bot_top - zmin, r=corner_r, at=(xmin, ymin, zmin)
    )
    bottom_cavity = cad.rounded_box(
        env_w - 2 * wall,
        env_h - 2 * wall,
        (z_bot_top - z_floor_top) + 2.0,
        r=max(1.5, corner_r - wall),
        at=(xmin + wall, ymin + wall, z_floor_top),
    )
    bottom_shell = bottom_outer - bottom_cavity

    # Upward snap-fit fingers on left and right inner walls of bottom_shell (at Y = -80..-64 mm)
    # Extending up to Z = +2.5 mm inside top_shell, with a 0.35 mm tall x 0.25 mm outward barb
    # at Z = +2.10..+2.45 mm that sits inside top_shell's internal snap pocket when seated and
    # engages top_shell's Z = -2.0..+1.8 mm lower wall lip by ~0.35 mm when pulled apart.
    snap_arm_l = cad.box(2.2, 16.0, 2.5 - z_floor_top, at=(xmin + wall + 0.25, -80.0, z_floor_top))
    snap_barb_l = cad.box(0.5, 16.0, 0.35, at=(xmin + wall - 0.25, -80.0, 2.10))
    snap_arm_r = cad.box(2.2, 16.0, 2.5 - z_floor_top, at=(xmax - wall - 2.45, -80.0, z_floor_top))
    snap_barb_r = cad.box(0.5, 16.0, 0.35, at=(xmax - wall - 0.25, -80.0, 2.10))
    bottom_shell = cad.union(bottom_shell, snap_arm_l, snap_barb_l, snap_arm_r, snap_barb_r)

    # 6 PCB mounting standoffs supporting PCBA at Z = 0.0 mm with 1.8 mm screw pilot holes
    standoffs = []
    for h in bf["holes"]:
        hx = float(h["x_mm"])
        hy = -float(h["y_mm"])
        standoffs.append(cad.standoff(hx, hy, z_floor_top, 0.0, od=5.6, id_=1.8))
    bottom_shell = cad.union(bottom_shell, *standoffs)

    # Internal guide housing for captive BOOTSEL button at (bs_cx, bs_cy)
    bs_boss = cad.slot(
        bs_cx, bs_cy, w=bs_w + 5.6, h=bs_h + 5.6, depth=9.0, r=2.0, z0=zmin
    )
    bottom_shell = bottom_shell + bs_boss

    bs_through = cad.slot(
        bs_cx, bs_cy, w=bs_w, h=bs_h, depth=4.0, r=0.8, z0=zmin - 1.0
    )
    bs_counterbore = cad.slot(
        bs_cx, bs_cy, w=bs_w + 2.2, h=bs_h + 2.2, depth=12.0, r=1.0, z0=zmin + 2.5
    )
    bottom_shell = bottom_shell - bs_through - bs_counterbore

    # -------------------------------------------------------------------------
    # 2. bootsel_button: flanged captive actuator at (bs_cx, bs_cy)
    # -------------------------------------------------------------------------
    z_step = zmin + 2.5  # -11.5 mm
    btn_lower = cad.slot(
        bs_cx, bs_cy, w=bs_w - 0.8, h=bs_h - 0.8, depth=2.2, r=0.6, z0=z_step - 2.2
    )
    btn_flange = cad.slot(
        bs_cx, bs_cy, w=bs_w + 1.4, h=bs_h + 1.4, depth=2.0, r=0.8, z0=z_step
    )
    btn_stem = cad.slot(
        bs_cx, bs_cy, w=3.6, h=3.6, depth=(-1.52) - (z_step + 2.0), r=0.6, z0=z_step + 2.0
    )
    bootsel_button = cad.union(btn_lower, btn_flange, btn_stem)

    # -------------------------------------------------------------------------
    # 3. top_shell: stepped beige upper bezel (Z = -2.0 .. 25.5 mm)
    # -------------------------------------------------------------------------
    # Sloped wedge profile rising smoothly from Z = 14.5 mm at front (Y=-146)
    # to Z = 25.5 mm at rear (Y=+2.0) with a broad 2.5 mm perimeter bevel, so the
    # stepped keycaps (Z = 24.8 .. 34.0 mm) protrude proudly above the bezel.
    h_front_top = 14.5 - z_split   # 16.5 mm above z_split (Z = 14.5 mm at front)
    h_back_top = 25.5 - z_split    # 27.5 mm above z_split (Z = 25.5 mm at rear)
    top_outer = cad.wedge(
        env_w, env_h, h_front=h_front_top, h_back=h_back_top, r=corner_r, at=(xmin, ymin, z_split), bevel=2.5
    )

    # Hollow interior using a matching sloped inner wedge (everywhere >= 3.2 mm below outer roof)
    roof_t = 3.2
    inner_w = env_w - 2 * wall
    inner_h = env_h - 2 * wall
    inner_wedge = cad.wedge(
        inner_w,
        inner_h,
        h_front=h_front_top - roof_t + 1.0,
        h_back=h_back_top - roof_t + 1.0,
        r=max(1.5, corner_r - wall),
        at=(xmin + wall, ymin + wall, z_split - 1.0),
        bevel=0.0,
    )
    # Shallow pocket in rear wall from z_split (-2.0 mm) up to Z = 2.2 mm so PCB rear edge (Y=0.0, Z=0..1.6)
    # has 0.4 mm clearance both when seated and during the entire downward installation sweep
    pcb_rear_relief = cad.box(
        board_w + 1.0, 2.4, 2.2 - (z_split - 1.0), at=(-0.5, -2.0, z_split - 1.0)
    )

    # Solid key-well surround collar (3.6 mm wall thickness around the stepped key-well opening)
    well_r14_cx, well_r14_cy, well_r14_w, well_r14_h = 155.0, -62.475, 287.4, 77.8
    well_r5_cx, well_r5_cy, well_r5_w, well_r5_h = 147.856, -110.1, 225.4, 21.6
    collar_w = 3.6
    collar_outer = cad.union(
        cad.slot(well_r14_cx, well_r14_cy, w=well_r14_w + 2 * collar_w, h=well_r14_h + 2 * collar_w, depth=30.0, r=3.5, z0=9.5),
        cad.slot(well_r5_cx, well_r5_cy, w=well_r5_w + 2 * collar_w, h=well_r5_h + 2 * collar_w, depth=30.0, r=3.5, z0=9.5),
    )

    inner_cavity = (cad.union(inner_wedge, pcb_rear_relief) - collar_outer)
    top_shell = top_outer - inner_cavity

    # Longitudinal lower-edge chamfers at (xmin, z_split) and (xmax, z_split)
    c_bot = 1.52
    top_shell = (
        top_shell
        - _xz_corner_chamfer(xmin, xmax, ymin, ymax, z_split, c_bot, top=False, right=False)
        - _xz_corner_chamfer(xmin, xmax, ymin, ymax, z_split, c_bot, top=False, right=True)
    )

    # Snap undercut pockets in left and right inner walls of top_shell (at Y = -83..-61 mm, Z = +1.8..+3.2 mm)
    snap_pocket_l = cad.box(0.6, 22.0, 1.4, at=(xmin + wall - 0.6, -83.0, 1.8))
    snap_pocket_r = cad.box(0.6, 22.0, 1.4, at=(xmax - wall, -83.0, 1.8))
    top_shell = top_shell - snap_pocket_l - snap_pocket_r

    # Cut stepped key-well opening all the way through
    well_cut = cad.union(
        cad.slot(well_r14_cx, well_r14_cy, w=well_r14_w, h=well_r14_h, depth=50.0, r=2.0, z0=5.0),
        cad.slot(well_r5_cx, well_r5_cy, w=well_r5_w, h=well_r5_h, depth=50.0, r=2.0, z0=5.0),
    )
    top_shell = top_shell - well_cut

    # 4 corner PCB hold-down bosses merged into top_shell roof down to Z = 1.65 mm
    clamp_posts = [
        cad.standoff(6.0, -6.0, 1.65, 23.0, od=4.6, id_=0.0),
        cad.standoff(304.0, -6.0, 1.65, 23.0, od=4.6, id_=0.0),
        cad.standoff(6.0, -126.0, 1.65, 14.0, od=4.6, id_=0.0),
        cad.standoff(304.0, -126.0, 1.65, 14.0, od=4.6, id_=0.0),
    ]
    top_shell = cad.union(top_shell, *clamp_posts)

    # Rear USB-C port opening (P_KB_DEV): open down to z_split on top_shell so top_shell drops over J1
    usb_top_z1 = usb_cz + usb_h / 2.0
    usb_cut_top_h = usb_top_z1 - (z_split - 1.0)
    usb_cut_top_cz = 0.5 * (usb_top_z1 + (z_split - 1.0))
    usb_cut_top = cad.edge_cut(
        axis="y",
        center=usb_cx,
        z=usb_cut_top_cz,
        w=usb_w,
        h=usb_cut_top_h,
        side="max",
        envelope=(xmin, ymin, xmax, ymax),
        r=1.0,
        reach=12.0,
    )
    usb_cut_bot = cad.edge_cut(
        axis="y",
        center=usb_cx,
        z=usb_cz,
        w=usb_w,
        h=usb_h,
        side="max",
        envelope=(xmin, ymin, xmax, ymax),
        r=1.0,
        reach=12.0,
    )
    top_shell = top_shell - usb_cut_top
    bottom_shell = bottom_shell - usb_cut_bot

    # -------------------------------------------------------------------------
    # 4. keycaps & keycaps_legends: 58 sculpted keycaps + contrasting legends
    # -------------------------------------------------------------------------
    unit_pitch = 19.05
    cap_z0 = 16.745  # 0.050 mm press-fit interference with switch stem top (Z = 16.795 mm)
    caps = []
    legends = []

    for i in range(1, 59):
        fid = f"F_K{i:02d}"
        feat = features[fid]
        fx, fy = [float(v) for v in feat["center_mm"]]
        fw, _fh = [float(v) for v in feat["size_mm"]]
        cx = xmin + fx
        cy = ymax - fy
        w_u = round((fw + 1.0) / unit_pitch, 2)
        legend_str = _parse_key_legend(feat.get("notes", ""), feat.get("name", ""))

        # Stepped row heights rising from Z = 24.8 mm (Row 5) to Z = 34.0 mm (Row 1)
        # so the sculpted keycaps protrude 7-9 mm proudly above the sloped top bezel
        if fy < 45.0:       # Row 1 (fy = 35.9)
            z_top = 34.0
        elif fy < 65.0:     # Row 2 (fy = 54.95)
            z_top = 31.6
        elif fy < 84.0:     # Row 3 (fy = 74.0)
            z_top = 29.3
        elif fy < 103.0:    # Row 4 (fy = 93.05)
            z_top = 27.0
        else:               # Row 5 (fy = 112.1)
            z_top = 24.8
        h_this = z_top - cap_z0

        z_skirt = 13.6
        total_h = (cap_z0 - z_skirt) + h_this
        cap = cad.keycap(
            w_u=w_u,
            legend="",
            at=(cx, cy, z_skirt),
            unit=unit_pitch,
            height=total_h,
            gap=1.0,
            r=1.4,
            emboss=False,
        )
        recess_w = max(15.2, w_u * unit_pitch - 3.6)
        recess_h = 15.2
        recess = cad.slot(
            cx, cy, w=recess_w, h=recess_h, depth=(cap_z0 - z_skirt) + 0.1, r=0.8, z0=z_skirt - 0.1
        )
        cap = cap - recess
        caps.append(cap)

        leg = cad.keycap_legend(
            legend_str,
            at=(cx, cy, z_skirt),
            height=total_h,
            legend_size=2.8 if len(legend_str) > 2 else 3.2,
            w_u=w_u,
            unit=unit_pitch,
        )
        if leg is not None:
            legends.append(leg)

    keycaps_solid = cad.union(*caps)
    legends_solid = cad.union(*legends)

    out_dir = Path("case/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    cad.export(bottom_shell, out_dir / "bottom_shell.stl")
    cad.export(bootsel_button, out_dir / "bootsel_button.stl")
    cad.export(top_shell, out_dir / "top_shell.stl")
    cad.export(keycaps_solid, out_dir / "keycaps.stl")
    cad.export(legends_solid, out_dir / "keycaps_legends.stl")


if __name__ == "__main__":
    build_enclosure()
