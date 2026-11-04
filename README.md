# Brilliant Labs Frame & Halo — Hardware, Firmware & Inventory System

This repository contains the complete hardware CAD models, schematics, firmware codebases, official SDKs, and an end-to-end **Simple Inventory Management & Alert System** for **Brilliant Labs Frame** and **Brilliant Labs Halo** AR glasses.

---

## Web Simulator & Glasses HUD Preview

The system features an interactive real-time Web Simulator & Operations Dashboard. It simulates the wearer's micro-OLED field of view (supporting Halo 256×256 round and Frame 640×400 rectangular formats), displays live inventory stock, and automatically pushes threshold alerts:

![Brilliant Labs Web Simulator & Inventory Management Dashboard](demo_screenshots/web_simulator_dashboard.png)

---

## Hardware & CAD References

This repository includes the complete set of mechanical CAD models (3D STL & STEP files), printed circuit board (PCB) electrical schematics (PDF), and mechanical dimension drawings across all Brilliant Labs eyewear hardware platforms.

### 1. Brilliant Labs Halo (AI Smart Glasses)

Halo is Brilliant Labs' flagship AI eyewear running Zephyr RTOS on an Alif Balletto B1 SoC with dual Arm Cortex-M55 cores and an Ethos-U55 Neural Processing Unit (NPU).

| Asset | Format | File Path | Description |
| :--- | :--- | :--- | :--- |
| **Halo 3D CAD Model** | `.stl` | [`hardware/halo/halo.stl`](hardware/halo/halo.stl) | Full 3D assembly including front frame, custom lenses, nose bridge, and both temple arms in the open wearing position. |
| **Hardware Manual** | `.md` | [`docs/halo/hardware.md`](docs/halo/hardware.md) | Official hardware manual containing subsystem breakdowns, assembly overview, and peripheral pinouts. |
| **Hardware Block Diagram** | `.svg` | [`docs/halo/images/halo-hardware-block-diagram.drawio.svg`](docs/halo/images/halo-hardware-block-diagram.drawio.svg) | Architectural interconnect diagram between Alif B1 SoC, camera, OLEDoS, power tree, and sensors. |
| **BLE Protocol Specs** | `.md` | [`docs/halo/halo-sdk-bluetooth-specs.md`](docs/halo/halo-sdk-bluetooth-specs.md) | Detailed GATT service specifications for Lua script execution, data streaming, and telemetry. |

#### Key Halo Specifications:
* **Processor**: Alif Semiconductor Balletto B1 (Dual Arm Cortex-M55 @ up to 400 MHz + Arm Ethos-U55 NPU)
* **Operating System**: Zephyr RTOS with integrated Lua 5.4 virtual machine
* **Micro-Display**: 256×256 circular color OLEDoS; direct-draw immediate mode (no double-buffer wait required); 24-bit RGB (`0xRRGGBB`)
* **Camera Sensor**: PixArt Global Shutter VGA (640×480) with programmable `libmpix` ISP pipeline
* **Audio**: Dual beamforming MEMS microphones + stereo bone-conduction temple transducers (LC3 & PCM support)
* **Sensors & Input**: 6-DoF IMU (accelerometer/gyroscope) with tap gesture detection + physical right temple push button (single/double/long press)
* **Battery & Power**: Integrated rechargeable Li-Po cell with custom magnetic multi-pin charging interface

---

### 2. Brilliant Labs Frame (AR Glasses)

Frame utilizes a dual-processor architecture pairing a Nordic nRF52840 BLE SoC with a Lattice CrossLink-NX FPGA for ultra-low-power vision and HUD processing.

| Asset | Format | File Path | Description |
| :--- | :--- | :--- | :--- |
| **Frame 3D CAD Model** | `.stl` | [`hardware/frame/frame.stl`](hardware/frame/frame.stl) | Complete physical glasses frame 3D geometry for rapid prototyping, fit checks, and custom modifications. |
| **"Mister Power" Cradle** | `.stl` | [`hardware/frame/charging-cradle.stl`](hardware/frame/charging-cradle.stl) | 3D printable charging dock ("Mister Power") housing the pogo-pin charging interface and USB-C port. |
| **Prescription (Rx) Clip** | `.stl` | [`hardware/frame/frame-rx-clip.stl`](hardware/frame/frame-rx-clip.stl) | Snap-on prescription lens adapter clip designed to hold corrective optical lenses behind the AR display. |
| **Frame Board Schematics** | `.pdf` | [`hardware/frame/frame-schematics.pdf`](hardware/frame/frame-schematics.pdf) | Complete electrical schematic diagrams for the Frame mainboard (nRF52840, FPGA, PMIC, level shifters). |
| **Cradle Schematics** | `.pdf` | [`hardware/frame/charging-cradle-schematics.pdf`](hardware/frame/charging-cradle-schematics.pdf) | Electrical schematics for the "Mister Power" USB-C charging dock and power delivery circuit. |
| **Frame Mechanical Drawing** | `.pdf` | [`hardware/frame/frame-mechanical-drawing.pdf`](hardware/frame/frame-mechanical-drawing.pdf) | Dimensioned mechanical blueprint of the glasses frame, hinge mechanics, and nose-pad geometry. |
| **Lens Mechanical Drawing** | `.pdf` | [`hardware/frame/frame-lenses-mechanical-drawing.pdf`](hardware/frame/frame-lenses-mechanical-drawing.pdf) | Engineering blueprint specifying lens curve radius, optical cutouts, and prism alignment dimensions. |
| **Hardware Manual** | `.md` | [`docs/frame/hardware.md`](docs/frame/hardware.md) | Official Frame hardware documentation. |

