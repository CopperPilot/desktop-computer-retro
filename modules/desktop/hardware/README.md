# KiCad Project — Compact All-in-One CM5 Desktop Computer (`main` Carrier Board)

Generated from `rea/spec.yaml` by rea-hardware (fab rules, stackup, outline at the origin, mounting
holes), then completed by the electrical agent. Every placed part carries a verified `LCSC` field.

## 1. Component Rating & Margin Verification

| Component / Group | Net / Rail | Max Rail Voltage / Peak Current | Part MPN (`LCSC`) | Datasheet Rating | Margin Check |
|---|---|---|---|---|---|
| `C_PD_IN` | `VBUS_IN` (unswitched `J_PWR` VBUS) | 15.0 V nominal (24.4 V surge clamp) | `CC0805KKX7R9BB105` (`C91185`, 1 uF 50 V X7R 0805) | 50 V X7R | 50 V = 3.33x of 15 V (> 24.4 V TVS clamp); keeps unswitched `J_PWR` `cSnkVBus` = 1.0 uF direct (2.0 uF total including `C_PD_VHV` behind 1 kOhm `R_PD_VHV`), well below the 10 uF USB Type-C limit |
| `Q_PD_SW` + `R_PD_PG` + `R_PD_PG2` + `C_PD_SS` | `VBUS_IN` -> `VBUS_PD` (15 V PD) | 15.0 V / 1.85 A peak (24.4 V surge clamp) | `AO3407A` (`C347478`, SOT-23) + 2x `0402WGF1003TCE` (`C25741`, 100k) + `CL05B104KB54PNC` (`C307331`, 100 nF 50 V) | `AO3407A`: -30 V `V_DS`, ±20 V `V_GS`, -4.2 A continuous, `R_DS(on)` = 37 mOhm typ at -10 V / 42 mOhm at -7.5 V (`P_D` = 1.4 W) | `R_PD_PG`=100k and `R_PD_PG2`=100k set `V_GS` = -7.50 V at 15 V (-12.2 V max at 24.4 V TVS clamp << ±20 V `V_GS(max)`) with `tau_G` = 5.0 ms soft-start (`C_PD_SS`=100 nF), isolating 67.1 uF (`C_PD_BULK` + `C_VIN1..3`) until `U_PD` `PG` asserts low |
| `C_PD_BULK` | `VBUS_PD` (switched 15 V PD) | 15.0 V nominal (24.4 V surge clamp) | `CA55-D035K476TE150` (`C2761441`, 47 uF 35 V Case-D 7343 tantalum, 150 mOhm ESR) | 35 V MnO2 tantalum | 35 V = 2.33x of 15 V (> 24.4 V TVS clamp); isolated behind `Q_PD_SW` during hot-plug and PD negotiation |
| `C_VIN1`, `C_VIN2` | `VBUS_PD` (switched 15 V PD) | 15.0 V nominal (24.4 V surge clamp) | `HGC0805R5106K350NSLJ` (`C33546007`, 10 uF 0805) | 35 V X5R | 35 V >= 2.33x of 15 V (> 24.4 V TVS clamp); isolated behind `Q_PD_SW` until PD negotiation completes |
| `C_VIN3`, `C_BUCK_BST`, `C_BUCK_EN` | `VBUS_PD` / `BUCK_BST` / `BUCK_EN` | 15.0 V / 18.3 V / 2.5 V | `CL05B104KB54PNC` (`C307331`, 100 nF 0402) | 50 V X7R | 50 V >= 2.73x of 18.3 V (> 27.7 V surge) |
| `C_PD_VHV`, `C_BUCK_VREG` | `PD_VHV` / `BUCK_VREG5` | 14.2 V / 3.3 V | `CL10A105KB8NNNC` (`C15849`, 1 uF 0603) | 50 V / 25 V X5R | `C_PD_VHV` isolated from `VBUS_IN` via `R_PD_VHV` = 1 kOhm (`0402WGF1001TCE`, `C11702`) per CH224A datasheet |
| `C_5V1..C_5V3` | `5V_SYS` | 5.0 V max | `C2012X5R1A476MTJ00E` (`C76636`, 47 uF 0805) | 10 V X5R | 3x 47 uF = 141 uF nominal (~70 uF effective at 5 V) adjacent to `L_BUCK.2` / `U_BUCK.9` |
| `C_CM5_BULK` | `5V_SYS` (at `U_CM5` pins 77-87) | 5.0 V max | `SA11AM101A19R15XXX` (`C135491`, 100 uF Case-A polymer, 15 mOhm ESR) | 10 V solid polymer | 10 V = 2.0x of 5 V; buffers CM5 3.0 A load steps directly at mezzanine socket |
| `C_3V3_IN`, `C_3V3_OUT1`, `C_3V3_OUT2`, `C_BL_IN`, `C_3V3_1`, `C_KB_VBUS`, `C_MOUSE_VBUS` | `5V_SYS`, `3V3_SYS`, `3V3_CM5`, `5V_USB_*` | <= 5.0 V max | `HGC0805R5106K350NSLJ` (`C33546007`, 10 uF 0805) | 35 V X5R | 35 V >= 7.0x of 5 V (>= 1.5x required) |
| `C_BL_COMP` | `BL_COMP` | <= 3.3 V max | `TCC0402X7R224K250AT` (`C915854`, 220 nF 0402) | 25 V X7R | Matches TPS61165 datasheet 220 nF COMP requirement |
| `C_BL_OUT` | `BL_LED_A` (LED string) | ~9.9 V typ (38 V OVP) | `CC0805KKX7R9BB105` (`C91185`, 1 uF 50 V X7R 0805) | 50 V X7R | 50 V = 1.32x above 38 V OVP cutoff |
| `C_5V4`, `C_CM5_5V`, `C_3V3_2`, `C_3V3_3`, `C_3V3_HF`, `C_CM5_1V8`, `C_BOOT_VBUS`, `C_KB_DEC`, `C_MOUSE_DEC`, `C_CC_KB`, `C_CC_MOUSE`, `C_DSI_3V3`, `C_HDMI_5V` | `5V_SYS` / `3V3_SYS` / `3V3_CM5` / `1V8_CM5` | <= 5.0 V max | `CL05B104KB54PNC` (`C307331`, 100 nF 0402) | 50 V X7R | 50 V >= 10.0x of 5 V |
| `C_BUCK_SS` | `BUCK_SS` | 3.3 V max | `0402B223K500NT` (`C1532`, 22 nF 0402) | 50 V X7R | Programs `t_SS = 22 nF * 0.6 V / 6 uA = 2.2 ms` soft-start |
| `U_PD` + `R_PD_CFG1` + `R_PD_VHV` | `VBUS_IN`, `CC1`, `CC2`, `PD_CFG1`, `PD_VHV` | 15.0 V PD | `CH224A` (`C42459160`) + `RC0402FR-0756KL` (`C114756`, 56 kOhm 1%) + `0402WGF1001TCE` (`C11702`, 1 kOhm 1%) | 4 V to 30 V operating (`VHV` pin 1 fed from `VBUS_IN` via `R_PD_VHV` = 1 kOhm `C11702` + 1 uF `C_PD_VHV` per CH224A application circuit); `CFG1` (pin 9) strapped to `GND` via `R_PD_CFG1` = 56 kOhm 1% (`C114756`) to request mandatory 15 V USB-PD 3.0 fixed PDO | 30 V max > 24.4 V TVS clamp on 15 V rail; 56 kOhm requests 15 V (1.85 A peak at 27.71 W input < 3.0 A PDO limit) |
| `U_BUCK` + `L_BUCK` + `C_BUCK_EN` | `VBUS_PD` -> `5V_SYS` | 15.0 V in (24.4 V surge clamp), 5.0 V / 4.89 A peak | `SY8205FCC` (`C111875`) + `PSPMAA0503-4R7M-ANP` (`C436535`) + `CL05B104KB54PNC` (`C307331`) | 4.5-30 V recommended operating / 33 V abs max input, 5.0 A continuous / 6.0 A peak (`V_REF` = 0.600 V; `R_BUCK_FB1`=73.2k `C26986` / `R_BUCK_FB2`=10k `C25744` -> `V_OUT` = 4.992 V); `R_BUCK_EN1`=100k / `R_BUCK_EN2`=20k + `C_BUCK_EN`=100 nF on switched `VBUS_PD` sets `V_BUCK_EN` = 2.50 V at 15.0 V (`>= 2.38 V` at 14.25 V > `V_ENH` = 1.2 V) with `tau_EN` = 1.67 ms RC delay after `Q_PD_SW` charges `VBUS_PD` | 30 V rec / 33 V abs max safely exceeds `D_PD_VBUS` (`PTVS15VS1UR,115`, `V_BR`=16.7-18.5 V, `V_CL`=24.4 V at 16.4 A); `Q_PD_SW` isolates `VBUS_PD` until `U_PD.10` (`PG`) asserts |
| `U_3V3` + `L_3V3` + `Q_3V3_INV` + `Q_3V3_DIS` + `R_3V3_DIS` + `R_3V3_BLEED` + `D_3V3_CLAMP` + `U_SW_DSI` + `R_DSI_DIS` | `5V_SYS` -> `3V3_SYS` -> `3V3_DSI` | 3.3 V / 0.55 A peak (`front_io` + `J_DSI.22`) | `TLV62569DBVR` (`C141836`) + `SPH4018H2R2MT` (`C370436`, 2.2 uH) + 2x `BSS138` (`C78284`) + `0402WGF330JTCE` (`C25105`, 33R) + `0402WGF1001TCE` (`C11702`, 1k) + `B5819W` (`C2943878`) + `TPS2051BDBVR` (`C24593`) | `TLV62569DBVR`: 2.5-5.5 V in, 2.0 A out (`R_3V3_FB1`=100k `C25741` / `R_3V3_FB2`=22.1k `C43473` -> `V_OUT` = 3.31 V), enabled by `3V3_CM5`; active discharge (`Q_3V3_INV`/`Q_3V3_DIS` + `R_3V3_DIS`=33R + `R_3V3_BLEED`=1k, `tau` = 1.85 ms) and `D_3V3_CLAMP` (`B5819W` Anode `3V3_SYS` -> Cathode `3V3_CM5`) clamp `3V3_SYS <= 3V3_CM5 + 0.25 V` during shutdown/reset; `TPS2051BDBVR`: 500 mA soft-start load switch gating `J_DSI.22` (`3V3_DSI`) via `DSI1_EN` with `R_DSI_DIS`=1k (`C11702`) output bleeder and `R_DSI_SCL`/`R_DSI_SDA`=1.8k (`C25871`) referenced to switched `3V3_DSI` | Offloads `front_io` SD card and `J_DSI.22` LCD panel from `3V3_CM5`, prevents cross-domain GPIO back-drive during power-down, and eliminates I2C back-powering into `3V3_DSI` when `U_SW_DSI` is off |
| `U_BL` + `L_BL` + `D_BL` + `R_BL_SET` + `R_BL_FB` + `D_BL_FB` + `D_BL_A` | `5V_SYS` -> `BL_LED_A` / `BL_FB` | 9.9 V typ / 220 mA (3S11P WLED, 38 V OVP) | `TPS61165DBVR` (`C58756`) + `SWPA4030S220MT` (`C83472`) + `MBR0560` (`C77338`) + `0805W8F910LT5E` (`C17478`, 0.91 Ohm) + `0402WGF4701TCE` (`C25900`, 4.7k) + `PTVSLC3D3V3B` (`C246774`) + `PTVS36VS1UR,115` (`C171823`) | 38 V boost switch, 1.2 A switch limit, 60 V Schottky; `I_LED` = 0.200 V / 0.91 Ohm = 220 mA; `R_BL_FB` (4.7k) + `D_BL_FB` (3.3 V TVS) protects `U_BL.6` (`FB`, 3.6 V abs max) on 375 mm `J_BL` harness | `C_BL_IN`=10 uF and `C_BL_COMP`=220 nF meet TPS61165 datasheet; `BL_FB` and `BL_LED_A` protected against harness ESD/short faults |
| `U_SW_HDMI` | `5V_SYS` -> `5V_HDMI` (`J_HDMI.18`) | 5.0 V / 55 mA HDMI +5V Power | `AP2331SA-7` (`C500764`, SOT-23-3) | 0.2 A continuous / <= 0.4 A current-limited reverse-blocking load switch (`R_DS(on)` = 250 mOhm typ) | Maintains 4.986 V >= 4.8 V at 55 mA while enforcing <= 0.4 A short-circuit limit |
| `U_CC_KB`, `U_CC_MOUSE`, `U_SW_KB`, `U_SW_MOUSE`, `Q_KB_EN`, `Q_MOUSE_EN`, `R_KB_DIS`, `R_MOUSE_DIS` | `5V_SYS` -> `5V_USB_KB`, `5V_USB_MOUSE` | 5.0 V / 500 mA USB 2.0 host (Cold Socket) | `TUSB320LIRWBR` (`C2836598`) + `TPS2041BDBVR` (`C51386`) + `2N7002` (`C8545`) + 2x `0402WGF1002TCE` (`C25744`, 10k) | `TUSB320LIRWBR` DFP mode (`PORT` pulled to `5V_SYS` via 4.7k `R_KB_PORT`/`R_MOUSE_PORT`, `VBUS_DET` via 910k `R_KB_VDET`/`R_MOUSE_VDET`); `TPS2041B` 500 mA continuous; `R_KB_DIS`/`R_MOUSE_DIS`=10k discharge 10.1 uF to `vSafe0V` (0.8 V) in `t_vSafe0V` = 183.3 ms < 650 ms | `TUSB320LIRWBR` open-drain `ID` (Pin 9) pulls `~{EN}` low only when valid 5.1k `Rd` is attached; `R_KB_DIS`/`R_MOUSE_DIS` guarantee `< 650 ms` `vSafe0V` discharge upon detach for rapid re-attach |
| `D_ESD_BOOT`, `D_ESD_KB`, `D_ESD_MOUSE` | `J_BOOT`, `J_KB`, `J_MOUSE` `D+/D-` & `VBUS` | 5.0 V VBUS / 3.3 V USB 2.0 HS | `USBLC6-2SC6` (`C2827654`, SOT-23-6) | 5.25 V VBUS standoff, 2.5 pF I/O capacitance | Rail-clamped ESD protection on USB 2.0 differential pairs and 5 V VBUS |
| `D_ESD_PWR`, `D_HDMI_ESD1..3` | `J_PWR` `D+/D-`, `J_HDMI` TMDS & DDC/CEC/HPD | 3.3 V TMDS/CEC, 5.0 V DDC/HPD | `TPD4E05U06DQAR` (`C138714`, USON-10) | 5.5 V reverse standoff, 0.4-0.5 pF ultra-low capacitance | Ground-referenced TVS protection for HDMI TMDS, direct CM5-conditioned HDMI DDC/CEC/HPD (`HDMI0_SCL`, `HDMI0_SDA`, `HDMI0_CEC`, `HDMI0_HOTPLUG`), and `J_PWR` D+/D- |
| `D_PD_CC1/2`, `D_BOOT_CC1/2`, `D_KB_TVS1/2`, `D_MOUSE_TVS1/2`, `D_SW_PWR`, `D_SW_BOOT`, `D_PD_VBUS` | USB-C `CC1`/`CC2`, `PWR_BUT`, `nRPIBOOT`, `VBUS_IN` | 5.0 V CC / 3.3 V buttons / 15.0 V `VBUS_IN` | `TSD05CDYFR` (`C20611048`, SOD-323) & `PTVS15VS1UR,115` (`C513104`, SOD-123) | `TSD05CDYFR`: 5.5 V standoff (~9 V clamp, ~11 pF) bidirectional TVS to `GND`; `PTVS15VS1UR,115`: 15.0 V standoff (`V_BR` = 16.7-18.5 V, `V_CL` = 24.4 V at 16.4 A) on 15 V `VBUS_IN` | Low-clamping 5.5 V ESD protection on all CC pins and rear pushbuttons; 15 V standoff TVS + 47 uF 35 V damped bulk cap protects `Q_PD_SW` and `U_BUCK` (30 V operating max) |
| `U_CM5` (`+5v_(Input)`) | `5V_SYS` | 3.0 A CM5 peak | `DF40C-100DS-0.4V(51)` (`C597931`) | 0.3 A/pin x 6 pins = 1.8 A continuous (3.6 A peak across 6 pins) | All 6 `+5v_(Input)` pins (77, 79, 81, 83, 85, 87) tied to `5V_SYS` with `PSU_MAX_CURRENT=5000` in EEPROM |

