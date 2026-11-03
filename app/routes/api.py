from datetime import date
from pathlib import Path
from flask import Blueprint, jsonify, send_from_directory, abort, current_app, request
from flask_login import login_required, current_user
from app.models import db, LeaveRequest, Evidence, Notification, Approval, User
from app.services.location import get_client_ip, is_gps_within_office, get_office_geofence
from app.services.scheduler import check_and_update_leave_statuses

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/atasan/persetujuan-data")
@login_required
def atasan_persetujuan_data():
    if not current_user.is_atasan:
        abort(403)
        
    check_and_update_leave_statuses()
    dept = request.args.get("dept", "all")
    cat = request.args.get("cat", "all")
    q = request.args.get("q", "").strip()

    query = LeaveRequest.query.filter_by(status="diajukan")

    if q:
        query = query.join(User).filter(
            (User.nama.ilike(f"%{q}%")) |
            (User.nip.ilike(f"%{q}%")) |
            (LeaveRequest.nomor_tiket.ilike(f"%{q}%"))
        )

    if dept != "all":
        query = query.join(User).filter(User.unit.ilike(f"%{dept}%"))

    if cat != "all":
        query = query.filter(LeaveRequest.kategori == cat)

    pending_requests = query.order_by(LeaveRequest.created_at.asc()).all()

    pending_total = LeaveRequest.query.filter_by(status="diajukan").count()
    approved_today = Approval.query.filter(
        Approval.keputusan == "disetujui",
        db.func.date(Approval.waktu) == date.today()
    ).count()
    rejected_today = Approval.query.filter(
        Approval.keputusan == "ditolak",
        db.func.date(Approval.waktu) == date.today()
    ).count()
    outside_total = LeaveRequest.query.filter(LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"])).count()
    unread_notifs = Notification.query.filter_by(user_id=current_user.id, dibaca=False).count()

    items = []
    for r in pending_requests:
        items.append({
            "id": r.id,
            "nomor_tiket": r.nomor_tiket,
            "pegawai_nama": r.pegawai.nama,
            "pegawai_nip": r.pegawai.nip,
            "pegawai_unit": r.pegawai.unit,
            "leave_type_nama": r.leave_type.nama,
            "tanggal_mulai": r.tanggal_mulai.strftime("%d %b %Y"),
            "alasan": r.alasan,
            "tujuan": r.tujuan or "",
            "kategori": r.kategori,
            "jam_pergi": r.jam_pergi.strftime("%H:%M") if r.jam_pergi else "-",
            "jam_pulang_rencana": r.jam_pulang_rencana.strftime("%H:%M") if r.jam_pulang_rencana else "-"
        })

    return jsonify({
        "pending_total": pending_total,
        "approved_today": approved_today,
        "rejected_today": rejected_today,
        "outside_total": outside_total,
        "unread_notifs": unread_notifs,
        "items": items
    })

@api_bp.route("/check-location", methods=["GET", "POST"])
def check_location():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        lat = data.get("latitude") or data.get("lat")
        lon = data.get("longitude") or data.get("lon") or data.get("lng")
    else:
        lat = request.args.get("latitude") or request.args.get("lat")
        lon = request.args.get("longitude") or request.args.get("lon") or request.args.get("lng")

    is_valid, distance, msg, office = is_gps_within_office(lat, lon)
    return jsonify({
        "in_radius": is_valid,
        "distance_meters": round(distance, 1),
        "message": msg,
        "office": office,
        "user_coords": {"latitude": lat, "longitude": lon}
    })

@api_bp.route("/check-ip")
def check_ip():
    client_ip = get_client_ip()
    office = get_office_geofence()
    return jsonify({
        "ip": client_ip,
        "office_geofence": office
    })

@api_bp.route("/monitoring-status")
@login_required
def monitoring_status():
    check_and_update_leave_statuses()
    
    outside_requests = LeaveRequest.query.filter(
        LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"])
    ).order_by(LeaveRequest.jam_pulang_rencana.asc()).all()

    items = []
    for r in outside_requests:
        items.append({
            "id": r.id,
            "nomor_tiket": r.nomor_tiket,
            "nama": r.pegawai.nama,
            "nip": r.pegawai.nip,
            "unit": r.pegawai.unit,
            "tujuan": r.tujuan,
            "alasan": r.alasan,
            "jam_pergi": r.jam_pergi.strftime("%H:%M") if r.jam_pergi else "-",
            "jam_pulang": r.jam_pulang_rencana.strftime("%H:%M") if r.jam_pulang_rencana else "-",
            "status": r.status
        })

    return jsonify({
        "count_outside": LeaveRequest.query.filter_by(status="sedang_di_luar").count(),
        "count_late": LeaveRequest.query.filter_by(status="terlambat_kembali").count(),
        "count_pending": LeaveRequest.query.filter_by(status="diajukan").count(),
        "items": items
    })

@api_bp.route("/notifications/unread")
@login_required
def unread_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id, dibaca=False)\
        .order_by(Notification.created_at.desc()).limit(10).all()

    pending_count = 0
    if current_user.is_atasan:
        pending_count = LeaveRequest.query.filter_by(status="diajukan").count()

    return jsonify({
        "count": len(notifs),
        "pending_count": pending_count,
        "notifications": [{
            "id": n.id,
            "judul": n.judul,
            "pesan": n.pesan,
            "link": n.link,
            "tipe": n.tipe,
            "time": n.created_at.strftime("%H:%M")
        } for n in notifs]
    })

@api_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def read_all_notifications():
    Notification.query.filter_by(user_id=current_user.id, dibaca=False).update({"dibaca": True})
    db.session.commit()
    return jsonify({"success": True})

@api_bp.route("/evidence/view/<filename>")
@login_required
def view_evidence_file(filename):
    """
    Secure evidence viewer: verifies login and role before streaming.
    Only the employee, atasan, or an admin can view the photo.
    """
    evidence = Evidence.query.filter_by(filename=filename).first_or_404()
    req = evidence.request

    # Access control: requester, their supervisor / any atasan in jurisdiction, or admin
    if not (current_user.is_admin or current_user.is_atasan or current_user.id == req.user_id):
        abort(403)

    storage_dir = Path(current_app.config["EVIDENCE_UPLOAD_FOLDER"])
    target_path = storage_dir / filename
    if not target_path.is_file():
        abort(404)

    return send_from_directory(storage_dir, filename)
