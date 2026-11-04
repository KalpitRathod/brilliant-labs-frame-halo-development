"""
inventory_app/main.py
FastAPI Server & Web Dashboard for Brilliant Labs Glasses Inventory Management
"""

import os
import sys
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure inventory_app directory is on sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import db
from glasses_bridge import glasses
from scanner_service import generate_qr_code, simulate_camera_scan


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    await glasses.connect()
    summary = db.get_inventory_summary()
    await glasses.display_standby(summary)
    yield
    await glasses.disconnect()


app = FastAPI(
    title="Brilliant Labs AR Glasses - Inventory & Alert System",
    lifespan=lifespan
)

# Mount static files
static_dir = os.path.join(APP_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Pydantic Request Models
class ItemCreate(BaseModel):
    sku: str
    name: str
    barcode: str
    category: str
    quantity: int
    min_threshold: int = 5
    unit: str = "pcs"
    location: str
    price: float = 0.0


class StockAdjust(BaseModel):
    delta: int
    reason: str = "Manual Adjustment"


class DeviceConfig(BaseModel):
    device_type: str  # 'halo' or 'frame'
    mode: str         # 'emulator' or 'ble'




@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_html_path = os.path.join(APP_DIR, "templates", "index.html")
    if os.path.exists(dashboard_html_path):
        with open(dashboard_html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard Template Missing</h1>", status_code=500)


# --- REST API: INVENTORY ---

@app.get("/api/items")
async def list_items():
    return db.get_all_items()


@app.get("/api/items/{sku}")
async def get_item(sku: str):
    item = db.get_item(sku)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/api/items")
async def create_item(payload: ItemCreate):
    try:
        new_item = db.add_item(
            sku=payload.sku,
            name=payload.name,
            barcode=payload.barcode,
            category=payload.category,
            quantity=payload.quantity,
            min_threshold=payload.min_threshold,
            location=payload.location,
            unit=payload.unit,
            price=payload.price
        )
        generate_qr_code(new_item["sku"], "sku")
        return new_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/items/{sku}/adjust")
async def adjust_stock(sku: str, payload: StockAdjust):
    updated = db.update_stock(sku, payload.delta, payload.reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # If the item currently shown on the glasses HUD is this one, update the HUD
    if glasses.current_state.get("mode") == "ITEM_VIEW":
        curr_sku = glasses.current_state.get("item", {}).get("sku")
        if curr_sku and curr_sku.upper() == sku.upper():
            await glasses.display_item(updated)
            
    return updated


# --- REST API: ALERTS ---

@app.get("/api/alerts")
async def list_alerts():
    return db.get_active_alerts()


@app.post("/api/alerts/{alert_id}/acknowledge")
async def ack_alert(alert_id: int):
    success = db.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update HUD if alert was being displayed
    if glasses.current_state.get("mode") == "ALERT":
        summary = db.get_inventory_summary()
        await glasses.display_standby(summary)
        
    return {"status": "acknowledged", "alert_id": alert_id}


# --- REST API: GLASSES & HUD CONTROL ---

@app.get("/api/glasses/status")
async def glasses_status():
    summary = db.get_inventory_summary()
    return {
        "device_type": glasses.device_type,
        "mode": glasses.mode,
        "is_connected": glasses.is_connected,
        "current_hud_state": glasses.current_state,
        "summary": summary
    }


@app.post("/api/glasses/scan")
async def trigger_scan(sku_or_barcode: str = Form(...)):
    item = db.get_item(sku_or_barcode)
    if not item:
        raise HTTPException(status_code=404, detail=f"No item matches '{sku_or_barcode}'")
    await glasses.display_item(item)
    return {"status": "displayed", "item": item}


@app.post("/api/glasses/alert")
async def trigger_alert_hud(alert_id: int = Form(...)):
    alerts = db.get_active_alerts()
    match = next((a for a in alerts if a["id"] == alert_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Active alert not found")
    await glasses.display_alert(match)
    return {"status": "displayed", "alert": match}


@app.post("/api/glasses/standby")
async def trigger_standby():
    summary = db.get_inventory_summary()
    await glasses.display_standby(summary)
    return {"status": "standby_displayed"}


@app.post("/api/glasses/config")
async def config_glasses(config: DeviceConfig):
    await glasses.disconnect()
    glasses.device_type = config.device_type.lower()
    glasses.mode = config.mode.lower()
    await glasses.connect()
    summary = db.get_inventory_summary()
    await glasses.display_standby(summary)
    return {"status": "configured", "device_type": glasses.device_type, "mode": glasses.mode}


@app.post("/api/glasses/tap")
async def handle_tap(gesture: str = Form(...)):
    """
    Simulate or handle glasses gestures:
    - 'single': +1 quantity check-in (or acknowledge alert)
    - 'double': -1 quantity check-out
    - 'long': reset to standby
    """
    mode = glasses.current_state.get("mode")

    if mode == "ALERT":
        alert = glasses.current_state.get("alert")
        if alert and "id" in alert:
            db.acknowledge_alert(alert["id"])
        summary = db.get_inventory_summary()
        await glasses.display_standby(summary)
        return {"action": "alert_acknowledged"}

    elif mode == "ITEM_VIEW":
        item = glasses.current_state.get("item")
        if not item:
            return {"action": "no_item"}
        sku = item["sku"]

        if gesture == "single":
            updated = db.update_stock(sku, delta=1, reason="Glasses Tap (+1 Check-in)")
            await glasses.display_item(updated) # type: ignore
            return {"action": "stock_incremented", "new_qty": updated["quantity"]} # type: ignore
        elif gesture == "double":
            updated = db.update_stock(sku, delta=-1, reason="Glasses Tap (-1 Check-out)")
            await glasses.display_item(updated) # type: ignore
            return {"action": "stock_decremented", "new_qty": updated["quantity"]} # type: ignore

    summary = db.get_inventory_summary()
    await glasses.display_standby(summary)
    return {"action": "reset_to_standby"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, app_dir=APP_DIR)