## 2. CM5 eMMC Flashing, Bootloader & EEPROM Power Configuration (`PSU_MAX_CURRENT=5000`)

1. Rear USB-C port `J_BOOT` connects directly to `U_CM5` `USB2_P` (Pin 105) and `USB2_N` (Pin 103) with 90 ohm differential routing and no intervening USB hub.
2. `J_BOOT` is configured as a USB-C sink with two independent 5.1 kOhm `Rd` pull-down resistors (`R_BOOT_CC1`, `R_BOOT_CC2`) to `GND`.
3. `U_CM5` `USB_OTG_ID` (Pin 101) is left open on the carrier board to use the CM5's internal pull-up for device/OTG bootstrap mode without conflicting external pull-ups.
4. Holding rear pushbutton `SW_BOOT` pulls `U_CM5` `nRPIBOOT` (Pin 93, internally pulled up on the CM5 module) to `GND`, forcing BCM2712 ROM USB device boot (`rpiboot`) on power-up; rear pushbutton `SW_PWR` pulls `PWR_BUT` (Pin 92, internally pulled up to the CM5 PMIC always-on standby domain) to `GND`.
5. Because 15 V USB-PD negotiation is handled externally by `U_PD` (`CH224A`) feeding the 5 V / 5 A synchronous buck converter `U_BUCK` (`SY8205FCC`) rather than `U_CM5` `CC1`/`CC2` (pins 94/96), factory `rpiboot` EEPROM provisioning sets `PSU_MAX_CURRENT=5000` in the bootloader configuration so the CM5 PMIC enables full 5.0 A input current budget without USB-C CC interrogation.

