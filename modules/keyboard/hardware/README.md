# KiCad project — Compact 58-Key Mechanical Desktop Keyboard

Generated from `rea/spec.yaml` by rea-hardware (fab rules, stackup, outline at the origin, mounting
holes), then completed by the electrical agent. Every placed part carries an `LCSC` field and matches
the 150-component `rea/spec.yaml` BOM 1-for-1.

## Architecture & Programming / Bootloader Path

- **MCU & Clocking (`U1`, RP2040, LCSC `C2040`)**:
  - Powered by `3V3_KB` (`IOVDD`, `USB_VDD`, `ADC_AVDD`, `VREG_IN`) with the internal core regulator generating `+1V1` on `VREG_VOUT` (Pin 45) for `DVDD` (Pins 23, 50).
  - Clocked by a 12.000 MHz SMD3225-4P crystal (`Y1`, Abracon `ABM8-272-T3`, LCSC `C20625731`, rated `C_L = 10 pF`, `ESR <= 50 Ohm` max per RP2040 XOSC specification) matched to 12 pF load capacitors (`C15`, `C16`, LCSC `C1547`, giving `C_load = (12 pF * 12 pF) / 24 pF + 4 pF stray = 10 pF`) and a 1 kOhm damping resistor (`R5`, LCSC `C11702`) on `XOUT`.
  - **Crystal Placement & Layout (`Y1`, `R5`, `C15`, `C16`)**: Placed immediately south of `U1` Pins 20 (`XIN`) and 21 (`XOUT`) at `(186.60, 22.65)` mm (`C15` at `(184.10, 22.65)`, `R5` at `(189.30, 21.65)`, `C16` at `(189.30, 23.35)`). `/XIN`, `/XOUT_MCU`, and `/XOUT_XTAL` are routed 100% on `F.Cu` with zero vias over a continuous, unbroken `B.Cu` ground plane (`/COL9` and `/COL10` are routed outside the crystal boundary at `x <= 183.87 mm`).
- **QSPI Flash, UF2 USB Bootloader & Reset Path (`U2`, `R7`, `SW59`, `R6`, `R8`, `J1`)**:
  - External 16 MB QSPI NOR flash `U2` (`W25Q128JVSIQ`, LCSC `C97521`) connects to `U1` `QSPI_SS`, `QSPI_SCLK`, and `QSPI_SD0..SD3`.
  - A 10 kOhm 1% pull-up resistor `R7` (`0402WGF1002TCE`, LCSC `C25744`) placed adjacent to `U2.1` (`~{CS}`) pulls `QSPI_SS_N` up to `3V3_KB` so that flash `~{CS}` tracks `3V3_KB` during power-up and reset while `U1.56` is tri-stated.
  - Bottom-mounted tactile switch `SW59` (`TS-1187A-B-A-B`, LCSC `C318884`, aligned with the bottom enclosure aperture `F_BOOTSEL` and captive actuator `A_BOOTSEL`) pulls `QSPI_SS_N` to `GND` through a 1 kOhm isolation resistor (`R6`, LCSC `C11702`). When `SW59` is pressed, the `R6` / `R7` divider pulls `QSPI_SS_N` to `3.3 V * (1 kOhm / 11 kOhm) = 0.30 V` (`< 0.8 V` `V_IL,max` of `U1` and `U2`).
  - `U1.26` (`RUN`) is pulled up to `3V3_KB` via 10 kOhm 1% resistor `R8` (`0402WGF1002TCE`, LCSC `C25744` at `(196.30, 19.00)` mm).
  - **Reachable post-assembly flashing sequence**: Holding `SW59` via the underside `BOOTSEL` button while plugging the USB-C cable into rear receptacle `J1` (`P_KB_DEV`) powers `VBUS_RAW` -> `F1` (`5V_USB_KB`) -> `U3` (`3V3_KB`) -> `U1` (`VREG_VOUT` = `+1V1`), starts the 12 MHz crystal oscillator (`Y1`), and samples `QSPI_SS_N` low (`0.30 V`) at power-on reset. The RP2040 ROM bootloader then enumerates directly over the wired USB 2.0 D+/D- path (`J1` -> `U4` ESD protection -> `R3`/`R4` 27 Ohm series terminations -> `U1` Pins 46/47) as a USB Mass Storage UF2 programming device without requiring enclosure disassembly.

