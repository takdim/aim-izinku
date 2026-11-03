import os
import uuid
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

def ensure_storage_dir():
    folder = Path(current_app.config["EVIDENCE_UPLOAD_FOLDER"])
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_and_compress_evidence(file_obj=None, base64_data=None, original_filename="bukti.jpg"):
    """
    Saves an evidence image, compressing it to target ~500 KB or less.
    Accepts either a Werkzeug FileStorage object or a data URI / base64 string.
    Returns (saved_filename, file_size_bytes, mime_type)
    """
    folder = ensure_storage_dir()
    unique_id = uuid.uuid4().hex[:12]
    out_filename = f"evd_{unique_id}.jpg"
    out_path = folder / out_filename

    image = None
    if base64_data:
        # Strip header if data URL
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
        decoded = base64.b64decode(base64_data)
        image = Image.open(BytesIO(decoded))
    elif file_obj:
        image = Image.open(file_obj)
    else:
        raise ValueError("Neither file_obj nor base64_data provided.")

    # Convert RGBA / Palette to RGB for JPEG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Resize if excessively large (e.g., > 1920 on longest edge)
    max_dim = 1600
    w, h = image.size
    if w > max_dim or h > max_dim:
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    # Compress iteratively to be under ~600 KB
    quality = 85
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    
    while buffer.tell() > 600 * 1024 and quality > 40:
        quality -= 10
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)

    with open(out_path, "wb") as f:
        f.write(buffer.getvalue())

    file_size = out_path.stat().st_size
    return out_filename, file_size, "image/jpeg"
