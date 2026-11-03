import csv
from io import StringIO
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_login import login_required, current_user
from app.models import (
    db, LeaveRequest, User, Approval, Evidence, Extension, ExceptionRequest,
    Notification, AuditLog
)
from app.services.network import get_client_ip
from app.services.scheduler import check_and_update_leave_statuses

atasan_bp = Blueprint("atasan", __name__, url_prefix="/atasan")

def check_atasan_permission():
    if not current_user.is_authenticated or not current_user.is_atasan:
        flash("Hanya Pimpinan / Atasan yang berwenang mengakses halaman ini.", "error")
        return False
    return True

@atasan_bp.before_request
def restrict_access():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if not current_user.is_atasan:
        flash("Akses ditolak: Anda tidak memiliki hak akses pimpinan.", "error")
        return redirect(url_for("pegawai.beranda"))

@atasan_bp.route("/dashboard")
def dashboard():
    check_and_update_leave_statuses()
    today = date.today()

    # Scope subordinates: if admin, can view all. If atasan, subordinates or all FT.
    subordinate_ids = [u.id for u in current_user.bawahan.all()]
    if current_user.is_admin or not subordinate_ids:
        # Fallback to all if dean or demo
        base_query = LeaveRequest.query
    else:
        base_query = LeaveRequest.query.filter(LeaveRequest.user_id.in_(subordinate_ids))

    # 4 KPI cards
    harian_count = base_query.filter(
        LeaveRequest.kategori == "harian",
        LeaveRequest.status.in_(["disetujui", "sedang_di_luar"]),
        LeaveRequest.tanggal_mulai <= today,
        LeaveRequest.tanggal_selesai >= today
    ).count()

    outside_count = base_query.filter(
        LeaveRequest.kategori == "keluar_sementara",
        LeaveRequest.status == "sedang_di_luar"
    ).count()

    late_count = base_query.filter(
        LeaveRequest.kategori == "keluar_sementara",
        LeaveRequest.status == "terlambat_kembali"
    ).count()

    pending_count = base_query.filter(
        LeaveRequest.status == "diajukan"
    ).count()

    # Active outside list
    outside_list = base_query.filter(
        LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"])
    ).order_by(LeaveRequest.jam_pulang_rencana.asc()).all()

    # Pending approvals (limit 5 for dashboard)
    pending_list = base_query.filter_by(status="diajukan").order_by(LeaveRequest.created_at.asc()).limit(5).all()

    return render_template(
        "atasan/dashboard.html",
        harian_count=harian_count,
        outside_count=outside_count,
        late_count=late_count,
        pending_count=pending_count,
        outside_list=outside_list,
        pending_list=pending_list,
        now_time=datetime.now().strftime("%H:%M WITA")
    )

@atasan_bp.route("/persetujuan")
def persetujuan():
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

    # KPI stats
    pending_total = LeaveRequest.query.filter_by(status="diajukan").count()
    approved_today = Approval.query.filter(
        Approval.keputusan == "disetujui",
        db.func.date(Approval.waktu) == date.today()
    ).count()
    rejected_today = Approval.query.filter(
        Approval.keputusan == "ditolak",
        db.func.date(Approval.waktu) == date.today()
    ).count()

    return render_template(
        "atasan/persetujuan.html",
        pending_requests=pending_requests,
        pending_total=pending_total,
        approved_today=approved_today,
        rejected_today=rejected_today,
        dept=dept,
        cat=cat,
        q=q
    )

@atasan_bp.route("/persetujuan/<int:request_id>/setuju", methods=["POST"])
def setujui_izin(request_id):
    leave_req = LeaveRequest.query.get_or_404(request_id)
    catatan = request.form.get("catatan", "Disetujui oleh atasan.").strip()

    leave_req.status = "disetujui"
    
    # If starting today and start time already passed, automatically set to sedang_di_luar
    now = datetime.now()
    if leave_req.kategori == "keluar_sementara" and leave_req.tanggal_mulai == now.date():
        if leave_req.jam_pergi and now.time() >= leave_req.jam_pergi:
            leave_req.status = "sedang_di_luar"

    approval = Approval(
        request_id=leave_req.id,
        approver_id=current_user.id,
        keputusan="disetujui",
        catatan=catatan,
        waktu=datetime.utcnow()
    )
    db.session.add(approval)

    # Notify Pegawai
    notif = Notification(
        user_id=leave_req.user_id,
        judul="Izin Disetujui",
        pesan=f"Permohonan izin Anda (#{leave_req.nomor_tiket}) telah disetujui oleh {current_user.nama}. Catatan: {catatan}",
        tipe="success",
        link=f"/pegawai/detail/{leave_req.id}"
    )
    db.session.add(notif)

    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        aksi="SETUJUI_IZIN",
        objek=f"LeaveRequest #{leave_req.nomor_tiket}",
        detail=f"Disetujui. Catatan: {catatan}",
        ip_address=get_client_ip()
    )
    db.session.add(log)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"success": True, "message": f"Izin #{leave_req.nomor_tiket} telah disetujui."})

    flash(f"Izin #{leave_req.nomor_tiket} untuk {leave_req.pegawai.nama} telah disetujui.", "success")
    return redirect(url_for("atasan.persetujuan"))