## Component Rating, Power Tree, ESD Protection & Thermal Verification

- **Coordinated Overcurrent & ESD Protection (`J1`, `C17`, `U4`, `F1`, `D60`, `R1`, `R2`)**:
  - `J1` (`TYPE-C-31-M-12`, LCSC `C165948`): dual `VBUS` contacts (`A4B9`, `B4A9` on `VBUS_RAW`) and dual `GND` contacts (`A1B12`, `B1A12`) plus 4 TH shield tabs rated **5.0 A** total (>= 1.25 A per power contact), exceeding the 0.5 A rail limit and ~65 mA active keyboard current with > 10x margin.
  - **High-Frequency Connector-Side ESD Decoupling & Data-Line Clamping (`C17`, `U4`)**:
    - Local 100 nF 16 V X7R high-frequency ESD decoupling capacitor `C17` (`CL05B104KO5NNNC`, LCSC `C1525` at `(156.40, 8.40)` mm) connects directly between `/VBUS_RAW` and `GND` at `J1` ahead of `F1`.
    - `U4` (`USBLC6-2SC6`, LCSC `C2827654`) is placed immediately adjacent to `J1` at `(159.50, 8.40)` mm (`<= 3 mm` from `J1` pads on `F.Cu` with in-line flow-through routing on `/USB_CONN_DP` and `/USB_CONN_DM`), with Pin 5 (`VBUS`) referenced to `/5V_USB_KB` downstream of `F1` so sustained overvoltage or reverse-polarity faults are current-limited by `F1`.
  - **Series PTC Fuse Isolation & Fuse-Coordinated Shunt TVS Clamping on `5V_USB_KB` (`F1`, `D60`, `C1`)**:
    - `F1` (`BSMD0805-050-24V`, LCSC `C910822`, 0805 PTC resettable fuse at `(158.50, 11.80)` mm): connected in series between `/VBUS_RAW` and `/5V_USB_KB`, rated **24 V**, **500 mA** hold current, **1.0 A** trip current, and **40 A** maximum fault current ($R_{\text{min}} = 0.15\,\Omega$, $R_{\text{typ}} = 0.35\,\Omega$, $R_{1\text{max}} = 0.85\,\Omega$).
    - Immediately downstream of `F1.2` on `/5V_USB_KB` sits a 400 W, 43.6 A peak-pulse, low-clamping 5.0 V unidirectional TVS diode `D60` (`PTVS5V0S1UR-FS`, LCSC `C5380694`, SOD-123FL at `(158.50, 13.90)` mm, $V_{\text{RWM}} = 5.0\text{ V}$, $V_{\text{BR}} = 6.4\text{--}7.0\text{ V}$, $V_{\text{CL}} \le 9.2\text{ V}$ at $I_{\text{PP}} = 43.6\text{ A}$) alongside `U4.5` and 2.2 uF 25 V X7R input decoupling capacitor `C1` (`CL21B225KAFNNNE`, LCSC `C19110` at `(161.30, 12.60)` mm), providing fuse-coordinated overvoltage, reverse-polarity, and ESD clamping ahead of 20 V abs-max LDO `U3`.
  - USB-C UFP (sink) configuration: `CC1` (`J1.A5`) and `CC2` (`J1.B5`) each have dedicated 5.1 kOhm 1% pull-down resistors (`R1` at `(161.50, 3.30)` mm and `R2` at `(153.25, 8.50)` mm, `0402WGF5101TCE`, LCSC `C25905`) connected directly to `GND` on `F.Cu` with zero vias and zero stubs.
