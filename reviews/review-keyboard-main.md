# Design review: Compact 58-key mechanical desktop keyboard: main board

Datasheet-level review of the schematic and layout by CopperPilot's independent review agent (`validate`). Severity: **P0** must be fixed before fabrication, **P1** should be fixed, **P2** worth a look.

Result: **0 P0**, **0 P1**, **1 P2**.

## P2

### P2.1 U4 (USBLC6-2SC6) VBUS clamp reference is isolated from local 100 nF ESD bypass cap C17 by PTC fuse F1, and C17 (16 V) is under-rated for unclamped VBUS_RAW faults

**Parts:** U4, C17, F1, D60, J1 · **Nets:** /VBUS_RAW, /5V_USB_KB, /USB_CONN_DP, /USB_CONN_DM

On the USB-C entry block (J1), the local 100 nF high-frequency ESD bypass capacitor C17 (CL05B104KO5NNNC, rated 16 V DC) is placed on /VBUS_RAW upstream of PTC resettable fuse F1 (BSMD0805-050-24V, rated 24 V), whereas the USBLC6-2SC6 ESD protection array U4 pin 5 (VBUS rail reference) and TVS diode D60 (PTVS5V0S1UR-FS) are connected to /5V_USB_KB downstream of F1. During a positive IEC 61000-4-2 fast-edge ESD strike (tr = 0.7-1 ns) on /USB_CONN_DP or /USB_CONN_DM, U4 steers transient current out of pin 5 onto /5V_USB_KB, which is separated from C17 by the series resistance and inductance of F1 (R_cold = 0.15-0.85 Ohm plus 3 vias) and must traverse 6.73 mm and 2 vias (including B.Cu segment (159.35, 8.40)->(159.60, 10.70)) to reach D60 and C1, adding ~6-8 nH of series inductance in the ESD clamping path. Furthermore, during a sustained VBUS overvoltage fault (up to 20-24 V from a non-compliant USB-C source) that causes D60 to conduct and trip F1, /VBUS_RAW is isolated from D60 and exposed to the full unclamped fault voltage, exceeding the 16 V DC rating of C17.

**Evidence:** In compact-58key-keyboard.kicad_sch and netlist, /VBUS_RAW connects J1.A4B9, J1.B4A9, C17.1 (lcsc.kicad_sym line 251: '100nF (104) +-10% 16V'), and F1.1 (BSMD0805-050-24V, 24 V max), while /5V_USB_KB connects F1.2, U4.5, D60.1, C1.1, and U3.3. In compact-58key-keyboard.kicad_pcb, U4 pad 5 at (158.35, 8.40) routes through a via to B.Cu (159.35, 8.40)->(159.60, 10.70) and back to F.Cu to reach D60 pad 1 at (160.13, 13.90) (6.73 mm total trace length) with no local 100 nF bypass capacitor on /5V_USB_KB adjacent to U4 pin 5.

**Suggested fix:** Place a local 100 nF (>=25 V) 0402 X7R bypass capacitor directly between U4 pin 5 (/5V_USB_KB) and U4 pin 2 (/GND) on F.Cu with zero vias, and upgrade C17 on /VBUS_RAW to a >=25 V or 50 V rated 0402 X7R capacitor so it survives unclamped voltages up to F1's 24 V rating when F1 trips.

**Status:** open. Agree, disagree or have a better fix? Open an issue.
