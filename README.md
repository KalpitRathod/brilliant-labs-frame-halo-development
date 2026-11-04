# Brilliant Labs Frame & Halo — Hardware, Firmware & Inventory System

This repository contains the complete hardware CAD models, schematics, firmware codebases, official SDKs, and an end-to-end **Simple Inventory Management & Alert System** for **Brilliant Labs Frame** and **Brilliant Labs Halo** AR glasses.

> 📘 **Master Architecture & Integration Guide:**  
> For an in-depth walkthrough combining hardware fabrication, firmware internals, the on-device Lua HUD script, and the end-to-end developer workflow, see [HARDWARE_FIRMWARE_PROJECT_GUIDE.md](HARDWARE_FIRMWARE_PROJECT_GUIDE.md).

---

## Web Simulator & Glasses HUD Preview

The system features an interactive real-time Web Simulator & Operations Dashboard. It simulates the wearer's micro-OLED field of view, displays live inventory stock levels, and automatically pushes threshold alerts to the glasses:

![Brilliant Labs Web Simulator & Inventory Management Dashboard](demo_screenshots/web_simulator_dashboard.png)

---

## Hardware & CAD References

This repository includes the complete set of mechanical 3D CAD models (.stl / .step), PCB electrical schematics (PDF), and mechanical dimension drawings for all Brilliant Labs hardware platforms.

---

### 1. Brilliant Labs Halo — AI Smart Glasses

Halo is Brilliant Labs' flagship AI eyewear running Zephyr RTOS on the Alif Balletto B1 SoC with dual Arm Cortex-M55 cores and an Ethos-U55 Neural Processing Unit (NPU).

#### 🔗 Official Halo Documentation & Tutorials

