"""
inventory_app/scanner_service.py
Barcode & QR generation and image processing simulation for Frame & Halo camera feeds.
"""

import os
import qrcode
from typing import Optional, Dict, Any
from PIL import Image

BARCODES_DIR = os.path.join(os.path.dirname(__file__), "static", "barcodes")
os.makedirs(BARCODES_DIR, exist_ok=True)


def generate_qr_code(data: str, filename_prefix: str = "qr") -> str:
    """Generate a high-contrast QR code image for a given SKU/Barcode."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    safe_name = "".join([c if c.isalnum() or c in "-_" else "_" for c in data])
    filepath = os.path.join(BARCODES_DIR, f"{filename_prefix}_{safe_name}.png")
    img.save(filepath)
    return filepath


def generate_all_sample_barcodes() -> Dict[str, str]:
    """Generate QR code images for all seeded inventory items."""
    from db import get_all_items
    items = get_all_items()
    results = {}
    for item in items:
        path = generate_qr_code(item["sku"], "sku")
        results[item["sku"]] = os.path.basename(path)
    return results


def simulate_camera_scan(image_path_or_bytes) -> Optional[str]:
    """
    Simulates optical recognition of barcode / SKU from the glasses camera buffer.
    In production on Frame/Halo: The host receives cropped JPEG (Frame) or raw VGA (Halo)
    and passes it through a decoder.
    """
    # For simulation, we check if image filename or content matches an existing SKU
    from db import get_all_items
    items = get_all_items()
    if isinstance(image_path_or_bytes, str):
        basename = os.path.basename(image_path_or_bytes)
        for item in items:
            if item["sku"] in basename or item["barcode"] in basename:
                return item["sku"]
    return None


if __name__ == "__main__":
    generated = generate_all_sample_barcodes()
    print(f"Generated {len(generated)} sample barcode QR labels in {BARCODES_DIR}")