## 3. Inter-Board 22-Pin FFC Pinout (`J_FIO` on `main` <-> `J_SUB_FIO` on `front_io`)

Type-B (opposite-side contact, 1-to-1 pin mapping) 22-pin 0.5 mm FFC (`FH12-22S-0.5SH(55)`) connecting top-mounted `J_FIO` (`F.Cu`, `rot=0`) on `main` to bottom-mounted `J_SUB_FIO` (`B.Cu`, `rot=0`, mirrored X pad coordinates) on `front_io`, routed to RP1 GPIO Bank 0 secondary SDIO (`GPIO22..27` constrained to <= 12.5 MHz Default-Speed mode with 80 ns clock period via CM5 RP1 `mmc` device-tree overlay `max-frequency = <12500000>`) with `G-S-S-G-S-S-G-S-G` ground return interleaving across pins 5-13:

| `J_FIO` Pin (`main`) | `J_SUB_FIO` Pin (`front_io`) | Net Name (`main`) | Signal / Function | CM5 Pin (`U_CM5`) / Source |
|---|---|---|---|---|
| 1 | 1 | `3V3_SYS` | +3.3 V peripheral supply from `U_3V3` (`TLV62569DBVR`, 2.0 A, with active discharge + `B5819W` clamp to `3V3_CM5`) | `U_3V3` (`3V3_SYS`) |
| 2 | 2 | `3V3_SYS` | +3.3 V peripheral supply from `U_3V3` (`TLV62569DBVR`, 2.0 A, with active discharge + `B5819W` clamp to `3V3_CM5`) | `U_3V3` (`3V3_SYS`) |
| 3 | 3 | `GND` | Ground return | `GND` |
| 4 | 4 | `SD_CLK_GPIO22` | Secondary SDIO Clock (`SD1_CLK` via 33 Ohm series source termination `R_SD_CLK`) | Pin 46 (`GPIO22`) |
| 5 | 5 | `GND` | Ground guard for `SD_CLK` | `GND` |
| 6 | 6 | `SD_CMD_GPIO23` | Secondary SDIO Command (`SD1_CMD` via 33 Ohm `R_SD_CMD` + 100 kOhm `R_SD_CMD_PU` to `3V3_CM5`) | Pin 47 (`GPIO23`) |
| 7 | 7 | `SD_DAT0_GPIO24` | Secondary SDIO Data 0 (`SD1_DAT0` via 33 Ohm `R_SD_DAT0` + 100 kOhm `R_SD_DAT0_PU` to `3V3_CM5`) | Pin 45 (`GPIO24`) |
| 8 | 8 | `SDIO_RET` | Interleaved SDIO ground return (`0R` `R_FIO_RET1` to `GND`) | `GND` (via `R_FIO_RET1`) |
| 9 | 9 | `SD_DAT1_GPIO25` | Secondary SDIO Data 1 (`SD1_DAT1` via 33 Ohm `R_SD_DAT1` + 100 kOhm `R_SD_DAT1_PU` to `3V3_CM5`) | Pin 41 (`GPIO25`) |
| 10 | 10 | `SD_DAT2_GPIO26` | Secondary SDIO Data 2 (`SD1_DAT2` via 33 Ohm `R_SD_DAT2` + 100 kOhm `R_SD_DAT2_PU` to `3V3_CM5`) | Pin 24 (`GPIO26`) |
| 11 | 11 | `GND` | Ground return | `GND` |
| 12 | 12 | `SD_DAT3_GPIO27` | Secondary SDIO Data 3 (`SD1_DAT3` via 33 Ohm `R_SD_DAT3` + 100 kOhm `R_SD_DAT3_PU` to `3V3_CM5`) | Pin 48 (`GPIO27`) |
| 13 | 13 | `SDIO_RET` | Interleaved SDIO ground return (`0R` `R_FIO_RET2` to `GND`) | `GND` (via `R_FIO_RET2`) |
| 14 | 14 | `SD_PWR_ON` | SD Card High-Side Switch (`U1` `AP22653W6-7`) Enable (100 kOhm pull-down `R_SD_PWR_PD` to `GND`) | Pin 34 (`GPIO5`) |
| 15 | 15 | `GND` | Ground return | `GND` |
| 16 | 16 | `ENC_A` | Brightness Rotary Encoder Phase A | Pin 50 (`GPIO17`) |
| 17 | 17 | `ENC_B` | Brightness Rotary Encoder Phase B | Pin 26 (`GPIO19`) |
| 18 | 18 | `ENC_SW` | Brightness Rotary Encoder Pushbutton | Pin 27 (`GPIO20`) |
| 19 | 19 | `SD_FAULT_VSS_N` | SD Card Load Switch `~{FAULT}` Interrupt (`U1.4`) | Pin 38 (`GPIO11`) |
| 20 | 20 | `SD_CD_VSS_GPIO6` | SD Card Detect | Pin 30 (`GPIO6`) |
| 21 | 21 | `SD_WP_VSS_GPIO13` | SD Write Protect | Pin 28 (`GPIO13`) |
| 22 | 22 | `GND` | Ground return | `GND` |
| 23, 24 | 23, 24 | `GND` | Mechanical mounting tabs | `GND` |

