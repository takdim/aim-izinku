import random
from datetime import datetime, date, time
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models import (
    db, LeaveRequest, LeaveType, Evidence, Extension, ExceptionRequest,
    Notification, AuditLog, User
)
from app.services.location import get_client_ip, is_gps_within_office, get_office_geofence
from app.services.storage import save_and_compress_evidence
from app.services.scheduler import check_and_update_leave_statuses

pegawai_bp = Blueprint("pegawai", __name__, url_prefix="/pegawai")

def generate_ticket_number():
    year = datetime.now().year
    rand_id = random.randint(1000, 9999)
    return f"IZN-{year}-{rand_id}"

@pegawai_bp.route("/beranda")
@login_required
def beranda():
    # Update statuses
    check_and_update_leave_statuses()
    client_ip = get_client_ip()
    office_geofence = get_office_geofence()

    # Active leave request (priority: sedang_di_luar, terlambat_kembali, disetujui, diajukan)
    active_request = LeaveRequest.query.filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali", "disetujui"])
    ).order_by(LeaveRequest.id.desc()).first()

    # Calculate monthly statistics
    now = datetime.now()
    month_requests = LeaveRequest.query.filter(
        LeaveRequest.user_id == current_user.id,
        db.extract('month', LeaveRequest.tanggal_mulai) == now.month,
        db.extract('year', LeaveRequest.tanggal_mulai) == now.year
    ).all()

    total_izin_bulan = len(month_requests)
    
    # Calculate duration
    total_minutes = 0
    for r in month_requests:
        if r.jam_pergi and r.jam_pulang_rencana:
            delta = (r.jam_pulang_rencana.hour * 60 + r.jam_pulang_rencana.minute) - (r.jam_pergi.hour * 60 + r.jam_pergi.minute)
            if delta > 0:
                total_minutes += delta

    jam_keluar = total_minutes // 60
    menit_keluar = total_minutes % 60

    # Recent list
    recent_requests = LeaveRequest.query.filter_by(user_id=current_user.id)\
        .order_by(LeaveRequest.created_at.desc()).limit(5).all()

    return render_template(
        "pegawai/beranda.html",
        active_request=active_request,
        client_ip=client_ip,
        office_geofence=office_geofence,
        total_izin_bulan=total_izin_bulan,
        durasi_str=f"{jam_keluar}j {menit_keluar}m",
        recent_requests=recent_requests
    )

@pegawai_bp.route("/ajukan-keluar", methods=["GET", "POST"])
@login_required
def ajukan_keluar():
    if request.method == "POST":
        jenis_kode = request.form.get("jenis_izin", "kedinasan")
        # Map code to leave type
        leave_type = LeaveType.query.filter_by(kategori="keluar_sementara").filter(
            LeaveType.kode.like(f"%{jenis_kode}%")
        ).first()

        if not leave_type:
            leave_type = LeaveType.query.filter_by(kategori="keluar_sementara").first()

        jam_pergi_str = request.form.get("jam_pergi")
        jam_pulang_str = request.form.get("jam_pulang_rencana")
        alasan = request.form.get("alasan", "").strip()
        tujuan = request.form.get("tujuan", "").strip()

        if not (jam_pergi_str and jam_pulang_str and alasan and tujuan):
            flash("Mohon lengkapi semua kolom wajib pengajuan.", "error")
            return redirect(url_for("pegawai.ajukan_keluar"))

        try:
            jam_pergi = datetime.strptime(jam_pergi_str, "%H:%M").time()
            jam_pulang = datetime.strptime(jam_pulang_str, "%H:%M").time()
        except ValueError:
            flash("Format jam tidak valid.", "error")
            return redirect(url_for("pegawai.ajukan_keluar"))

        if jam_pulang <= jam_pergi:
            flash("Jam rencana pulang harus lebih lambat dari jam keberangkatan.", "error")
            return redirect(url_for("pegawai.ajukan_keluar"))

        today = date.today()
        tiket = generate_ticket_number()

        new_req = LeaveRequest(
            nomor_tiket=tiket,
            user_id=current_user.id,
            leave_type_id=leave_type.id if leave_type else 1,
            kategori="keluar_sementara",
            tanggal_mulai=today,
            tanggal_selesai=today,
            jam_pergi=jam_pergi,
            jam_pulang_rencana=jam_pulang,
            alasan=alasan,
            tujuan=tujuan,
            status="diajukan"
        )
        db.session.add(new_req)

        # Notify Atasan
        if current_user.atasan_id:
            notif = Notification(
                user_id=current_user.atasan_id,
                judul="Pengajuan Izin Keluar Baru",
                pesan=f"{current_user.nama} mengajukan izin keluar sementara ke {tujuan} ({jam_pergi_str} - {jam_pulang_str} WITA).",
                tipe="info",
                link=f"/atasan/persetujuan"
            )
            db.session.add(notif)

        # Audit log
        log = AuditLog(
            user_id=current_user.id,
            aksi="AJUKAN_IZIN_KELUAR",
            objek=f"LeaveRequest #{tiket}",
            detail=f"Tujuan: {tujuan}, Jam: {jam_pergi_str}-{jam_pulang_str}",
            ip_address=get_client_ip()
        )
        db.session.add(log)
        db.session.commit()

        flash(f"Pengajuan izin #{tiket} berhasil dikirim dan menunggu persetujuan atasan.", "success")
        return redirect(url_for("pegawai.beranda"))

    # GET
    leave_types = LeaveType.query.filter_by(kategori="keluar_sementara", aktif=True).all()
    today_str = datetime.now().strftime("%A, %d %B %Y")
    return render_template("pegawai/form_izin_keluar.html", leave_types=leave_types, today_str=today_str)

