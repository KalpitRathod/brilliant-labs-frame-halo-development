"""
inventory_app/glasses_bridge.py
Bluetooth Low Energy & Emulated Glasses Bridge for Frame & Halo.
"""

import asyncio
import os
import logging
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlassesBridge")


class GlassesBridge:
    def __init__(self, device_type: str = "halo", mode: str = "emulator"):
        """
        device_type: 'halo' (256x256 round) or 'frame' (640x400 double-buffered)
        mode: 'emulator' (uses halo_emulator/local simulation) or 'ble' (real hardware)
        """
        self.device_type = device_type.lower()
        self.mode = mode.lower()
        self.is_connected = False
        self.current_state = {
            "mode": "STANDBY",
            "title": "INVENTORY HUD",
            "lines": ["System Online", "Ready to scan items"],
            "status": "NORMAL",
            "accent_color": "#00D9FF"
        }
        self.ble_client = None
        self.emulator = None
        self.emu_msg = None
        self.preview_image_path = os.path.join(
            os.path.dirname(__file__), "static", "current_hud.png"
        )
        os.makedirs(os.path.dirname(self.preview_image_path), exist_ok=True)
        # Generate initial HUD image
        self.render_hud_preview()

    async def connect(self) -> bool:
        """Connect to either real BLE hardware or start emulator."""
        logger.info(f"Connecting to {self.device_type.upper()} in {self.mode.upper()} mode...")
        
        if self.mode == "emulator":
            try:
                from halo_emulator import HaloEmulator, EmulatorBrilliantMsg
                self.emulator = HaloEmulator()
                self.emu_msg = EmulatorBrilliantMsg(self.emulator)
                await self.emu_msg.connect()
                self.is_connected = True
                logger.info("Connected to Halo/Frame Emulator successfully.")
                await self.send_lua("frame.display.clear(0); print('EMU_READY')")
                self.render_hud_preview()
                return True
            except Exception as e:
                logger.warning(f"Emulator init failed ({e}), falling back to simulated bridge mode.")
                self.is_connected = True
                self.render_hud_preview()
                return True

        elif self.mode == "ble":
            try:
                if self.device_type == "halo":
                    from brilliant_ble import BrilliantBle
                    self.ble_client = BrilliantBle()
                    await self.ble_client.connect()
                else:
                    from frame_ble import FrameBle
                    self.ble_client = FrameBle()
                    await self.ble_client.connect()

                self.is_connected = True
                logger.info(f"Connected to physical {self.device_type.upper()} via BLE.")
                return True
            except Exception as e:
                logger.error(f"Failed to connect to physical glasses via BLE: {e}")
                self.is_connected = False
                return False
        
        return False

    async def disconnect(self) -> None:
        """Disconnect BLE or stop emulator."""
        if self.emu_msg:
            try:
                await self.emu_msg.disconnect()
            except Exception:
                pass
        if self.ble_client:
            try:
                await self.ble_client.disconnect()
            except Exception:
                pass
        self.is_connected = False
        logger.info("Glasses disconnected.")

    async def send_lua(self, lua_code: str) -> Optional[str]:
        """Send raw Lua string to the connected glasses."""
        if not self.is_connected:
            await self.connect()

        if self.mode == "emulator" and self.emu_msg:
            try:
                return await self.emu_msg.send_lua(lua_code)
            except Exception as e:
                logger.debug(f"Emulator send_lua note: {e}")
                return None
        elif self.mode == "ble" and self.ble_client:
            try:
                return await self.ble_client.send_lua(lua_code)
            except Exception as e:
                logger.error(f"BLE send_lua error: {e}")
                return None
        return None

    async def display_item(self, item: Dict[str, Any]) -> None:
        """Render scanned inventory item details on the glasses HUD."""
        sku = item.get("sku", "UNKNOWN")
        name = item.get("name", "Unknown Item")
        qty = item.get("quantity", 0)
        min_th = item.get("min_threshold", 5)
        loc = item.get("location", "Warehouse")

        is_critical = (qty == 0)
        is_warning = (0 < qty <= min_th)

        status_str = "OUT OF STOCK" if is_critical else ("LOW STOCK" if is_warning else "IN STOCK")
        accent_color = "#FF2222" if is_critical else ("#FFCC00" if is_warning else "#22DD44")

        self.current_state = {
            "mode": "ITEM_VIEW",
            "title": f"ITEM: {sku}",
            "lines": [
                name[:24],
                f"Qty: {qty} {item.get('unit', 'pcs')} (Min: {min_th})",
                f"Status: {status_str}",
                f"Loc: {loc}",
                "[Tap] +1 In  |  [2xTap] -1 Out"
            ],
            "status": status_str,
            "accent_color": accent_color,
            "item": item
        }

        # Build Lua command for the glasses
        if self.device_type == "halo":
            hex_color = 0xFF2222 if is_critical else (0xFFCC00 if is_warning else 0x22DD44)
            lua = f"""
            frame.display.clear(0);
            frame.display.rect(8, 12, 240, 30, 0x00D9FF, false);
            frame.display.text("ITEM SCAN", 65, 18, 0x00D9FF);
            frame.display.text("{sku}", 20, 52, 0xFFFF00);
            frame.display.text("{name[:18]}", 20, 78, 0xFFFFFF);
            frame.display.text("Qty: {qty} (Min: {min_th})", 20, 108, {hex_color});
            frame.display.text("Loc: {loc[:16]}", 20, 136, 0x00D9FF);
            frame.display.text("[Tap] +1  [2xTap] -1", 20, 180, 0x888888);
            """
        else: # Frame 640x400
            frame_color = "RED" if is_critical else ("YELLOW" if is_warning else "GREEN")
            lua = f"""
            frame.display.text("=== INVENTORY ITEM SCAN ===", 40, 30, {{color='BLUE'}});
            frame.display.text("SKU     : {sku}", 40, 70, {{color='YELLOW'}});
            frame.display.text("Name    : {name}", 40, 110, {{color='WHITE'}});
            frame.display.text("Quantity: {qty} (Min: {min_th}) - {status_str}", 40, 150, {{color='{frame_color}'}});
            frame.display.text("Location: {loc}", 40, 190, {{color='BLUE'}});
            frame.display.text("Actions : [Single Tap] +1 In Stock  |  [Double Tap] -1 Dispense", 40, 250, {{color='GREY'}});
            frame.display.show();
            """

        await self.send_lua(lua)
        self.render_hud_preview()

    async def display_alert(self, alert: Dict[str, Any]) -> None:
        """Render high-priority inventory alert on the glasses HUD."""
        severity = alert.get("severity", "WARNING").upper()
        sku = alert.get("item_sku", "N/A")
        msg = alert.get("message", "Inventory Alert")
        loc = alert.get("location", "Warehouse")
        qty = alert.get("quantity", 0)

        is_crit = (severity == "CRITICAL")
        accent = "#FF2222" if is_crit else "#FFCC00"

        self.current_state = {
            "mode": "ALERT",
            "title": f"!! {severity} ALERT !!",
            "lines": [
                f"SKU: {sku}",
                msg[:32],
                f"Remaining Stock: {qty}",
                f"Location: {loc}",
                "[Tap] Acknowledge Alert"
            ],
            "status": severity,
            "accent_color": accent,
            "alert": alert
        }

        if self.device_type == "halo":
            lua = f"""
            frame.display.clear(0);
            frame.display.rect(8, 10, 240, 32, 0xFF2222, true);
            frame.display.text("! {severity} ALERT !", 30, 18, 0x000000);
            frame.display.text("{sku}", 20, 52, 0xFFFF00);
            frame.display.text("Remaining: {qty}", 20, 80, 0xFF2222);
            frame.display.text("{loc[:18]}", 20, 108, 0x00D9FF);
            frame.display.text("[Tap] Acknowledge", 30, 175, 0x888888);
            if frame.sound then frame.sound(1000, 200) end
            """
        else:
            lua = f"""
            frame.display.text("*************************************************", 40, 30, {{color='RED'}});
            frame.display.text("           [!] {severity} INVENTORY ALERT [!]   ", 40, 60, {{color='RED'}});
            frame.display.text("*************************************************", 40, 90, {{color='RED'}});
            frame.display.text("Item SKU : {sku}", 50, 130, {{color='YELLOW'}});
            frame.display.text("Details  : {msg[:45]}", 50, 170, {{color='WHITE'}});
            frame.display.text("Location : {loc}", 50, 210, {{color='BLUE'}});
            frame.display.text("Controls : [Tap once] Acknowledge Alert", 50, 280, {{color='GREY'}});
            frame.display.show();
            """

        await self.send_lua(lua)
        self.render_hud_preview()

    async def display_standby(self, summary: Dict[str, Any]) -> None:
        """Render default standby HUD with total items and alert count."""
        tot = summary.get("total_items", 0)
        alerts_cnt = summary.get("active_alerts_count", 0)
        low_stk = summary.get("low_stock", 0)

        self.current_state = {
            "mode": "STANDBY",
            "title": "BRILLIANT INVENTORY",
            "lines": [
                "System: Online (BLE Connected)",
                f"Total Managed SKUs: {tot}",
                f"Active Alerts: {alerts_cnt}",
                f"Low Stock Items: {low_stk}",
                "Aim at Barcode / Item"
            ],
            "status": "NORMAL",
            "accent_color": "#00D9FF"
        }

        if self.device_type == "halo":
            lua = f"""
            frame.display.clear(0);
            frame.display.rect(8, 8, 240, 240, 0x444444, false);
            frame.display.text("INVENTORY HUD", 45, 25, 0x00D9FF);
            frame.display.text("System Online", 50, 65, 0xFFFFFF);
            frame.display.text("Total Items: {tot}", 35, 100, 0xFFFFFF);
            frame.display.text("Active Alerts: {alerts_cnt}", 30, 130, 0xFFFF00);
            frame.display.text("Aim to scan item", 40, 175, 0x888888);
            """
        else:
            lua = f"""
            frame.display.text("BRILLIANT INVENTORY HUD", 170, 50, {{color='BLUE'}});
            frame.display.text("System Online - Bluetooth BLE Connected", 130, 120, {{color='WHITE'}});
            frame.display.text("Total SKUs: {tot}   |   Active Alerts: {alerts_cnt}", 140, 170, {{color='YELLOW'}});
            frame.display.text("Ready to scan barcodes or receive alerts...", 130, 220, {{color='GREY'}});
            frame.display.show();
            """

        await self.send_lua(lua)
        self.render_hud_preview()

    def render_hud_preview(self) -> str:
        """
        Generate a photorealistic preview image of the smart glasses HUD viewport
        so the user can see on PC exactly what the glasses wearer sees!
        """
        if self.device_type == "halo":
            width, height = 256, 256
            img = Image.new("RGBA", (width, height), (10, 14, 20, 255))
            draw = ImageDraw.Draw(img)

            # Circular lens border simulation
            draw.ellipse((2, 2, width - 3, height - 3), outline=(40, 60, 80), width=2)

            # Header Banner
            accent = self.current_state.get("accent_color", "#00D9FF")
            mode = self.current_state.get("mode", "STANDBY")

            if mode == "ALERT":
                draw.rectangle((10, 14, width - 10, 44), fill=(220, 30, 30))
                draw.text((28, 22), self.current_state["title"], fill=(255, 255, 255))
            else:
                draw.rectangle((10, 14, width - 10, 40), outline=(0, 217, 255), width=1)
                draw.text((36, 20), self.current_state["title"], fill=(0, 217, 255))

            # Body Lines
            y_offset = 58
            for line in self.current_state.get("lines", []):
                fill_color = (255, 255, 255)
                if "SKU:" in line or "Total" in line:
                    fill_color = (255, 220, 50)
                elif "Qty:" in line or "Stock:" in line or "Alerts:" in line:
                    fill_color = (255, 120, 100) if "OUT" in line or "CRITICAL" in line else (50, 230, 100)
                elif "[" in line or "Aim" in line:
                    fill_color = (140, 150, 160)

                draw.text((20, y_offset), line, fill=fill_color)
                y_offset += 24

        else: # Frame 640x400 rectangular display
            width, height = 640, 400
            img = Image.new("RGBA", (width, height), (12, 16, 22, 255))
            draw = ImageDraw.Draw(img)

            # Glass bezel simulation
            draw.rectangle((4, 4, width - 5, height - 5), outline=(50, 70, 95), width=2)

            mode = self.current_state.get("mode", "STANDBY")
            title = self.current_state.get("title", "INVENTORY HUD")

            if mode == "ALERT":
                draw.rectangle((20, 20, width - 20, 70), fill=(200, 30, 30))
                draw.text((60, 35), title, fill=(255, 255, 255))
            else:
                draw.rectangle((20, 20, width - 20, 65), outline=(0, 217, 255), width=2)
                draw.text((50, 35), title, fill=(0, 217, 255))

            y_offset = 95
            for line in self.current_state.get("lines", []):
                fill_color = (240, 240, 245)
                if "SKU" in line:
                    fill_color = (255, 220, 50)
                elif "Qty" in line or "Remaining" in line:
                    fill_color = (255, 90, 90) if "0" in line else (70, 240, 120)
                elif "[" in line:
                    fill_color = (150, 165, 180)

                draw.text((45, y_offset), line, fill=fill_color)
                y_offset += 32

        img.save(self.preview_image_path, "PNG")
        return self.preview_image_path


# Global singleton instance for app
glasses = GlassesBridge(device_type="halo", mode="emulator")

