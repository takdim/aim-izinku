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
    
    # Office network IP ranges / subnets
    OFFICE_SUBNETS = [
        s.strip() for s in os.getenv("OFFICE_SUBNETS", "127.0.0.1,::1,10.15.22.0/24,192.168.0.0/16").split(",") if s.strip()
    ]
    
    # Dev bypass
    DEV_BYPASS_IP_CHECK = os.getenv("DEV_BYPASS_IP_CHECK", "false").lower() in ("true", "1", "yes")