## 4. MIPI DSI1 22-Pin FFC Pinout (`J_DSI` on `main`)

Standard Raspberry Pi 22-way 0.5 mm pitch FFC DSI pinout (`pinout-cm5.md`) driving the native 3.3 V single-supply 8.0-inch 4:3 (1024x768) IPS MIPI-DSI display module (`KD080D10-22MIPI-A1`, featuring an integrated Fitipower EK79007 / Ilitek ILI9881C 4-lane MIPI-DSI T-CON and internal charge-pump AVDD/VGH/VGL bias generator powered from 3.3 V `/3V3_DSI` on pin 22) over a 100-Ohm impedance-controlled, double-shielded silver-ink EMI-shielded 22-pin 0.5 mm FFC (`375 mm`, operating at `1024x768 @ 60 Hz` across all 4 MIPI DSI lanes = `283 Mbps/lane` / `141.5 MHz` Nyquist clock, `< 1.2 dB` insertion loss vs `> 6 dB` MIPI D-PHY v1.2 HS receiver budget), with `J_DSI.22` (`3V3_DSI`) gated by soft-start load switch `U_SW_DSI` (`TPS2051BDBVR`) from `3V3_SYS` and discharged when OFF by `R_DSI_DIS` (`1 kOhm`):

| `J_DSI` Pin | Net Name | Function / CM5 Pin (`U_CM5`) |
|---|---|---|
| 1, 4, 7, 10, 13, 16, 19 | `GND` | Ground return (every 3rd pin) |
| 2, 3 | `MIPI1_D0_N`, `MIPI1_D0_P` | DSI1 Lane 0 (Pins 175, 177) |
| 5, 6 | `MIPI1_D1_N`, `MIPI1_D1_P` | DSI1 Lane 1 (Pins 181, 183) |
| 8, 9 | `MIPI1_C_N`, `MIPI1_C_P` | DSI1 Clock (Pins 187, 189) |
| 11, 12 | `MIPI1_D2_N`, `MIPI1_D2_P` | DSI1 Lane 2 (Pins 193, 195) |
| 14, 15 | `MIPI1_D3_N`, `MIPI1_D3_P` | DSI1 Lane 3 (Pins 194, 196) |
| 17, 18 | `DSI1_RST`, `DSI1_EN` | Panel Reset (`CAM_GPIO0`, Pin 97) / Panel Enable (`CAM_GPIO1`, Pin 100, also enabling `U_SW_DSI`) |
| 20, 21 | `MIPI1_SCL`, `MIPI1_SDA` | Panel I2C (`SCL0` Pin 80, `SDA0` Pin 82) with 1.8 kOhm pull-ups (`R_DSI_SCL`, `R_DSI_SDA`) to switched `3V3_DSI` |
| 22 | `3V3_DSI` | +3.3 V Switched Panel Logic Supply from `U_SW_DSI` (`TPS2051BDBVR`, fed from `3V3_SYS`, with 1 kOhm `R_DSI_DIS` bleeder) |
| 23, 24 | `GND` | Mechanical mounting tabs |
