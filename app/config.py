import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "unhas-izin-monitor-secret-fallback")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:papua123@localhost:3306/aim_izinku"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload storage (outside public static for privacy & access control)
    EVIDENCE_UPLOAD_FOLDER = BASE_DIR / os.getenv("EVIDENCE_UPLOAD_FOLDER", "storage_evidences")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max request payload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
    
    # Office GPS Geofence & Radius
    OFFICE_LATITUDE = float(os.getenv("OFFICE_LATITUDE", "-5.230188"))
    OFFICE_LONGITUDE = float(os.getenv("OFFICE_LONGITUDE", "119.503378"))
    OFFICE_RADIUS_METERS = float(os.getenv("OFFICE_RADIUS_METERS", "500.0"))
    OFFICE_NAME = os.getenv("OFFICE_NAME", "Kampus Fakultas Teknik Unhas Gowa")
    
    # Dev bypass
    DEV_BYPASS_GPS_CHECK = os.getenv("DEV_BYPASS_GPS_CHECK", "false").lower() in ("true", "1", "yes")
    DEV_BYPASS_IP_CHECK = os.getenv("DEV_BYPASS_IP_CHECK", "false").lower() in ("true", "1", "yes")
