from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, AuditLog
from app.services.network import get_client_ip

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin.users"))
        elif current_user.is_atasan:
            return redirect(url_for("atasan.dashboard"))
        return redirect(url_for("pegawai.beranda"))

    if request.method == "POST":
        nip = request.form.get("nip", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter((User.nip == nip) | (User.email == nip)).first()
        if user and user.check_password(password):
            if not user.aktif:
                flash("Akun Anda telah dinonaktifkan. Silakan hubungi admin kepegawaian.", "error")
                return render_template("login.html")

            login_user(user, remember=True)
            # Audit log
            log = AuditLog(
                user_id=user.id,
                aksi="LOGIN",
                objek=f"User {user.nip}",
                detail=f"Login berhasil sebagai {user.peran}",
                ip_address=get_client_ip()
            )
            db.session.add(log)
            db.session.commit()

            flash(f"Selamat datang, {user.nama}!", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)

            if user.is_admin:
                return redirect(url_for("admin.users"))
            elif user.is_atasan:
                return redirect(url_for("atasan.dashboard"))
            return redirect(url_for("pegawai.beranda"))
        else:
            flash("NIP atau kata sandi tidak cocok. Silakan coba lagi.", "error")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    log = AuditLog(
        user_id=current_user.id,
        aksi="LOGOUT",
        objek=f"User {current_user.nip}",
        detail="Pengguna keluar sistem",
        ip_address=get_client_ip()
    )
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash("Anda telah berhasil keluar dari sistem.", "info")
    return redirect(url_for("auth.login"))
