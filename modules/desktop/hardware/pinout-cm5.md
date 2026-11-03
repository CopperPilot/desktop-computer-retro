# Raspberry Pi Compute Module 5 (2x 100-pin board-to-board): verified pinout

Source: Raspberry Pi CM5 IO Board rev 2 KiCad files (pip.raspberrypi.com, design files) (fetched from the maker at build time).
Symbol `rea_refs:ComputeModule5-CM5`, footprint `rea_refs:Raspberry-Pi-5-Compute-Module`. Use these: do not draw your own.

| Pin | Name | Type |
|---|---|---|
| 1 | GND | power_in |
| 2 | GND | power_in |
| 3 | Ethernet_Pair3_P | passive |
| 4 | Ethernet_Pair1_P | passive |
| 5 | Ethernet_Pair3_N | passive |
| 6 | Ethernet_Pair1_N | passive |
| 7 | GND | power_in |
| 8 | GND | power_in |
| 9 | Ethernet_Pair2_N | passive |
| 10 | Ethernet_Pair0_N | passive |
| 11 | Ethernet_Pair2_P | passive |
| 12 | Ethernet_Pair0_P | passive |
| 13 | GND | power_in |
| 14 | GND | power_in |
| 15 | Ethernet_nLED3(3.3v) | output |
| 16 | FAN_TACHO | input |
| 17 | Ethernet_nLED2(3.3v) | output |
| 18 | Ethernet_SYNC_OUT(3.3v) | input |
| 19 | FAN_PWM | output |
| 20 | EEPROM_nWP | passive |
| 21 | LED_nACT | open_collector |
| 22 | GND | power_in |
| 23 | GND | power_in |
| 24 | GPIO26 | passive |
| 25 | GPIO21 | passive |
| 26 | GPIO19 | passive |
| 27 | GPIO20 | passive |
| 28 | GPIO13 | passive |
| 29 | GPIO16 | passive |
| 30 | GPIO6 | passive |
| 31 | GPIO12 | passive |
| 32 | GND | power_in |
| 33 | GND | power_in |
| 34 | GPIO5 | passive |
| 35 | ID_SC | passive |
| 36 | ID_SD | passive |
| 37 | GPIO7 | passive |
| 38 | GPIO11 | passive |
| 39 | GPIO8 | passive |
| 40 | GPIO9 | passive |
| 41 | GPIO25 | passive |
| 42 | GND | power_in |
| 43 | GND | power_in |
| 44 | GPIO10 | passive |
| 45 | GPIO24 | passive |
| 46 | GPIO22 | passive |
| 47 | GPIO23 | passive |
| 48 | GPIO27 | passive |
| 49 | GPIO18 | passive |
| 50 | GPIO17 | passive |
| 51 | GPIO15 | passive |
| 52 | GND | power_in |
| 53 | GND | power_in |
| 54 | GPIO4 | passive |
| 55 | GPIO14 | passive |
| 56 | GPIO3 | passive |
| 57 | SD_CLK | passive |
| 58 | GPIO2 | passive |
| 59 | GND | power_in |
| 60 | GND | power_in |
| 61 | SD_DAT3 | passive |
| 62 | SD_CMD | passive |
| 63 | SD_DAT0 | passive |
| 64 | SD_DAT5 | passive |
| 65 | GND | power_in |
| 66 | GND | power_in |
| 67 | SD_DAT1 | passive |
| 68 | SD_DAT4 | passive |
| 69 | SD_DAT2 | passive |
| 70 | SD_DAT7 | passive |
| 71 | GND | power_in |
| 72 | SD_DAT6 | passive |
| 73 | SD_VDD_Override | input |
| 74 | GND | power_in |
| 75 | SD_PWR_ON | output |
| 76 | VBAT | passive |
| 77 | +5v_(Input) | power_in |
| 78 | GPIO_VREF(1.8v/3.3v_Input) | power_in |
| 79 | +5v_(Input) | power_in |
| 80 | SCL0 | passive |
| 81 | +5v_(Input) | power_in |
| 82 | SDA0 | passive |
| 83 | +5v_(Input) | power_in |
| 84 | +3.3v_(Output) | power_out |
| 85 | +5v_(Input) | power_in |
| 86 | +3.3v_(Output) | passive |
| 87 | +5v_(Input) | power_in |
| 88 | +1.8v_(Output) | power_out |
| 89 | WiFi_nDisable | input |
| 90 | +1.8v_(Output) | passive |
| 91 | BT_nDisable | input |
| 92 | PWR_BUT | passive |
| 93 | nRPIBOOT | input |
| 94 | CC1 | passive |
| 95 | LED_nPWR | output |
| 96 | CC2 | passive |
| 97 | CAM_GPIO0 | passive |
| 98 | GND | power_in |
| 99 | PMIC_ENABLE | input |
| 100 | CAM_GPIO1 | passive |
| 101 | USB_OTG_ID | input |
| 102 | PCIe_nCLKREQ | input |
| 103 | USB2_N | passive |
| 104 | PCIE_nWAKE | input |
| 105 | USB2_P | passive |
| 106 | PCIE_PWR_EN | output |
| 107 | GND | power_in |
| 108 | GND | power_in |
| 109 | PCIe_nRST | output |
| 110 | PCIe_CLK_P | output |
| 111 | VBUS_EN | output |
| 112 | PCIe_CLK_N | output |
| 113 | GND | power_in |
| 114 | GND | power_in |
| 115 | MIPI0_D0_N | input |
| 116 | PCIe_RX_P | input |
| 117 | MIPI0_D0_P | input |
| 118 | PCIe_RX_N | input |
| 119 | GND | power_in |
| 120 | GND | power_in |
| 121 | MIPI0_D1_N | input |
| 122 | PCIe_TX_P | output |
| 123 | MIPI0_D1_P | input |
| 124 | PCIe_TX_N | output |
| 125 | GND | power_in |
| 126 | GND | power_in |
| 127 | MIPI0_C_N | input |
| 128 | USB3-0-RX_N | input |
| 129 | MIPI0_C_P | input |
| 130 | USB3-0-RX_P | input |
| 131 | GND | power_in |
| 132 | GND | power_in |
| 133 | MIPI0_D2_N | input |
| 134 | USB3-0-D_P | passive |
| 135 | MIPI0_D2_P | input |
| 136 | USB3-0-D_N | passive |
| 137 | GND | power_in |
| 138 | GND | power_in |
| 139 | MIPI0_D3_N | input |
| 140 | USB3-0-TX_N | output |
| 141 | MIPI0_D3_P | input |
| 142 | USB3-0-TX_P | output |
| 143 | HDMI1_HOTPLUG | input |
| 144 | GND | power_in |
| 145 | HDMI1_SDA | bidirectional |
| 146 | HDMI1_TX2_P | output |
| 147 | HDMI1_SCL | open_collector |
| 148 | HDMI1_TX2_N | output |
| 149 | HDMI1_CEC | open_collector |
| 150 | GND | power_in |
| 151 | HDMI0_CEC | open_collector |
| 152 | HDMI1_TX1_P | output |
| 153 | HDMI0_HOTPLUG | input |
| 154 | HDMI1_TX1_N | output |
| 155 | GND | power_in |
| 156 | GND | power_in |
| 157 | USB3-1-RX_N | input |
| 158 | HDMI1_TX0_P | output |
| 159 | USB3-1-RX_P | input |
| 160 | HDMI1_TX0_N | output |
| 161 | GND | power_in |
| 162 | GND | power_in |
| 163 | USB3-1-D_P | passive |
| 164 | HDMI1_CLK_P | output |
| 165 | USB3-1-D_N | passive |
| 166 | HDMI1_CLK_N | output |
| 167 | GND | power_in |
| 168 | GND | power_in |
| 169 | USB3-1-TX_N | output |
| 170 | HDMI0_TX2_P | output |
| 171 | USB3-1-TX_P | output |
| 172 | HDMI0_TX2_N | output |
| 173 | GND | power_in |
| 174 | GND | power_in |
| 175 | MIPI1_D0_N | output |
| 176 | HDMI0_TX1_P | output |
| 177 | MIPI1_D0_P | output |
| 178 | HDMI0_TX1_N | output |
| 179 | GND | power_in |
| 180 | GND | power_in |
| 181 | MIPI1_D1_N | output |
| 182 | HDMI0_TX0_P | output |
| 183 | MIPI1_D1_P | output |
| 184 | HDMI0_TX0_N | output |
| 185 | GND | power_in |
| 186 | GND | power_in |
| 187 | MIPI1_C_N | output |
| 188 | HDMI0_CLK_P | output |
| 189 | MIPI1_C_P | output |
| 190 | HDMI0_CLK_N | output |
| 191 | GND | power_in |
| 192 | GND | power_in |
| 193 | MIPI1_D2_N | output |
| 194 | MIPI1_D3_N | output |
| 195 | MIPI1_D2_P | output |
| 196 | MIPI1_D3_P | output |
| 197 | GND | power_in |
| 198 | GND | power_in |
| 199 | HDMI0_SDA | bidirectional |
| 200 | HDMI0_SCL | open_collector |

