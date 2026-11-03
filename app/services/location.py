import math
from flask import request, current_app
from app.models import SystemSetting

def get_client_ip():
    """Get real client IP respecting proxies."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        ip = request.headers.get("X-Real-IP").strip()
    else:
        ip = request.remote_addr or "127.0.0.1"
    return ip

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate geodesic distance between two GPS coordinates using Haversine formula.
    Returns distance in meters.
    """
    R = 6371000.0  # Earth's radius in meters
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def get_office_geofence():
    """
    Retrieve configured office GPS coordinates and tolerance radius.
    Defaults to Fakultas Teknik Universitas Hasanuddin (Kampus Gowa).
    """
    lat_setting = SystemSetting.query.filter_by(key="office_latitude").first()
    lon_setting = SystemSetting.query.filter_by(key="office_longitude").first()
    radius_setting = SystemSetting.query.filter_by(key="office_radius_meters").first()
    name_setting = SystemSetting.query.filter_by(key="office_name").first()

    default_lat = float(current_app.config.get("OFFICE_LATITUDE", -5.230188))
    default_lon = float(current_app.config.get("OFFICE_LONGITUDE", 119.503378))
    default_radius = float(current_app.config.get("OFFICE_RADIUS_METERS", 500.0))
    default_name = current_app.config.get("OFFICE_NAME", "Kampus Fakultas Teknik Unhas Gowa")

    try:
        lat = float(lat_setting.value) if lat_setting and lat_setting.value else default_lat
    except ValueError:
        lat = default_lat

    try:
        lon = float(lon_setting.value) if lon_setting and lon_setting.value else default_lon
    except ValueError:
        lon = default_lon

    try:
        radius = float(radius_setting.value) if radius_setting and radius_setting.value else default_radius
    except ValueError:
        radius = default_radius

    name = name_setting.value if name_setting and name_setting.value else default_name

    return {
        "latitude": lat,
        "longitude": lon,
        "radius_meters": radius,
        "name": name
    }

def is_gps_within_office(user_lat, user_lon):
    """
    Check if the user's GPS coordinates are within the office radius.
    Returns: (is_valid: bool, distance_meters: float, message: str, office_info: dict)
    """
    office_info = get_office_geofence()

    # Check dev bypass first
    bypass_setting = SystemSetting.query.filter_by(key="dev_bypass_gps_check").first()
    if bypass_setting and bypass_setting.value.lower() in ("true", "1", "yes"):
        return True, 0.0, "Mode Dev: Bypass Geofence GPS Aktif (Bebas Lokasi)", office_info
    if current_app.config.get("DEV_BYPASS_GPS_CHECK", False):
        return True, 0.0, "Mode Dev: Bypass Geofence GPS Aktif (Bebas Lokasi)", office_info

    if user_lat is None or user_lon is None:
        return False, 0.0, "Koordinat GPS belum terdeteksi. Aktifkan GPS dan izinkan akses lokasi pada browser.", office_info

    try:
        u_lat = float(user_lat)
        u_lon = float(user_lon)
    except (ValueError, TypeError):
        return False, 0.0, "Format koordinat GPS tidak valid.", office_info

    distance = calculate_haversine_distance(
        u_lat, u_lon,
        office_info["latitude"], office_info["longitude"]
    )

    radius = office_info["radius_meters"]
    if distance <= radius:
        return True, distance, f"Lokasi Terverifikasi ({int(distance)} meter dari titik pusat, batas radius {int(radius)} meter)", office_info
    else:
        diff = int(distance - radius)
        return False, distance, f"Di Luar Radius Kantor ({int(distance)} meter dari titik pusat, melewati batas radius {diff} meter)", office_info

