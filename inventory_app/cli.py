"""
inventory_app/cli.py
Terminal CLI for Brilliant Labs Smart Glasses Inventory Management & Alert System
"""

import sys
import os
import argparse
import asyncio

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import db
from glasses_bridge import glasses


async def cmd_list():
    items = db.get_all_items()
    print("\n" + "=" * 80)
    print(f"{'SKU':<16} {'NAME':<30} {'QTY':<8} {'MIN':<6} {'STATUS':<12} {'LOCATION'}")
    print("-" * 80)
    for i in items:
        status = "CRITICAL" if i["quantity"] == 0 else ("LOW" if i["quantity"] <= i["min_threshold"] else "OK")
        print(f"{i['sku']:<16} {i['name'][:28]:<30} {i['quantity']:<8} {i['min_threshold']:<6} {status:<12} {i['location']}")
    print("=" * 80)
    summary = db.get_inventory_summary()
    print(f"Total: {summary['total_items']} | Out of Stock: {summary['out_of_stock']} | Low Stock: {summary['low_stock']} | Alerts: {summary['active_alerts_count']}\n")


async def cmd_alerts():
    alerts = db.get_active_alerts()
    print("\n" + "=" * 80)
    print("ACTIVE INVENTORY ALERTS")
    print("-" * 80)
    if not alerts:
        print("No active alerts.")
    else:
        for a in alerts:
            print(f"[{a['id']}] [{a['severity']}] {a['item_sku']} ({a['item_name']}) - {a['message']} | Loc: {a['location']}")
    print("=" * 80 + "\n")


async def cmd_scan(sku_or_barcode: str):
    await glasses.connect()
    item = db.get_item(sku_or_barcode)
    if not item:
        print(f"[-] No item found matching '{sku_or_barcode}'")
        return
    print(f"[+] Found item: {item['name']} (SKU: {item['sku']})")
    print(f"    Quantity : {item['quantity']} {item['unit']} (Min Threshold: {item['min_threshold']})")
    print(f"    Location : {item['location']}")
    print(f"[+] Beaming item card to {glasses.device_type.upper()} glasses HUD...")
    await glasses.display_item(item)
    print(f"[+] HUD Preview generated at: {glasses.preview_image_path}")


async def cmd_adjust(sku: str, delta: int):
    await glasses.connect()
    updated = db.update_stock(sku, delta, reason="CLI Adjustment")
    if not updated:
        print(f"[-] Item '{sku}' not found.")
        return
    print(f"[+] Stock updated for {updated['sku']}: New Qty = {updated['quantity']}")
    # Check if this triggered alert
    if updated['quantity'] <= updated['min_threshold']:
        print(f"[!] WARNING: Stock has reached or dropped below threshold ({updated['min_threshold']})!")
        alerts = db.get_active_alerts()
        for a in alerts:
            if a["item_sku"] == updated["sku"]:
                print(f"[!] Pushing alert to glasses HUD: {a['message']}")
                await glasses.display_alert(a)
                break
    else:
        await glasses.display_item(updated)


async def cmd_ack(alert_id: int):
    success = db.acknowledge_alert(alert_id)
    if success:
        print(f"[+] Alert {alert_id} acknowledged.")
        await glasses.display_standby(db.get_inventory_summary())
    else:
        print(f"[-] Alert {alert_id} not found.")


async def cmd_demo():
    print("\n=== STARTING AUTOMATED INVENTORY & ALERT SYSTEM DEMO ===")
    await glasses.connect()

    # 1. Standby
    print("\n[Step 1] Initializing Standby HUD...")
    await glasses.display_standby(db.get_inventory_summary())
    await asyncio.sleep(1.5)

    # 2. Scan an item
    target_sku = "HALO-BLK-001"
    print(f"\n[Step 2] Worker aims glasses at SKU: {target_sku}...")
    item = db.get_item(target_sku)
    await glasses.display_item(item)
    print(f"         HUD showing: {item['name']} (Stock: {item['quantity']})")
    await asyncio.sleep(2)

    # 3. Simulate Dispense / Pick (Double tap)
    print("\n[Step 3] Worker takes 1 item from shelf (Double tap check-out)...")
    updated = db.update_stock(target_sku, -1, reason="Pick order item")
    print(f"         New quantity: {updated['quantity']} (Min Threshold: {updated['min_threshold']})")
    await glasses.display_item(updated)
    await asyncio.sleep(2)

    # 4. Check alerts
    alerts = db.get_active_alerts()
    print(f"\n[Step 4] Checking Alert Engine... Found {len(alerts)} alerts.")
    low_alert = next((a for a in alerts if a["item_sku"] == target_sku), None)
    if low_alert:
        print(f"         [!] TRIGGERING HUD ALERT ON GLASSES: {low_alert['message']}")
        await glasses.display_alert(low_alert)
        await asyncio.sleep(2)

    # 5. Acknowledge and restock
    print("\n[Step 5] Worker taps temple button to acknowledge alert...")
    if low_alert:
        db.acknowledge_alert(low_alert["id"])
    print("         Restocking item (+5 pcs)...")
    restocked = db.update_stock(target_sku, 5, reason="Restock delivery")
    await glasses.display_item(restocked)
    await asyncio.sleep(1.5)

    # 6. Return to standby
    print("\n[Step 6] Returning glasses to Standby HUD...")
    await glasses.display_standby(db.get_inventory_summary())
    print("\n=== DEMO COMPLETED SUCCESSFULLY ===")
    print(f"Glasses HUD output saved to: {glasses.preview_image_path}\n")


def main():
    db.init_db()
    parser = argparse.ArgumentParser(description="Brilliant Labs Frame & Halo Inventory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    subparsers.add_parser("list", help="List all inventory items")
    subparsers.add_parser("alerts", help="List active inventory alerts")
    
    scan_parser = subparsers.add_parser("scan", help="Scan an item SKU or barcode")
    scan_parser.add_argument("sku", help="SKU code or barcode string")

    adjust_parser = subparsers.add_parser("adjust", help="Adjust stock quantity")
    adjust_parser.add_argument("sku", help="Item SKU")
    adjust_parser.add_argument("delta", type=int, help="Positive or negative quantity change")

    ack_parser = subparsers.add_parser("ack", help="Acknowledge alert by ID")
    ack_parser.add_argument("alert_id", type=int, help="Alert ID")

    subparsers.add_parser("demo", help="Run automated end-to-end demonstration")

    args = parser.parse_args()

    if args.command == "list":
        asyncio.run(cmd_list())
    elif args.command == "alerts":
        asyncio.run(cmd_alerts())
    elif args.command == "scan":
        asyncio.run(cmd_scan(args.sku))
    elif args.command == "adjust":
        asyncio.run(cmd_adjust(args.sku, args.delta))
    elif args.command == "ack":
        asyncio.run(cmd_ack(args.alert_id))
    elif args.command == "demo":
        asyncio.run(cmd_demo())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