@atasan_bp.route("/persetujuan/<int:request_id>/tolak", methods=["POST"])
def tolak_izin(request_id):
    leave_req = LeaveRequest.query.get_or_404(request_id)
    catatan = request.form.get("catatan", "").strip()

    if not catatan:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return jsonify({"success": False, "message": "Catatan alasan penolakan wajib diisi."}), 400
        flash("Catatan alasan penolakan wajib diisi.", "error")
        return redirect(url_for("atasan.persetujuan"))

    leave_req.status = "ditolak"
    leave_req.catatan_penolakan = catatan

    approval = Approval(
        request_id=leave_req.id,
        approver_id=current_user.id,
        keputusan="ditolak",
        catatan=catatan,
        waktu=datetime.utcnow()
    )
    db.session.add(approval)

    # Notify Pegawai
    notif = Notification(
        user_id=leave_req.user_id,
        judul="Izin Ditolak",
        pesan=f"Permohonan izin #{leave_req.nomor_tiket} ditolak oleh {current_user.nama}. Alasan: {catatan}",
        tipe="error",
        link=f"/pegawai/detail/{leave_req.id}"
    )
    db.session.add(notif)

    log = AuditLog(
        user_id=current_user.id,
        aksi="TOLAK_IZIN",
        objek=f"LeaveRequest #{leave_req.nomor_tiket}",
        detail=f"Ditolak. Alasan: {catatan}",
        ip_address=get_client_ip()
    )
    db.session.add(log)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"success": True, "message": f"Izin #{leave_req.nomor_tiket} telah ditolak."})

    flash(f"Izin #{leave_req.nomor_tiket} telah ditolak.", "info")
    return redirect(url_for("atasan.persetujuan"))

@atasan_bp.route("/sedang-di-luar")
def sedang_di_luar():
    check_and_update_leave_statuses()
    outside_requests = LeaveRequest.query.filter(
        LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"])
    ).order_by(LeaveRequest.jam_pulang_rencana.asc()).all()

    late_count = LeaveRequest.query.filter_by(status="terlambat_kembali").count()
    ontime_count = LeaveRequest.query.filter_by(status="sedang_di_luar").count()

    completed_today = LeaveRequest.query.filter(
        LeaveRequest.status.in_(["selesai", "selesai_terlambat", "selesai_pengecualian"]),
        db.func.date(LeaveRequest.jam_kembali_aktual) == date.today()
    ).count()

    return render_template(
        "atasan/sedang_di_luar.html",
        outside_requests=outside_requests,
        late_count=late_count,
        ontime_count=ontime_count,
        completed_today=completed_today,
        now_time=datetime.now().strftime("%H:%M:%S WITA")
    )

@atasan_bp.route("/verifikasi-bukti")
def verifikasi_bukti():
    # List leaves that have evidence uploaded
    evidences = Evidence.query.order_by(Evidence.waktu_unggah_server.desc()).limit(30).all()
    return render_template("atasan/verifikasi_bukti.html", evidences=evidences)

@atasan_bp.route("/pengecualian")
def pengecualian():
    pending_exceptions = ExceptionRequest.query.filter_by(status="menunggu").all()
    pending_extensions = Extension.query.filter_by(status="menunggu").all()
    return render_template(
        "atasan/pengecualian.html",
        pending_exceptions=pending_exceptions,
        pending_extensions=pending_extensions
    )

@atasan_bp.route("/pengecualian/<int:exc_id>/putuskan", methods=["POST"])
def putuskan_pengecualian(exc_id):
    exc = ExceptionRequest.query.get_or_404(exc_id)
    keputusan = request.form.get("keputusan")  # disetujui / ditolak
    catatan = request.form.get("catatan", "")

    exc.status = keputusan
    exc.approver_id = current_user.id
    exc.catatan = catatan
    exc.decided_at = datetime.utcnow()

    leave_req = exc.request
    if keputusan == "disetujui":
        leave_req.status = "selesai_pengecualian"
    else:
        # Rejected exception leaves it flagged
        leave_req.status = "terlambat_kembali"

    notif = Notification(
        user_id=leave_req.user_id,
        judul=f"Disposisi Pengecualian ({keputusan.capitalize()})",
        pesan=f"Pengecualian izin #{leave_req.nomor_tiket} telah {keputusan}. Catatan: {catatan}",
        tipe="success" if keputusan == "disetujui" else "error",
        link=f"/pegawai/detail/{leave_req.id}"
    )
    db.session.add(notif)
    db.session.commit()

    flash(f"Pengecualian #{leave_req.nomor_tiket} berhasil diputuskan ({keputusan}).", "success")
    return redirect(url_for("atasan.pengecualian"))