- **LDO Voltage Rating, Headroom, Monotonic Placement & Thermal Margin (`U3`, `C1`, `C2`, `C3`, `C4`)**:
  - `U3` (`LDL1117S33R`, STMicroelectronics, LCSC `C435835`, SOT-223-4 at `(166.95, 12.30)` mm in the monotonic power-entry path between `J1`/`F1` and `U2`/`U1`): 3.3 V fixed low-dropout regulator rated **18 V** maximum operating input / **20 V** absolute maximum input (`> 2x` worst-case TVS clamping voltage), **1.2 A** output current capability, low quiescent current **`I_Q = 250 uA` typical / `500 uA` max** (`<< 2.5 mA` USB 2.0 suspend limit), and low dropout **`V_DO = 350 mV` typ / `600 mV` max at 1.2 A** (`< 150 mV` at 250 mA).
  - **Worst-Case Dropout Margin (`> 680 mV` headroom)**: At minimum USB 2.0 bus voltage `VBUS_RAW = 4.40 V`, `I_load = 0.25 A`, and post-trip `R_F1,1max = 0.85 Ohm`, `V_IN,min(U3) = 4.40 V - 0.25 A * 0.85 Ohm = 4.188 V >> 3.35 V + 0.15 V = 3.50 V`.
  - **SOT-223-4 Thermal Margin at Full 0.25 A Continuous Specification**: In SOT-223-4 ($R_{\theta\text{JA}} \approx 60^\circ\text{C/W}$), delivering the full `0.25 A` continuous `3V3_KB` specification in `prompt.md` at `V_IN = 5.0 V` dissipates $P_D = (5.0\text{ V} - 3.3\text{ V}) \times 0.25\text{ A} = 0.425\text{ W}$, producing a junction temperature rise of only $\Delta T_J \approx 25.5^\circ\text{C}$ ($T_J \approx 60.5^\circ\text{C} \ll 125^\circ\text{C}$ max at $35^\circ\text{C}$ enclosure ambient).
  - **Zero-Via Core Regulator & IOVDD Decoupling (`C3`, `C4`)**: `C3` (`1 uF` 25 V X5R, LCSC `C52923` at `(188.35, 10.20)` mm) connects directly on `F.Cu` (`w = 0.20-0.30 mm`, length `1.8 mm`, **zero vias**) to `U1` Pin 45 (`VREG_VOUT`, `/+1V1`), and `C4` (`1 uF` 25 V X5R, LCSC `C52923` at `(190.30, 12.30)` mm) connects directly on `F.Cu` (**zero vias**) to `U1` Pins 42, 43, and 44 (`VREG_IN`, `/3V3_KB`).
- **Capacitor Voltage Ratings (>= 1.5x maximum rail voltage) & USB 2.0 Hot-Plug Inrush Compliance**:
  - `VBUS_RAW` / `5V_USB_KB` rails (5.0 V nominal, 5.25 V max; 1.5x requirement = 7.88 V): `C1` (2.2 uF, **25 V**), `C17` (100 nF, **16 V**). Direct unswitched capacitance on `VBUS` is `2.3 uF <= 10 uF` (`11.5 uC <= 50 uC` USB 2.0 hot-plug limit).
  - `3V3_KB` rail (3.3 V nominal; 1.5x requirement = 4.95 V): `C2` (4.7 uF, **25 V**), `C4` (1 uF, **25 V**), `C7..C14` (8x 100 nF, **16 V**).
  - `+1V1` core rail (1.1 V nominal; 1.5x requirement = 1.65 V): `C3` (1 uF, **25 V**), `C5..C6` (2x 100 nF, **16 V**).
  - `12 MHz Crystal` load network (`XIN` / `XOUT_XTAL`, <= 3.3 V): `C15`, `C16` (12 pF C0G, **50 V**).
  - `D1..D58` (`1N4148W`, LCSC `C81598`, SOD-123F): rated **75 V** / **150 mA** vs 3.3 V GPIO matrix scanning (< 1 mA).
  - `SW1..SW58` (`CPG151101D06`, LCSC `C49234237`) and `SW59` (`TS-1187A-B-A-B`, LCSC `C318884`): rated **12 V DC / 10 mA** and **12 V DC / 50 mA** on 3.3 V logic signals.
  - No MOSFETs are used in this design.
