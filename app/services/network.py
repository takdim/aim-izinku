import ipaddress
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

def is_ip_in_office_network(ip_str=None):
    """
    Check if the IP is inside the configured office subnets.
    Supports IPv4, IPv6, CIDR blocks, and single IPs.
    """
    # Check dev bypass first
    bypass_setting = SystemSetting.query.filter_by(key="dev_bypass_ip_check").first()
    if bypass_setting and bypass_setting.value.lower() in ("true", "1", "yes"):
        return True, "Dev Mode Bypass Aktif"
    if current_app.config.get("DEV_BYPASS_IP_CHECK", False):
        return True, "Dev Mode Bypass Aktif"

    if not ip_str:
        ip_str = get_client_ip()

    # Get subnets from database or fallback to config
    subnet_setting = SystemSetting.query.filter_by(key="office_subnets").first()
    if subnet_setting and subnet_setting.value:
        allowed_list = [s.strip() for s in subnet_setting.value.split(",") if s.strip()]
    else:
        allowed_list = current_app.config.get("OFFICE_SUBNETS", ["127.0.0.1", "::1"])

    try:
        client_ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False, f"Format IP tidak valid ({ip_str})"

    # Handle IPv4-mapped IPv6 addresses (e.g., ::ffff:192.168.1.5)
    if isinstance(client_ip, ipaddress.IPv6Address) and client_ip.ipv4_mapped:
        client_ip = client_ip.ipv4_mapped

    for network_str in allowed_list:
        try:
            if "/" in network_str:
                network = ipaddress.ip_network(network_str, strict=False)
                if client_ip in network:
                    return True, f"Terhubung ke Subnet Kantor ({network_str})"
            else:
                target_ip = ipaddress.ip_address(network_str)
                if client_ip == target_ip:
                    return True, f"Terhubung ke Jaringan Kantor ({network_str})"
        except ValueError:
            continue

    return False, f"IP ({ip_str}) di luar jaringan kantor"