@atasan_bp.route("/perpanjangan/<int:ext_id>/putuskan", methods=["POST"])
def putuskan_perpanjangan(ext_id):
    ext = Extension.query.get_or_404(ext_id)
    keputusan = request.form.get("keputusan")  # disetujui / ditolak
    catatan = request.form.get("catatan", "")

    ext.status = keputusan
    ext.approver_id = current_user.id
    ext.catatan = catatan
    ext.decided_at = datetime.utcnow()

    leave_req = ext.request
    if keputusan == "disetujui":
        leave_req.jam_pulang_rencana = ext.jam_pulang_baru
        leave_req.status = "sedang_di_luar"

    notif = Notification(
        user_id=leave_req.user_id,
        judul=f"Perpanjangan Waktu ({keputusan.capitalize()})",
        pesan=f"Pengajuan perpanjangan izin #{leave_req.nomor_tiket} telah {keputusan}. Jam baru: {ext.jam_pulang_baru.strftime('%H:%M')} WITA.",
        tipe="success" if keputusan == "disetujui" else "error",
        link=f"/pegawai/penyelesaian/{leave_req.id}"
    )
    db.session.add(notif)
    db.session.commit()

    flash(f"Perpanjangan izin #{leave_req.nomor_tiket} telah {keputusan}.", "success")
    return redirect(url_for("atasan.pengecualian"))

@atasan_bp.route("/rekap")
def rekap():
    check_and_update_leave_statuses()
    month = int(request.args.get("month", datetime.now().month))
    year = int(request.args.get("year", datetime.now().year))
    export_fmt = request.args.get("export")

    # Aggregate by employee
    users = User.query.filter_by(aktif=True, peran="pegawai").all()
    rekap_data = []

    for u in users:
        reqs = LeaveRequest.query.filter(
            LeaveRequest.user_id == u.id,
            db.extract('month', LeaveRequest.tanggal_mulai) == month,
            db.extract('year', LeaveRequest.tanggal_mulai) == year
        ).all()

        harian_count = sum(1 for r in reqs if r.kategori == "harian")
        keluar_count = sum(1 for r in reqs if r.kategori == "keluar_sementara")
        late_count = sum(1 for r in reqs if r.status in ("selesai_terlambat", "terlambat_kembali"))
        exc_count = sum(1 for r in reqs if r.status == "selesai_pengecualian")

        total_min = 0
        for r in reqs:
            if r.jam_pergi and r.jam_pulang_rencana:
                delta = (r.jam_pulang_rencana.hour * 60 + r.jam_pulang_rencana.minute) - (r.jam_pergi.hour * 60 + r.jam_pergi.minute)
                if delta > 0:
                    total_min += delta

        hours = total_min // 60
        mins = total_min % 60

        rekap_data.append({
            "user": u,
            "harian_count": harian_count,
            "keluar_count": keluar_count,
            "late_count": late_count,
            "exc_count": exc_count,
            "durasi_str": f"{hours}j {mins}m",
            "total_reqs": len(reqs)
        })

    # CSV Export
    if export_fmt == "csv":
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(["NIP", "Nama Pegawai", "Unit Kerja", "Izin Harian", "Izin Keluar", "Total Durasi", "Terlambat", "Pengecualian"])
        for row in rekap_data:
            cw.writerow([
                row["user"].nip,
                row["user"].nama,
                row["user"].unit,
                row["harian_count"],
                row["keluar_count"],
                row["durasi_str"],
                row["late_count"],
                row["exc_count"]
            ])
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=rekap_izin_unhas_{year}_{month:02d}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    return render_template(
        "atasan/rekap.html",
        rekap_data=rekap_data,
        month=month,
        year=year
    )

@atasan_bp.route("/detail/<int:request_id>")
def detail_izin(request_id):
    leave_req = LeaveRequest.query.get_or_404(request_id)
    evidences = Evidence.query.filter_by(request_id=leave_req.id).all()
    approvals = leave_req.approvals.all()
    extensions = leave_req.extensions.all()
    exceptions = leave_req.exceptions.all()

    return render_template(
        "atasan/detail_izin.html",
        leave_req=leave_req,
        evidences=evidences,
        approvals=approvals,
        extensions=extensions,
        exceptions=exceptions
    )
