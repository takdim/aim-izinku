from datetime import datetime, date, time
from app.models import db, LeaveRequest, Notification, Extension, AuditLog

def check_and_update_leave_statuses(app=None):
    """
    Periodically checks leave requests to update status:
    1. 'disetujui' -> 'sedang_di_luar' if today and current time >= jam_pergi
    2. 'sedang_di_luar' -> 'terlambat_kembali' if today and current time > jam_pulang_rencana (or approved extension)
    """
    if app:
        with app.app_context():
            _run_status_update()
    else:
        _run_status_update()

def _run_status_update():
    now = datetime.now()
    today = now.date()
    current_time = now.time()

    # 1. Update disetujui -> sedang_di_luar
    pending_departure = LeaveRequest.query.filter(
        LeaveRequest.status == "disetujui",
        LeaveRequest.kategori == "keluar_sementara",
        LeaveRequest.tanggal_mulai <= today,
        LeaveRequest.jam_pergi <= current_time
    ).all()

    for req in pending_departure:
        # Check if already past planned return time
        target_return = req.jam_pulang_rencana
        # Check approved extension
        approved_ext = Extension.query.filter_by(request_id=req.id, status="disetujui").order_by(Extension.id.desc()).first()
        if approved_ext:
            target_return = approved_ext.jam_pulang_baru

        if target_return and current_time > target_return:
            req.status = "terlambat_kembali"
            # Send notification
            notif = Notification(
                user_id=req.user_id,
                judul="Peringatan Keterlambatan",
                pesan=f"Izin keluar Anda (#{req.nomor_tiket}) telah melewati batas waktu ({target_return.strftime('%H:%M')}). Segera kembali dan unggah bukti kehadiran.",
                tipe="error",
                link=f"/pegawai/penyelesaian/{req.id}"
            )
            db.session.add(notif)
        else:
            req.status = "sedang_di_luar"
            notif = Notification(
                user_id=req.user_id,
                judul="Izin Keluar Aktif",
                pesan=f"Izin keluar #{req.nomor_tiket} sedang aktif. Jangan lupa kembali sebelum pukul {target_return.strftime('%H:%M') if target_return else '-'}.",
                tipe="info",
                link=f"/pegawai/penyelesaian/{req.id}"
            )
            db.session.add(notif)

    # 2. Update sedang_di_luar -> terlambat_kembali
    active_outside = LeaveRequest.query.filter(
        LeaveRequest.status == "sedang_di_luar",
        LeaveRequest.kategori == "keluar_sementara"
    ).all()

    for req in active_outside:
        target_return = req.jam_pulang_rencana
        approved_ext = Extension.query.filter_by(request_id=req.id, status="disetujui").order_by(Extension.id.desc()).first()
        if approved_ext:
            target_return = approved_ext.jam_pulang_baru

        if target_return and (today > req.tanggal_selesai or (today == req.tanggal_selesai and current_time > target_return)):
            req.status = "terlambat_kembali"
            notif = Notification(
                user_id=req.user_id,
                judul="Batas Waktu Izin Terlewati",
                pesan=f"Izin #{req.nomor_tiket} telah melewati batas waktu ({target_return.strftime('%H:%M')}). Segera konfirmasi kepulangan dan unggah bukti presensi.",
                tipe="error",
                link=f"/pegawai/penyelesaian/{req.id}"
            )
            db.session.add(notif)
            
            # Notify Atasan if exists
            if req.pegawai and req.pegawai.atasan_id:
                notif_atasan = Notification(
                    user_id=req.pegawai.atasan_id,
                    judul="Pegawai Terlambat Kembali",
                    pesan=f"{req.pegawai.nama} belum kembali dari izin keluar #{req.nomor_tiket} (Batas: {target_return.strftime('%H:%M')}).",
                    tipe="warning",
                    link=f"/atasan/detail/{req.id}"
                )
                db.session.add(notif_atasan)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    # 3. Cleanup expired evidence files (PRD Section 8 Rule 4 & Section 14)
    _cleanup_expired_evidences()

def _cleanup_expired_evidences():
    """
    Deletes physical evidence image files older than the configured retention period
    (default: 365 days) from disk, while keeping the leave request history and recap intact.
    """
    import os
    from pathlib import Path
    from flask import current_app
    from app.models import SystemSetting, Evidence

    retention_setting = SystemSetting.query.filter_by(key="masa_simpan_bukti").first()
    try:
        days = int(retention_setting.value) if retention_setting and retention_setting.value else 365
    except ValueError:
        days = 365

    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)

    expired_evidences = Evidence.query.filter(Evidence.waktu_unggah_server < cutoff).all()
    storage_dir = Path(current_app.config["EVIDENCE_UPLOAD_FOLDER"])

    for evd in expired_evidences:
        file_path = storage_dir / evd.filename
        if file_path.exists():
            try:
                os.remove(file_path)
            except OSError:
                pass
        # Remove evidence database record or mark archived
        db.session.delete(evd)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
