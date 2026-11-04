"""
inventory_app/db.py
SQLite Database & Alert Logic for Brilliant Labs Frame & Halo Inventory Management
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed_sample_data: bool = True) -> None:
    """Initialize database tables and seed sample data if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                barcode TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                min_threshold INTEGER NOT NULL DEFAULT 5,
                unit TEXT NOT NULL DEFAULT 'units',
                location TEXT NOT NULL,
                price REAL NOT NULL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Alerts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_sku TEXT NOT NULL,
                alert_type TEXT NOT NULL,  -- 'LOW_STOCK', 'OUT_OF_STOCK', 'RESTOCK_REQUIRED', 'PICK_ORDER'
                severity TEXT NOT NULL,    -- 'CRITICAL', 'WARNING', 'INFO'
                message TEXT NOT NULL,
                is_acknowledged BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_sku) REFERENCES items (sku)
            )
        """)

        # Transactions Audit Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_sku TEXT NOT NULL,
                delta_quantity INTEGER NOT NULL,
                new_quantity INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_sku) REFERENCES items (sku)
            )
        """)

        conn.commit()

        # Seed sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]

        if count == 0 and seed_sample_data:
            sample_items = [
                ("FRM-BLK-001", "Brilliant Frame (Smokey Black)", "85004400101", "Eyewear", 12, 5, "pcs", "Aisle 1 - Bay A1", 349.00),
                ("HALO-BLK-001", "Brilliant Halo AI Glasses", "85004400102", "Eyewear", 3, 5, "pcs", "Aisle 1 - Bay A2", 299.00),
                ("PWR-CRD-001", "Mister Power Charging Cradle", "85004400201", "Accessories", 2, 4, "pcs", "Aisle 2 - Shelf B1", 49.00),
                ("RX-CLIP-001", "Prescription Rx Clip-On Insert", "85004400202", "Accessories", 18, 6, "pcs", "Aisle 2 - Shelf B2", 39.00),
                ("OLED-SONY-01", "Micro-OLED Display 640x400", "85004400301", "Components", 0, 10, "units", "Component Bin C-04", 85.00),
                ("BAT-LIPO-180", "180mAh Li-Po Frame Battery", "85004400302", "Components", 4, 8, "units", "Battery Safe B-01", 12.50),
                ("CAM-OV9734-1", "OmniVision OV9734 Camera Sensor", "85004400303", "Components", 25, 10, "units", "Cleanroom Box D-12", 24.00),
                ("ALIF-B1-SOC", "Alif Balletto B1 Dual Cortex-M55", "85004400304", "Components", 15, 10, "units", "Cleanroom Box D-15", 35.00)
            ]
            cursor.executemany("""
                INSERT INTO items (sku, name, barcode, category, quantity, min_threshold, unit, location, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_items)
            conn.commit()

            # Trigger initial alerts check
            check_and_generate_alerts()


def get_all_items() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY quantity ASC, name ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_item(sku_or_barcode: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items 
            WHERE UPPER(sku) = UPPER(?) OR barcode = ?
        """, (sku_or_barcode.strip(), sku_or_barcode.strip()))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_stock(sku_or_barcode: str, delta: int, reason: str = "Manual Adjustment") -> Optional[Dict[str, Any]]:
    """Update stock quantity and record audit log and check alerts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items 
            WHERE UPPER(sku) = UPPER(?) OR barcode = ?
        """, (sku_or_barcode.strip(), sku_or_barcode.strip()))
        item = cursor.fetchone()
        if not item:
            return None

        current_qty = item["quantity"]
        new_qty = max(0, current_qty + delta)
        sku = item["sku"]

        cursor.execute("""
            UPDATE items 
            SET quantity = ?, last_updated = CURRENT_TIMESTAMP
            WHERE sku = ?
        """, (new_qty, sku))

        cursor.execute("""
            INSERT INTO inventory_logs (item_sku, delta_quantity, new_quantity, reason)
            VALUES (?, ?, ?, ?)
        """, (sku, delta, new_qty, reason))

        conn.commit()

    check_and_generate_alerts()
    return get_item(sku)


def add_item(sku: str, name: str, barcode: str, category: str, quantity: int, min_threshold: int, location: str, unit: str = "pcs", price: float = 0.0) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (sku, name, barcode, category, quantity, min_threshold, unit, location, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sku.strip().upper(), name.strip(), barcode.strip(), category.strip(), quantity, min_threshold, unit, location.strip(), price))
        conn.commit()

    check_and_generate_alerts()
    return get_item(sku) # type: ignore


def check_and_generate_alerts() -> List[Dict[str, Any]]:
    """Scan inventory items and generate alerts if stock is zero or below min_threshold."""
    generated_alerts = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()

        for item in items:
            sku = item["sku"]
            qty = item["quantity"]
            threshold = item["min_threshold"]
            name = item["name"]

            if qty == 0:
                # Check if active unacknowledged alert already exists
                cursor.execute("""
                    SELECT id FROM alerts 
                    WHERE item_sku = ? AND alert_type = 'OUT_OF_STOCK' AND is_acknowledged = 0
                """, (sku,))
                if not cursor.fetchone():
                    msg = f"CRITICAL: '{name}' (SKU: {sku}) is completely OUT OF STOCK!"
                    cursor.execute("""
                        INSERT INTO alerts (item_sku, alert_type, severity, message)
                        VALUES (?, 'OUT_OF_STOCK', 'CRITICAL', ?)
                    """, (sku, msg))
                    generated_alerts.append({"sku": sku, "type": "OUT_OF_STOCK", "msg": msg})

            elif qty <= threshold:
                cursor.execute("""
                    SELECT id FROM alerts 
                    WHERE item_sku = ? AND alert_type = 'LOW_STOCK' AND is_acknowledged = 0
                """, (sku,))
                if not cursor.fetchone():
                    msg = f"WARNING: '{name}' is LOW IN STOCK ({qty} left, min: {threshold})."
                    cursor.execute("""
                        INSERT INTO alerts (item_sku, alert_type, severity, message)
                        VALUES (?, 'LOW_STOCK', 'WARNING', ?)
                    """, (sku, msg))
                    generated_alerts.append({"sku": sku, "type": "LOW_STOCK", "msg": msg})

        conn.commit()
    return generated_alerts


def get_active_alerts() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, i.name as item_name, i.quantity, i.min_threshold, i.location
            FROM alerts a
            JOIN items i ON a.item_sku = i.sku
            WHERE a.is_acknowledged = 0
            ORDER BY CASE a.severity WHEN 'CRITICAL' THEN 1 WHEN 'WARNING' THEN 2 ELSE 3 END,
                     a.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def acknowledge_alert(alert_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET is_acknowledged = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_inventory_summary() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        total_items = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM items WHERE quantity = 0")
        out_of_stock = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM items WHERE quantity > 0 AND quantity <= min_threshold")
        low_stock = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_acknowledged = 0")
        active_alerts_count = cursor.fetchone()[0]

        return {
            "total_items": total_items,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "healthy_stock": total_items - (out_of_stock + low_stock),
            "active_alerts_count": active_alerts_count
        }


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print("Summary:", get_inventory_summary())
    print("Active Alerts:", len(get_active_alerts()))