| Resource | Link |
| :--- | :--- |
| **Halo Overview** | [docs.brilliant.xyz/halo](https://docs.brilliant.xyz/halo/) |
| **Halo Hardware Manual** | [docs.brilliant.xyz/halo/hardware](https://docs.brilliant.xyz/halo/hardware/) |
| **Halo SDK Guide** | [docs.brilliant.xyz/halo/halo-sdk](https://docs.brilliant.xyz/halo/halo-sdk/) |
| **Halo Lua API Reference** | [docs.brilliant.xyz/halo/halo-sdk-lua](https://docs.brilliant.xyz/halo/halo-sdk-lua/) |
| **Halo Python SDK Guide** | [docs.brilliant.xyz/halo/halo-sdk-python](https://docs.brilliant.xyz/halo/halo-sdk-python/) |
| **Halo Flutter SDK Guide** | [docs.brilliant.xyz/halo/halo-sdk-flutter](https://docs.brilliant.xyz/halo/halo-sdk-flutter/) |
| **Halo BLE/Bluetooth Specs** | [docs.brilliant.xyz/halo/halo-sdk-bluetooth-specs](https://docs.brilliant.xyz/halo/halo-sdk-bluetooth-specs/) |
| **Using Your Halo Guide** | [docs.brilliant.xyz/halo/using-halo](https://docs.brilliant.xyz/halo/using-halo/) |

#### 📁 Downloaded Assets (In This Repository)

| Asset | Format | Local File | Description |
| :--- | :--- | :--- | :--- |
| **Halo 3D CAD Assembly** | `.stl` | [hardware/halo/halo.stl](hardware/halo/halo.stl) | Full 3D assembly model — front frame, lenses, nose bridge, and both temple arms in open wearing position |
| **Halo Hardware Manual** | `.md` | [docs/halo/hardware.md](docs/halo/hardware.md) | Local copy of the official hardware manual with block diagrams and peripheral specs |
| **Halo BLE Block Diagram** | `.svg` | [docs/halo/images/halo-hardware-block-diagram.drawio.svg](docs/halo/images/halo-hardware-block-diagram.drawio.svg) | Architectural interconnect diagram (Alif B1, OLEDoS, camera, power tree, sensors) |
| **Halo BLE Connection Diagram** | `.svg` | [docs/halo/images/halo-bluetooth-connection-diagram.drawio.svg](docs/halo/images/halo-bluetooth-connection-diagram.drawio.svg) | BLE GATT connection flow between host app and glasses |
| **Halo Lua API Reference** | `.md` | [docs/halo/halo-sdk-lua.md](docs/halo/halo-sdk-lua.md) | Full Lua 5.4 API reference for Halo hardware peripherals |
| **Halo Python SDK Guide** | `.md` | [docs/halo/halo-sdk-python.md](docs/halo/halo-sdk-python.md) | Python host-side SDK usage guide |
| **Halo BLE Specs** | `.md` | [docs/halo/halo-sdk-bluetooth-specs.md](docs/halo/halo-sdk-bluetooth-specs.md) | GATT service and characteristic specifications |

#### Key Halo Specifications
| Component | Detail |
| :--- | :--- |
| **Processor** | Alif Semiconductor Balletto B1 (Dual Arm Cortex-M55 @ up to 400 MHz + Arm Ethos-U55 NPU) |
| **OS** | Zephyr RTOS with Lua 5.4 VM — `main.lua` auto-runs on boot |
| **Micro-Display** | 256×256 circular color OLEDoS; immediate draw (no `show()` needed); 24-bit RGB `0xRRGGBB` |
| **Camera** | PixArt Global Shutter VGA (640×480) with configurable `libmpix` ISP pipeline |
| **Audio** | Dual beamforming MEMS mics + stereo bone-conduction speakers (LC3 & PCM encoding) |
| **Input** | Physical right temple push button (single/double/long press) + 6-DoF IMU tap gestures |
| **Connectivity** | Bluetooth Low Energy 5.x; BLE OTA firmware update via MCUboot/SMP |
| **CAD File** | [hardware/halo/halo.stl](hardware/halo/halo.stl) (~10 MB, full assembly) |

---

### 2. Brilliant Labs Frame — AR Glasses

Frame uses a dual-processor architecture pairing a Nordic nRF52840 BLE SoC with a Lattice CrossLink-NX FPGA for ultra-low-power AR HUD processing.

#### 🔗 Official Frame Documentation & Tutorials

| Resource | Link |
| :--- | :--- |
| **Frame Overview** | [docs.brilliant.xyz/frame](https://docs.brilliant.xyz/frame/) |
| **Frame Hardware Manual** | [docs.brilliant.xyz/frame/hardware](https://docs.brilliant.xyz/frame/hardware/) |
| **Frame SDK Guide** | [docs.brilliant.xyz/frame/frame-sdk](https://docs.brilliant.xyz/frame/frame-sdk/) |
| **Frame Lua API Reference** | [docs.brilliant.xyz/frame/frame-sdk-lua](https://docs.brilliant.xyz/frame/frame-sdk-lua/) |
| **Frame Python SDK Guide** | [docs.brilliant.xyz/frame/frame-sdk-python](https://docs.brilliant.xyz/frame/frame-sdk-python/) |
| **Frame Flutter SDK Guide** | [docs.brilliant.xyz/frame/frame-sdk-flutter](https://docs.brilliant.xyz/frame/frame-sdk-flutter/) |
| **Frame BLE/Bluetooth Specs** | [docs.brilliant.xyz/frame/frame-sdk-bluetooth-specs](https://docs.brilliant.xyz/frame/frame-sdk-bluetooth-specs/) |

#### 📁 Downloaded Assets (In This Repository)

| Asset | Format | Local File | Description |
| :--- | :--- | :--- | :--- |
| **Frame 3D CAD Model** | `.stl` | [hardware/frame/frame.stl](hardware/frame/frame.stl) | Complete glasses frame geometry for prototyping, fit checks, and custom modifications |
| **"Mister Power" Charging Cradle** | `.stl` | [hardware/frame/charging-cradle.stl](hardware/frame/charging-cradle.stl) | 3D printable pogo-pin charging dock ("Mister Power") with USB-C port |
| **Prescription (Rx) Clip** | `.stl` | [hardware/frame/frame-rx-clip.stl](hardware/frame/frame-rx-clip.stl) | Snap-on adapter clip to hold corrective prescription lenses behind the AR display |
| **Frame Board Schematics** | `.pdf` | [hardware/frame/frame-schematics.pdf](hardware/frame/frame-schematics.pdf) | Full mainboard PCB schematic (nRF52840 + Lattice FPGA + PMIC + sensors) |
| **Charging Cradle Schematics** | `.pdf` | [hardware/frame/charging-cradle-schematics.pdf](hardware/frame/charging-cradle-schematics.pdf) | PCB schematic for the "Mister Power" USB-C charging dock |
| **Frame Mechanical Drawing** | `.pdf` | [hardware/frame/frame-mechanical-drawing.pdf](hardware/frame/frame-mechanical-drawing.pdf) | Dimensioned blueprint of frame, hinge mechanics, and nose-pad geometry |
| **Lens Mechanical Drawing** | `.pdf` | [hardware/frame/frame-lenses-mechanical-drawing.pdf](hardware/frame/frame-lenses-mechanical-drawing.pdf) | Optical cut-out dimensions, prism alignment, and lens curve radius |
| **Frame Hardware Manual** | `.md` | [docs/frame/hardware.md](docs/frame/hardware.md) | Local copy of the official hardware manual |
| **Frame Lua API Reference** | `.md` | [docs/frame/frame-sdk-lua.md](docs/frame/frame-sdk-lua.md) | Full Frame Lua API reference (display, camera, IMU, BLE, microphone) |
| **Frame Python SDK Guide** | `.md` | [docs/frame/frame-sdk-python.md](docs/frame/frame-sdk-python.md) | Python host-side SDK usage guide |

#### Key Frame Specifications
| Component | Detail |
| :--- | :--- |
| **Processor** | Nordic Semiconductor nRF52840 (Arm Cortex-M4F @ 64 MHz) |
| **FPGA** | Lattice CrossLink-NX (LIFCL-17) — camera ISP and graphics pipeline |
| **OS** | Custom C firmware with embedded Lua 5.4 VM |
| **Micro-Display** | 640×400 micro-OLED; double-buffered — `frame.display.show()` required; 16-color palette |
| **Camera** | OmniVision OV09734 (720×720 → cropped JPEG via FPGA ISP) |
| **Audio** | Single omnidirectional MEMS microphone (PCM) |
| **Input** | 3-axis accelerometer IMU tap interrupt |
| **Connectivity** | Bluetooth Low Energy 5.x; Nordic DFU OTA firmware update |
| **Schematics** | [hardware/frame/frame-schematics.pdf](hardware/frame/frame-schematics.pdf) |

---

### 3. Brilliant Labs Monocle — Pocket AR Display

Monocle is Brilliant Labs' open-source single-eye AR display with fully open hardware in both parametric STEP and mesh STL formats.

#### 🔗 Official Monocle Documentation & Tutorials

| Resource | Link |
| :--- | :--- |
| **Monocle Overview** | [docs.brilliant.xyz/monocle](https://docs.brilliant.xyz/monocle/) |
| **Monocle Hardware Manual** | [docs.brilliant.xyz/monocle/hardware](https://docs.brilliant.xyz/monocle/hardware/) |
| **Building Apps for Monocle** | [docs.brilliant.xyz/monocle/building-apps](https://docs.brilliant.xyz/monocle/building-apps/) |
| **MicroPython on Monocle** | [docs.brilliant.xyz/monocle/micropython](https://docs.brilliant.xyz/monocle/micropython/) |
| **Firmware Update Guide** | [docs.brilliant.xyz/monocle/update](https://docs.brilliant.xyz/monocle/update/) |

#### 📁 Downloaded Assets (In This Repository)

| Asset | Format | Local File | Description |
| :--- | :--- | :--- | :--- |
| **Monocle Body (STEP)** | `.step` | [hardware/monocle/monocle-body.step](hardware/monocle/monocle-body.step) | Parametric CAD for precision engineering (SolidWorks / Fusion 360 / FreeCAD) |
| **Monocle Body (STL)** | `.stl` | [hardware/monocle/monocle-body.stl](hardware/monocle/monocle-body.stl) | Mesh file optimized for 3D printing |
| **Monocle Schematics** | `.pdf` | [hardware/monocle/monocle-schematics.pdf](hardware/monocle/monocle-schematics.pdf) | Full mainboard schematic (nRF52840, Gowin FPGA, Micro-OLED driver, camera) |
| **Charging Case Schematics** | `.pdf` | [hardware/monocle/monocle-cc-schematics.pdf](hardware/monocle/monocle-cc-schematics.pdf) | Portable clamshell charging case PCB schematic |
| **Monocle Dimension Drawing** | `.pdf` | [hardware/monocle/monocle-dimensions.pdf](hardware/monocle/monocle-dimensions.pdf) | Eye relief, field-of-view, and outer envelope dimensions |
| **Case Dimension Drawing** | `.pdf` | [hardware/monocle/monocle-cc-dimensions.pdf](hardware/monocle/monocle-cc-dimensions.pdf) | Charging case pocket and spring contact mechanical drawing |
| **Monocle Hardware Manual** | `.md` | [docs/monocle/hardware.md](docs/monocle/hardware.md) | Local copy of the official hardware manual |
| **Building Monocle Apps** | `.md` | [docs/monocle/building-apps.md](docs/monocle/building-apps.md) | App development guide for Monocle |
| **MicroPython Reference** | `.md` | [docs/monocle/micropython.md](docs/monocle/micropython.md) | MicroPython API reference for Monocle |

---

### 4. Firmware & SDK Sources

| Repository | Local Directory | Description |
| :--- | :--- | :--- |
| **Frame Firmware + FPGA RTL** | [firmware/frame-codebase/](firmware/frame-codebase/) | Nordic nRF52840 C firmware, MCUboot bootloader, Lattice CrossLink-NX SystemVerilog RTL (camera ISP, graphics accelerators) |
| **Halo Firmware** | [firmware/halo-firmware/](firmware/halo-firmware/) | Zephyr RTOS source for Alif Balletto B1 — Lua VM, MCUboot BLE OTA, IMU, camera, audio |
| **Unified Brilliant SDK** | [sdk/python/](sdk/python/) | `brilliant-ble`, `brilliant-msg`, `brilliant-sdk`, `halo-emulator` Python packages |
| **Flutter SDK** | [sdk/flutter/](sdk/flutter/) | `brilliant_ble`, `brilliant_msg`, `brilliant_sdk` Flutter/Dart packages (Melos workspace) |
| **WebBluetooth SDK** | [sdk/webbluetooth/](sdk/webbluetooth/) | TypeScript browser-side BLE packages |
| **Noa Companion App** | [apps/noa-flutter/](apps/noa-flutter/) | Full Flutter source for the official iOS/Android Noa companion app |

#### Official GitHub Repositories
| Repository | URL |
| :--- | :--- |
| **All Brilliant Labs Repos** | [github.com/brilliantlabsAR](https://github.com/brilliantlabsAR) |
| **Frame Firmware & FPGA RTL** | [github.com/brilliantlabsAR/frame-codebase](https://github.com/brilliantlabsAR/frame-codebase) |
| **Halo Firmware (Zephyr)** | [github.com/brilliantlabsAR/halo-firmware](https://github.com/brilliantlabsAR/halo-firmware) |
| **Unified SDK Monorepo** | [github.com/brilliantlabsAR/brilliant_sdk](https://github.com/brilliantlabsAR/brilliant_sdk) |
| **Official Documentation** | [github.com/brilliantlabsAR/docs](https://github.com/brilliantlabsAR/docs) |
| **Noa Flutter App** | [github.com/brilliantlabsAR/noa-flutter](https://github.com/brilliantlabsAR/noa-flutter) |

---

### 5. 3D Printing & Fabrication Guidelines

| Part | Recommended Process | Material | Notes |
| :--- | :--- | :--- | :--- |
| **Glasses Chassis & Temple Arms** | SLS or MJF | Nylon PA12 | Best lightweight durability and snap-fit flex |
| **Prescription (Rx) Clip** | SLA/DLP Resin | Tough Resin or ABS-like | 50-micron layer height for precise optical clip fit |
| **Charging Cradle ("Mister Power")** | FDM | PETG or PLA+ | 0.16–0.20mm layer height, 20% infill |
| **Tolerances** | — | — | Pogo-pin holes and magnetic pockets: +0.15mm clearance |

---

## Workspace Structure

```
├── HARDWARE_FIRMWARE_PROJECT_GUIDE.md# Master Architecture, Firmware & Project Integration Playbook
├── hardware/                         # Mechanical 3D CAD (.stl / .step) & Electrical Schematics (.pdf)
│   ├── halo/halo.stl
│   ├── frame/
│   │   ├── frame.stl, charging-cradle.stl, frame-rx-clip.stl
│   │   └── frame-schematics.pdf, charging-cradle-schematics.pdf, *.pdf
│   └── monocle/
│       ├── monocle-body.step, monocle-body.stl
│       └── monocle-schematics.pdf, monocle-cc-schematics.pdf, *.pdf
│
├── firmware/
│   ├── frame-codebase/               # nRF52840 C firmware + Lattice FPGA RTL
│   └── halo-firmware/                # Zephyr RTOS + Lua VM for Alif Balletto B1
│
├── sdk/
│   ├── python/                       # brilliant-ble, brilliant-msg, brilliant-sdk, halo-emulator
│   ├── flutter/                      # Melos Flutter workspace
│   └── webbluetooth/                 # TypeScript/WebBluetooth SDK
│
├── apps/noa-flutter/                 # Official Noa companion app (Flutter/Dart)
│
├── docs/                             # Full offline copy of docs.brilliant.xyz
│   ├── halo/                         # Halo hardware manual, Lua/Python/Flutter/BLE SDK docs
│   ├── frame/                        # Frame hardware manual, Lua/Python/Flutter/BLE SDK docs
│   └── monocle/                      # Monocle hardware manual, MicroPython, building-apps guides
│
├── demo_screenshots/
│   └── web_simulator_dashboard.png   # Live web simulator dashboard screenshot
│
├── inventory_app/                    # Smart Glasses Inventory & Alert System
│   ├── db.py                         # SQLite + alert engine
│   ├── glasses_bridge.py             # BLE/emulator bridge for Frame & Halo HUD
│   ├── scanner_service.py            # QR/barcode generator & camera scan simulator
│   ├── main.py                       # FastAPI server & REST API
│   ├── cli.py                        # Terminal CLI & end-to-end demo
│   ├── lua/inventory_hud.lua         # On-device Lua HUD app
│   ├── static/                       # current_hud.png preview + barcodes/
│   ├── templates/index.html          # Web dashboard (Bootstrap dark theme)
│   └── tests/test_inventory.py       # Unit test suite
│
└── .venv/                            # Python virtual environment
```

---

## Quick Start: Inventory & Alert System

### 1. Activate Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Launch Web Dashboard
```powershell
.\.venv\Scripts\python.exe inventory_app\main.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### 3. Terminal CLI Commands

```powershell
# Full end-to-end automated demo
.\.venv\Scripts\python.exe inventory_app\cli.py demo

# List all warehouse inventory
.\.venv\Scripts\python.exe inventory_app\cli.py list

# Beam item card to glasses HUD (by SKU or barcode)
.\.venv\Scripts\python.exe inventory_app\cli.py scan HALO-BLK-001

# Adjust stock (+/- quantity)
.\.venv\Scripts\python.exe inventory_app\cli.py adjust HALO-BLK-001 -1

# View all active alerts
.\.venv\Scripts\python.exe inventory_app\cli.py alerts

# Run unit tests
.\.venv\Scripts\python.exe inventory_app\tests\test_inventory.py
```

---

## Hardware Architecture Comparison

| Feature | Brilliant Labs Frame | Brilliant Labs Halo |
| :--- | :--- | :--- |
| **Compute SoC** | Nordic nRF52840 (Cortex-M4F) + Lattice CrossLink-NX FPGA | Alif Balletto B1 (Dual Cortex-M55 + Ethos-U55 NPU) |
| **OS / Runtime** | Custom C Firmware + Embedded Lua VM | Zephyr RTOS + Embedded Lua 5.4 VM |
| **Display** | 640×400 OLED; Double-buffered (`show()` required) | 256×256 round color OLEDoS; Direct draw |
| **Display Colors** | 16-color named palette (`WHITE`, `RED`, etc.) | Full 24-bit RGB hex (`0xRRGGBB`) |
| **Audio** | Single MEMS microphone (PCM) | Dual MEMS mics + stereo bone-conduction speakers (LC3 & PCM) |
| **Camera** | OmniVision OV09734 → cropped JPEG via FPGA | PixArt Global Shutter VGA, `libmpix` pipeline |
| **Input** | 3-axis IMU tap callback | Temple button (single/double/long) + 6-DoF IMU |
| **Firmware OTA** | Nordic DFU BLE update | MCUboot / SMP over BLE |
| **CAD Files** | [hardware/frame/](hardware/frame/) | [hardware/halo/](hardware/halo/) |
| **Schematics** | [hardware/frame/frame-schematics.pdf](hardware/frame/frame-schematics.pdf) | See [docs/halo/hardware.md](docs/halo/hardware.md) |
| **Official Docs** | [docs.brilliant.xyz/frame](https://docs.brilliant.xyz/frame/) | [docs.brilliant.xyz/halo](https://docs.brilliant.xyz/halo/) |