## MIPI 22-way FFC (DSI/CSI port 0, Hirose FH12-22S-0.5SH)

Signal names as on the CM5 (see the table above).

| Pin | Signal |
|---|---|
| 1 | GND |
| 2 | DPHY0_D0_N |
| 3 | DPHY0_D0_P |
| 4 | GND |
| 5 | DPHY0_D1_N |
| 6 | DPHY0_D1_P |
| 7 | GND |
| 8 | DPHY0_C_N |
| 9 | DPHY0_C_P |
| 10 | GND |
| 11 | DPHY0_D2_N |
| 12 | DPHY0_D2_P |
| 13 | GND |
| 14 | DPHY0_D3_N |
| 15 | DPHY0_D3_P |
| 16 | GND |
| 17 | CAM_GPIO0 |
| 18 | CAM_GPIO1 |
| 19 | GND |
| 20 | SCL0 |
| 21 | SDA0 |
| 22 | +3.3v |

## MIPI 22-way FFC (DSI/CSI port 1, Hirose FH12-22S-0.5SH)

Signal names as on the CM5 (see the table above).

| Pin | Signal |
|---|---|
| 1 | GND |
| 2 | DPHY1_D0_N |
| 3 | DPHY1_D0_P |
| 4 | GND |
| 5 | DPHY1_D1_N |
| 6 | DPHY1_D1_P |
| 7 | GND |
| 8 | DPHY1_C_N |
| 9 | DPHY1_C_P |
| 10 | GND |
| 11 | DPHY1_D2_N |
| 12 | DPHY1_D2_P |
| 13 | GND |
| 14 | DPHY1_D3_N |
| 15 | DPHY1_D3_P |
| 16 | GND |
| 17 | (not connected) |
| 18 | (not connected) |
| 19 | GND |
| 20 | SCL1 |
| 21 | SDA1 |
| 22 | +3.3v |

## The module's 3D model

`rea_refs.3dshapes/CM5_module.stl` (STL) and `CM5_module.step` (STEP): the real module, [55.3, 40.3, 4.92] mm, origin at its corner, connectors on its underside (z < 0). Use it as the purchased module's `model` (copy it under case/purchased/ and place it on the board's connectors); a box stand-in fails `mech.meshes`.
