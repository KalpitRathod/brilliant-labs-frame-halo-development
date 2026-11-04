"""
inventory_app/tests/test_inventory.py
Unit tests for database, alert logic, and glasses bridge.
"""

import sys
import os
import unittest
import asyncio

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import db
from glasses_bridge import GlassesBridge


class TestInventorySystem(unittest.TestCase):
    def setUp(self):
        db.init_db()

    def test_database_items_loaded(self):
        items = db.get_all_items()
        self.assertGreaterEqual(len(items), 5)
        item = db.get_item("FRM-BLK-001")
        self.assertIsNotNone(item)
        self.assertEqual(item["sku"], "FRM-BLK-001")

    def test_stock_adjustment_and_alert_trigger(self):
        # Pick an item and reduce its quantity to 0 to trigger OUT_OF_STOCK
        sku = "ALIF-B1-SOC"
        item = db.get_item(sku)
        orig_qty = item["quantity"]

        # Reduce to 0
        updated = db.update_stock(sku, -orig_qty, reason="Testing OOS Alert")
        self.assertEqual(updated["quantity"], 0)

        alerts = db.get_active_alerts()
        oos_alerts = [a for a in alerts if a["item_sku"] == sku and a["alert_type"] == "OUT_OF_STOCK"]
        self.assertGreaterEqual(len(oos_alerts), 1)

        # Restore stock
        db.update_stock(sku, orig_qty, reason="Restore after test")

    def test_glasses_bridge_preview_generation(self):
        async def run_bridge_test():
            bridge = GlassesBridge(device_type="halo", mode="emulator")
            item = db.get_item("FRM-BLK-001")
            await bridge.display_item(item)
            self.assertTrue(os.path.exists(bridge.preview_image_path))

            summary = db.get_inventory_summary()
            await bridge.display_standby(summary)
            self.assertTrue(os.path.exists(bridge.preview_image_path))

        asyncio.run(run_bridge_test())


if __name__ == "__main__":
    unittest.main()