#### Key Frame Specifications:
* **Compute Architecture**: Nordic Semiconductor nRF52840 (64 MHz Arm Cortex-M4F) + Lattice CrossLink-NX (LIFCL-17) FPGA
* **Micro-Display**: 640×400 micro-OLED; double-buffered display pipeline (`frame.display.show()` required); 16-color named palette
* **Camera Sensor**: OmniVision OV09734 (720×720 cropped JPEG generated on-chip via FPGA ISP)
* **Audio**: Single MEMS omnidirectional microphone
* **Sensors & Input**: 3-axis accelerometer / IMU tap interrupt detection
* **Power & Charging**: Integrated battery with nose-bridge charging pins connecting to "Mister Power" cradle

---

### 3. Brilliant Labs Monocle (Pocket AR Monocular Display)

Monocle is Brilliant Labs' open-source single-eye augmented reality display module with open hardware files in both parametric STEP and mesh STL formats.

| Asset | Format | File Path | Description |
| :--- | :--- | :--- | :--- |
| **Monocle Body (STEP)** | `.step` | [`hardware/monocle/monocle-body.step`](hardware/monocle/monocle-body.step) | Parametric 3D CAD model for precision engineering, CNC machining, or CAD modeling in SolidWorks / Fusion 360. |
| **Monocle Body (STL)** | `.stl` | [`hardware/monocle/monocle-body.stl`](hardware/monocle/monocle-body.stl) | Mesh 3D CAD model optimized for direct 3D printing. |
| **Monocle Schematics** | `.pdf` | [`hardware/monocle/monocle-schematics.pdf`](hardware/monocle/monocle-schematics.pdf) | Full mainboard schematic (nRF52840, Gowin FPGA, Micro-OLED driver, camera interface). |
| **Charging Case Schematics** | `.pdf` | [`hardware/monocle/monocle-cc-schematics.pdf`](hardware/monocle/monocle-cc-schematics.pdf) | Schematics for the portable clamshell charging case. |
| **Dimension Blueprint** | `.pdf` | [`hardware/monocle/monocle-dimensions.pdf`](hardware/monocle/monocle-dimensions.pdf) | Optical eye relief, field of view, and outer envelope dimensions. |
| **Case Dimension Blueprint**| `.pdf` | [`hardware/monocle/monocle-cc-dimensions.pdf`](hardware/monocle/monocle-cc-dimensions.pdf) | Mechanical drawing for the charging case pocket and spring contacts. |

---

### 4. 3D Printing & Fabrication Guidelines

* **Frame & Temple Arms**: Recommended fabrication via **SLS (Selective Laser Sintering)** with **Nylon PA12** or **MJF (Multi Jet Fusion)** for durability, lightness, and snap-fit flexural strength.
* **Prescription (Rx) Lens Clips**: Recommended fabrication via **SLA / DLP Resin** (e.g. Tough Resin or ABS-like) at 50-micron layer height to ensure precise clip tolerances without scratching optical lenses.
* **Charging Cradle ("Mister Power")**: Can be printed on standard FDM printers using **PETG** or **PLA+** (0.16mm–0.20mm layer height, 20% infill).
* **Tolerances**: Pogo-pin hole diameters and magnetic alignment pockets are modeled with +0.15mm clearance.

---

## Workspace Structure

