from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, LeaveType, AuditLog, SystemSetting
from app.services.network import get_client_ip

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def restrict_admin():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if not current_user.is_admin:
        flash("Akses khusus Administrator Sistem.", "error")
        return redirect(url_for("pegawai.beranda"))

@admin_bp.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        nip = request.form.get("nip", "").strip()
        nama = request.form.get("nama", "").strip()
        email = request.form.get("email", "").strip()
        jabatan = request.form.get("jabatan", "").strip()
        unit = request.form.get("unit", "").strip()
        peran = request.form.get("peran", "pegawai")
        atasan_id = request.form.get("atasan_id") or None
        password = request.form.get("password", "password123").strip()

        if User.query.filter_by(nip=nip).first():
            flash(f"Pegawai dengan NIP {nip} sudah terdaftar.", "error")
            return redirect(url_for("admin.users"))

        new_user = User(
            nip=nip,
            nama=nama,
            email=email if email else None,
            jabatan=jabatan,
            unit=unit,
            peran=peran,
            atasan_id=atasan_id,
            aktif=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash(f"Pengguna {nama} (NIP {nip}) berhasil ditambahkan.", "success")
        return redirect(url_for("admin.users"))

    users_list = User.query.order_by(User.id.asc()).all()
    atasan_list = User.query.filter(User.peran.in_(["atasan", "admin"])).all()
    return render_template("admin/users.html", users=users_list, atasan_list=atasan_list)

@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.aktif = not user.aktif
    db.session.commit()
    flash(f"Status akun {user.nama} diubah menjadi {'Aktif' if user.aktif else 'Nonaktif'}.", "info")
    return redirect(url_for("admin.users"))

@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        subnets = request.form.get("office_subnets", "").strip()
        bypass = request.form.get("dev_bypass_ip_check", "false")
        jam_kerja = request.form.get("jam_kerja", "08:00 - 16:00")
        masa_simpan = request.form.get("masa_simpan_bukti", "365")

        # Save to SystemSetting table
        def upsert_setting(k, v, desc=""):
            s = SystemSetting.query.filter_by(key=k).first()
            if not s:
                s = SystemSetting(key=k, value=v, deskripsi=desc)
                db.session.add(s)
            else:
                s.value = v

        upsert_setting("office_subnets", subnets, "Daftar Subnet IP Kantor yang valid")
        upsert_setting("dev_bypass_ip_check", bypass, "Mode Dev Bypass Pengecekan IP")
        upsert_setting("jam_kerja", jam_kerja, "Rentang Jam Kerja Resmi Unhas")
        upsert_setting("masa_simpan_bukti", masa_simpan, "Masa Simpan Bukti Foto (Hari)")

        db.session.commit()
        flash("Pengaturan sistem berhasil diperbarui.", "success")
        return redirect(url_for("admin.settings"))

    # Load current settings
    settings_dict = {s.key: s.value for s in SystemSetting.query.all()}
    return render_template("admin/settings.html", settings=settings_dict)

@admin_bp.route("/audit-logs")
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template("admin/audit_logs.html", logs=logs)