@pegawai_bp.route("/ajukan-harian", methods=["GET", "POST"])
@login_required
def ajukan_harian():
    if request.method == "POST":
        leave_type_id = request.form.get("leave_type_id")
        tgl_mulai_str = request.form.get("tanggal_mulai")
        tgl_selesai_str = request.form.get("tanggal_selesai")
        alasan = request.form.get("alasan", "").strip()

        if not (leave_type_id and tgl_mulai_str and tgl_selesai_str and alasan):
            flash("Mohon lengkapi semua data formulir izin harian.", "error")
            return redirect(url_for("pegawai.ajukan_harian"))

        try:
            tgl_mulai = datetime.strptime(tgl_mulai_str, "%Y-%m-%d").date()
            tgl_selesai = datetime.strptime(tgl_selesai_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Format tanggal tidak valid.", "error")
            return redirect(url_for("pegawai.ajukan_harian"))

        if tgl_selesai < tgl_mulai:
            flash("Tanggal selesai tidak boleh sebelum tanggal mulai.", "error")
            return redirect(url_for("pegawai.ajukan_harian"))

        # Optional attachment
        lampiran_filename = None
        if "lampiran" in request.files and request.files["lampiran"].filename:
            f = request.files["lampiran"]
            try:
                fname, _, _ = save_and_compress_evidence(file_obj=f, original_filename=f.filename)
                lampiran_filename = fname
            except Exception as e:
                pass

        tiket = generate_ticket_number()
        new_req = LeaveRequest(
            nomor_tiket=tiket,
            user_id=current_user.id,
            leave_type_id=leave_type_id,
            kategori="harian",
            tanggal_mulai=tgl_mulai,
            tanggal_selesai=tgl_selesai,
            alasan=alasan,
            lampiran_awal=lampiran_filename,
            status="diajukan"
        )
        db.session.add(new_req)

        # Notify Atasan
        if current_user.atasan_id:
            notif = Notification(
                user_id=current_user.atasan_id,
                judul="Pengajuan Izin Harian",
                pesan=f"{current_user.nama} mengajukan izin harian ({tgl_mulai_str} s.d {tgl_selesai_str}).",
                tipe="info",
                link="/atasan/persetujuan"
            )
            db.session.add(notif)

        db.session.commit()
        flash(f"Izin harian #{tiket} berhasil diajukan.", "success")
        return redirect(url_for("pegawai.beranda"))

    leave_types = LeaveType.query.filter_by(kategori="harian", aktif=True).all()
    return render_template("pegawai/form_izin_harian.html", leave_types=leave_types)

@pegawai_bp.route("/penyelesaian/<int:request_id>", methods=["GET", "POST"])
@login_required
def penyelesaian(request_id):
    check_and_update_leave_statuses()
    leave_req = LeaveRequest.query.filter_by(id=request_id, user_id=current_user.id).first_or_404()

    client_ip = get_client_ip()
    office_geofence = get_office_geofence()

    if request.method == "POST":
        # Check GPS Geofence enforcement
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")

        is_valid_loc, distance, loc_msg, _ = is_gps_within_office(lat, lon)
        if not is_valid_loc:
            flash(f"Gagal verifikasi lokasi: {loc_msg}", "error")
            return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

        tipe_bukti = request.form.get("tipe_bukti", "Foto di Meja Kerja")
        keterangan = request.form.get("keterangan", "")
        camera_data = request.form.get("camera_image")
        file_upload = request.files.get("file_upload")

        if not camera_data and not (file_upload and file_upload.filename):
            flash("Bukti kehadiran fisik wajib disertakan (ambil foto kamera atau unggah berkas).", "error")
            return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

        try:
            if camera_data:
                filename, size, mime = save_and_compress_evidence(base64_data=camera_data)
            else:
                filename, size, mime = save_and_compress_evidence(file_obj=file_upload, original_filename=file_upload.filename)
        except Exception as e:
            flash(f"Gagal memproses bukti foto: {str(e)}", "error")
            return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

        # Parse GPS coordinates
        try:
            lat_float = float(lat) if lat else None
            lon_float = float(lon) if lon else None
        except ValueError:
            lat_float, lon_float = None, None

        # Record Evidence with GPS location & distance
        evidence = Evidence(
            request_id=leave_req.id,
            filename=filename,
            original_filename=file_upload.filename if file_upload else "live_capture.jpg",
            tipe_bukti=tipe_bukti,
            keterangan=keterangan,
            ip_address=client_ip,
            latitude=lat_float,
            longitude=lon_float,
            distance_meters=round(distance, 1) if distance else 0.0,
            file_size_bytes=size,
            mime_type=mime,
            waktu_unggah_server=datetime.utcnow()
        )
        db.session.add(evidence)

        # Update Request Status
        now = datetime.now()
        leave_req.jam_kembali_aktual = now
        
        # Determine if returned late
        target_return = leave_req.jam_pulang_rencana
        approved_ext = Extension.query.filter_by(request_id=leave_req.id, status="disetujui").order_by(Extension.id.desc()).first()
        if approved_ext:
            target_return = approved_ext.jam_pulang_baru

        if target_return and now.time() > target_return:
            leave_req.status = "selesai_terlambat"
            status_text = "selesai (terlambat kembali)"
        else:
            leave_req.status = "selesai"
            status_text = "selesai tepat waktu"

        # Audit Log
        log = AuditLog(
            user_id=current_user.id,
            aksi="SELESAI_IZIN",
            objek=f"LeaveRequest #{leave_req.nomor_tiket}",
            detail=f"Status: {leave_req.status}, GPS: {lat_float},{lon_float} ({round(distance, 1)}m dari kantor)",
            ip_address=client_ip
        )
        db.session.add(log)

        # Notify Atasan
        if current_user.atasan_id:
            notif = Notification(
                user_id=current_user.atasan_id,
                judul="Izin Selesai Dilaporkan",
                pesan=f"{current_user.nama} telah menyelesaikan izin #{leave_req.nomor_tiket} ({status_text}) dalam radius kantor.",
                tipe="success",
                link=f"/atasan/detail/{leave_req.id}"
            )
            db.session.add(notif)

        db.session.commit()
        flash(f"Izin #{leave_req.nomor_tiket} berhasil ditutup. Lokasi GPS dan presensi fisik terverifikasi.", "success")
        return redirect(url_for("pegawai.beranda"))

    # Latest evidence if already uploaded
    latest_evidence = Evidence.query.filter_by(request_id=leave_req.id).order_by(Evidence.id.desc()).first()

    return render_template(
        "pegawai/penyelesaian_izin.html",
        leave_req=leave_req,
        client_ip=client_ip,
        office_geofence=office_geofence,
        latest_evidence=latest_evidence
    )

@pegawai_bp.route("/perpanjangan/<int:request_id>", methods=["POST"])
@login_required
def ajukan_perpanjangan(request_id):
    leave_req = LeaveRequest.query.filter_by(id=request_id, user_id=current_user.id).first_or_404()
    jam_baru_str = request.form.get("jam_pulang_baru")
    alasan = request.form.get("alasan", "").strip()

    if not (jam_baru_str and alasan):
        flash("Jam perpanjangan baru dan alasan wajib diisi.", "error")
        return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

    try:
        jam_baru = datetime.strptime(jam_baru_str, "%H:%M").time()
    except ValueError:
        flash("Format jam tidak valid.", "error")
        return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

    ext = Extension(
        request_id=leave_req.id,
        jam_pulang_baru=jam_baru,
        alasan=alasan,
        status="menunggu"
    )
    db.session.add(ext)

    if current_user.atasan_id:
        notif = Notification(
            user_id=current_user.atasan_id,
            judul="Pengajuan Perpanjangan Jam Izin",
            pesan=f"{current_user.nama} mengajukan perpanjangan izin #{leave_req.nomor_tiket} hingga {jam_baru_str} WITA: {alasan}",
            tipe="warning",
            link="/atasan/pengecualian"
        )
        db.session.add(notif)

    db.session.commit()
    flash("Pengajuan perpanjangan berhasil dikirimkan ke atasan.", "success")
    return redirect(url_for("pegawai.penyelesaian", request_id=request_id))

@pegawai_bp.route("/pengecualian/<int:request_id>", methods=["GET", "POST"])
@login_required
def form_pengecualian(request_id):
    leave_req = LeaveRequest.query.filter_by(id=request_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        alasan = request.form.get("alasan", "").strip()
        if not alasan:
            flash("Alasan pengecualian tidak boleh kosong.", "error")
            return redirect(url_for("pegawai.form_pengecualian", request_id=request_id))

        exc = ExceptionRequest(
            request_id=leave_req.id,
            alasan=alasan,
            status="menunggu"
        )
        db.session.add(exc)

        # Set status to selesai_pengecualian tentatively
        leave_req.status = "selesai_pengecualian"
        leave_req.jam_kembali_aktual = datetime.now()

        if current_user.atasan_id:
            notif = Notification(
                user_id=current_user.atasan_id,
                judul="Pengecualian Izin Tanpa Bukti",
                pesan=f"{current_user.nama} menutup izin #{leave_req.nomor_tiket} lewat jalur pengecualian: {alasan}",
                tipe="warning",
                link="/atasan/pengecualian"
            )
            db.session.add(notif)

        db.session.commit()
        flash("Pengecualian berhasil diajukan dan menunggu telaah atasan.", "info")
        return redirect(url_for("pegawai.beranda"))

    return render_template("pegawai/form_pengecualian.html", leave_req=leave_req)

@pegawai_bp.route("/riwayat")
@login_required
def riwayat():
    check_and_update_leave_statuses()
    status_filter = request.args.get("status", "semua")
    search_query = request.args.get("q", "").strip()

    query = LeaveRequest.query.filter_by(user_id=current_user.id)

    if status_filter == "selesai":
        query = query.filter(LeaveRequest.status.in_(["selesai", "selesai_terlambat", "selesai_pengecualian"]))
    elif status_filter == "di_luar":
        query = query.filter(LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"]))
    elif status_filter == "menunggu":
        query = query.filter_by(status="diajukan")
    elif status_filter == "ditolak":
        query = query.filter_by(status="ditolak")

    if search_query:
        query = query.filter(
            (LeaveRequest.nomor_tiket.ilike(f"%{search_query}%")) |
            (LeaveRequest.tujuan.ilike(f"%{search_query}%")) |
            (LeaveRequest.alasan.ilike(f"%{search_query}%"))
        )

    requests_list = query.order_by(LeaveRequest.created_at.desc()).all()

    # Counters
    all_count = LeaveRequest.query.filter_by(user_id=current_user.id).count()
    done_count = LeaveRequest.query.filter_by(user_id=current_user.id)\
        .filter(LeaveRequest.status.in_(["selesai", "selesai_terlambat", "selesai_pengecualian"])).count()
    outside_count = LeaveRequest.query.filter_by(user_id=current_user.id)\
        .filter(LeaveRequest.status.in_(["sedang_di_luar", "terlambat_kembali"])).count()
    pending_count = LeaveRequest.query.filter_by(user_id=current_user.id, status="diajukan").count()

    return render_template(
        "pegawai/daftar_riwayat.html",
        requests_list=requests_list,
        status_filter=status_filter,
        search_query=search_query,
        all_count=all_count,
        done_count=done_count,
        outside_count=outside_count,
        pending_count=pending_count
    )

@pegawai_bp.route("/detail/<int:request_id>")
@login_required
def detail(request_id):
    leave_req = LeaveRequest.query.filter_by(id=request_id, user_id=current_user.id).first_or_404()
    evidences = Evidence.query.filter_by(request_id=leave_req.id).all()
    approvals = leave_req.approvals.all()
    extensions = leave_req.extensions.all()
    exceptions = leave_req.exceptions.all()

    return render_template(
        "pegawai/detail_riwayat.html",
        leave_req=leave_req,
        evidences=evidences,
        approvals=approvals,
        extensions=extensions,
        exceptions=exceptions
    )

@pegawai_bp.route("/batalkan/<int:request_id>", methods=["POST"])
@login_required
def batalkan(request_id):
    leave_req = LeaveRequest.query.filter_by(id=request_id, user_id=current_user.id).first_or_404()
    if leave_req.status != "diajukan":
        flash("Hanya izin yang masih menunggu persetujuan yang dapat dibatalkan.", "error")
        return redirect(url_for("pegawai.detail", request_id=request_id))

    leave_req.status = "dibatalkan"
    log = AuditLog(
        user_id=current_user.id,
        aksi="BATALKAN_IZIN",
        objek=f"LeaveRequest #{leave_req.nomor_tiket}",
        detail="Pegawai membatalkan permohonan",
        ip_address=get_client_ip()
    )
    db.session.add(log)
    db.session.commit()
    flash(f"Pengajuan #{leave_req.nomor_tiket} telah dibatalkan.", "info")
    return redirect(url_for("pegawai.riwayat"))