```
├── hardware/                         # Mechanical 3D CAD (.stl / .step) & Electrical Schematics (.pdf)
│   ├── halo/
│   │   └── halo.stl                  # Halo full 3D assembly (front frame, lenses, temple arms)
│   ├── frame/
│   │   ├── frame.stl                 # Frame 3D CAD model
│   │   ├── charging-cradle.stl       # "Mister Power" charging cradle 3D CAD model
│   │   ├── frame-rx-clip.stl         # Prescription (Rx) clip insert 3D CAD model
│   │   ├── frame-schematics.pdf      # Frame mainboard electrical schematics
│   │   ├── charging-cradle-schematics.pdf # Charging cradle electrical schematics
│   │   ├── frame-mechanical-drawing.pdf
│   │   └── frame-lenses-mechanical-drawing.pdf
│   └── monocle/
│       ├── monocle-body.step         # Monocle STEP 3D CAD model
│       ├── monocle-body.stl          # Monocle STL 3D CAD model
│       ├── monocle-schematics.pdf    # Monocle electrical schematics
│       └── monocle-cc-schematics.pdf # Monocle charging case schematics
│
├── firmware/                         # Official device firmware and FPGA RTL
│   ├── frame-codebase/               # Nordic nRF52840 C firmware + Lattice CrossLink-NX FPGA RTL
│   └── halo-firmware/                # Zephyr RTOS on Alif Balletto B1 (Cortex-M55 + Ethos-U55 NPU)
│
├── sdk/                              # Unified Brilliant SDK (Halo & Frame monorepo)
│   ├── python/                       # brilliant-ble, brilliant-msg, brilliant-sdk, halo-emulator
│   ├── flutter/                      # Melos Flutter workspace for mobile apps
│   └── webbluetooth/                 # WebBluetooth / TypeScript libraries
│
├── apps/
│   └── noa-flutter/                  # Full official Noa companion app source code
│
├── docs/                             # Official documentation portal & API references
│
├── demo_screenshots/                 # Live simulator captures & HUD screenshots
│   └── web_simulator_dashboard.png   # Full web simulator dashboard screenshot
│
├── inventory_app/                    # Smart Glasses Inventory Management & Alert Application
│   ├── db.py                         # SQLite database with threshold alert trigger logic
│   ├── glasses_bridge.py             # BLE & Emulator bridge for Frame & Halo displays
│   ├── scanner_service.py            # Barcode/QR generator & optical camera scanner simulation
│   ├── main.py                       # FastAPI web server & live glasses HUD controller
│   ├── cli.py                        # Terminal CLI for warehouse operators & automated demo
│   ├── lua/
│   │   └── inventory_hud.lua         # On-device Lua HUD app for Frame & Halo
│   ├── static/
│   │   ├── current_hud.png           # Live rendered preview of the wearer's HUD display
│   │   └── barcodes/                 # Printable QR / Barcode labels for inventory SKUs
│   ├── templates/
│   │   └── index.html                # Modern web dashboard with live HUD viewport
│   └── tests/
│       └── test_inventory.py         # Automated unit test suite
│
└── .venv/                            # Configured Python virtual environment
```

---

## Quick Start: Running the Inventory & Alert System

### 1. Activate Environment
In PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Run the Interactive Web Dashboard
```powershell
.\.venv\Scripts\python.exe inventory_app\main.py
```
Open your browser to: **`http://127.0.0.1:8000`**

#### Web Dashboard Features:
* **Live Glasses HUD Viewport**: See exactly what the smart glasses wearer sees on their micro-OLED display in real time (`current_hud.png`).
* **Device Switcher**: Toggle between **Halo** (256×256 round color display) and **Frame** (640×400 rectangular display).
* **Virtual Glasses Input**: Simulate temple button / IMU tap gestures:
  * **Single Tap**: +1 Quantity Check-in or Acknowledge Alert.
  * **Double Tap**: -1 Quantity Check-out.
  * **Long Press**: Reset to Standby HUD.
* **Stock & Threshold Management**: View all managed SKUs, adjust quantities, generate printable QR codes.
* **Active Alert Engine**: Low-stock and out-of-stock items automatically generate critical alerts and can be beamed directly to the wearer's HUD.

---

### 3. Run the Terminal CLI & Automated Demo

#### Run End-to-End Automated Demonstration:
```powershell
.\.venv\Scripts\python.exe inventory_app\cli.py demo
```

#### List Current Inventory:
```powershell
.\.venv\Scripts\python.exe inventory_app\cli.py list
```

#### Scan an Item (Beams to Glasses HUD):
```powershell
.\.venv\Scripts\python.exe inventory_app\cli.py scan HALO-BLK-001
```

#### Adjust Stock:
```powershell
.\.venv\Scripts\python.exe inventory_app\cli.py adjust HALO-BLK-001 -1
```

#### View Active Alerts:
```powershell
.\.venv\Scripts\python.exe inventory_app\cli.py alerts
```

---

## Hardware Architecture Comparison

| Feature | Brilliant Labs Frame | Brilliant Labs Halo |
| :--- | :--- | :--- |
| **Compute SoC** | Nordic nRF52840 (Cortex-M4F) + Lattice FPGA | Alif Balletto B1 (Dual Cortex-M55 + Ethos-U55 NPU) |
| **OS / Runtime** | Custom C Firmware + Embedded Lua VM | Zephyr RTOS + Embedded Lua 5.4 VM |
| **Display** | 640×400 OLED; Double-buffered (`frame.display.show()` required) | 256×256 circular color OLEDoS; Direct draw |
| **Colors** | 16-color named palette (`WHITE`, `RED`, `GREEN`, `BLUE`, etc.) | Full 24-bit RGB hex (`0xRRGGBB`) |
| **Audio** | Single MEMS microphone | Dual MEMS mics + stereo bone conduction speakers |
| **Camera** | OmniVision OV09734 (cropped JPEG via FPGA) | PixArt global shutter VGA (`libmpix` pipeline) |
| **Inputs** | 3-axis IMU tap callback | Physical temple button + IMU tap callback |
| **CAD Formats** | STL (`hardware/frame/`) | STL (`hardware/halo/`) |
| **Schematics** | PDF (`hardware/frame/`) | Block diagrams & spec sheets (`docs/halo/`) |

---

## Running Automated Unit Tests
```powershell
.\.venv\Scripts\python.exe inventory_app\tests\test_inventory.py
```
