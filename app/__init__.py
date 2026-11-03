import os
from datetime import datetime
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config
from app.models import db, User, Notification
from app.services.location import get_client_ip, get_office_geofence

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan masuk untuk mengakses sistem Izin Monitor Unhas."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.pegawai import pegawai_bp
    from app.routes.atasan import atasan_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pegawai_bp)
    app.register_blueprint(atasan_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for("admin.users"))
            elif current_user.is_atasan:
                return redirect(url_for("atasan.dashboard"))
            return redirect(url_for("pegawai.beranda"))
        return redirect(url_for("auth.login"))

    # Global template context processor
    @app.context_processor
    def inject_global_context():
        client_ip = get_client_ip()
        office_geofence = get_office_geofence()
        unread_notifs_count = 0
        if current_user.is_authenticated:
            unread_notifs_count = Notification.query.filter_by(
                user_id=current_user.id, dibaca=False
            ).count()

        return {
            "current_ip": client_ip,
            "office_geofence": office_geofence,
            "unread_count": unread_notifs_count,
            "now_datetime": datetime.now()
        }

    # Custom Jinja template filters
    @app.template_filter("time_format")
    def time_format_filter(val):
        if not val:
            return "-"
        return val.strftime("%H:%M")

    @app.template_filter("date_format")
    def date_format_filter(val):
        if not val:
            return "-"
        return val.strftime("%d %b %Y")

    # Background scheduler for automatic status transitions
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = BackgroundScheduler(daemon=True)
        from app.services.scheduler import check_and_update_leave_statuses
        scheduler.add_job(
            func=check_and_update_leave_statuses,
            args=[app],
            trigger="interval",
            seconds=60,
            id="status_checker"
        )
        try:
            scheduler.start()
        except Exception:
            pass

    return app
