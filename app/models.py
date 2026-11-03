from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nama = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    jabatan = db.Column(db.String(120), nullable=False, default="Pegawai")
    unit = db.Column(db.String(150), nullable=False, default="Fakultas Teknik Unhas Gowa")
    peran = db.Column(db.Enum("pegawai", "atasan", "admin", name="user_role"), nullable=False, default="pegawai")
    atasan_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    foto_profil = db.Column(db.Text, nullable=True)
    aktif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    atasan = db.relationship("User", remote_side=[id], backref=db.backref("bawahan", lazy="dynamic"))
    requests = db.relationship("LeaveRequest", foreign_keys="LeaveRequest.user_id", backref="pegawai", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_atasan(self):
        return self.peran in ("atasan", "admin")

    @property
    def is_admin(self):
        return self.peran == "admin"


class LeaveType(db.Model):
    __tablename__ = "leave_types"
    
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(50), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.Enum("keluar_sementara", "harian", name="leave_category"), nullable=False)
    perlu_lampiran = db.Column(db.Boolean, default=False)
    jenis_bukti_diterima = db.Column(db.String(255), nullable=True)
    aktif = db.Column(db.Boolean, default=True)


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"
    
    id = db.Column(db.Integer, primary_key=True)
    nomor_tiket = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey("leave_types.id"), nullable=False)
    kategori = db.Column(db.Enum("keluar_sementara", "harian", name="req_category"), nullable=False)
    
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    jam_pergi = db.Column(db.Time, nullable=True)
    jam_pulang_rencana = db.Column(db.Time, nullable=True)
    jam_kembali_aktual = db.Column(db.DateTime, nullable=True)
    
    alasan = db.Column(db.Text, nullable=False)
    tujuan = db.Column(db.String(255), nullable=True)
    lampiran_awal = db.Column(db.String(255), nullable=True)
    
    status = db.Column(
        db.Enum(
            "diajukan",
            "disetujui",
            "ditolak",
            "dibatalkan",
            "sedang_di_luar",
            "terlambat_kembali",
            "selesai",
            "selesai_terlambat",
            "selesai_pengecualian",
            name="request_status"
        ),
        nullable=False,
        default="diajukan",
        index=True
    )
    
    catatan_penolakan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leave_type = db.relationship("LeaveType", backref="requests")
    approvals = db.relationship("Approval", backref="request", lazy="dynamic", cascade="all, delete-orphan")
    evidences = db.relationship("Evidence", backref="request", lazy="dynamic", cascade="all, delete-orphan")
    extensions = db.relationship("Extension", backref="request", lazy="dynamic", cascade="all, delete-orphan")
    exceptions = db.relationship("ExceptionRequest", backref="request", lazy="dynamic", cascade="all, delete-orphan")


class Approval(db.Model):
    __tablename__ = "approvals"
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("leave_requests.id", ondelete="CASCADE"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    keputusan = db.Column(db.Enum("disetujui", "ditolak", name="approval_decision"), nullable=False)
    catatan = db.Column(db.Text, nullable=True)
    waktu = db.Column(db.DateTime, default=datetime.utcnow)

    approver = db.relationship("User", foreign_keys=[approver_id])


class Evidence(db.Model):
    __tablename__ = "evidences"
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("leave_requests.id", ondelete="CASCADE"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    tipe_bukti = db.Column(db.String(100), default="Foto di Meja Kerja")
    keterangan = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    file_size_bytes = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(100), default="image/jpeg")
    waktu_unggah_server = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Extension(db.Model):
    __tablename__ = "extensions"
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("leave_requests.id", ondelete="CASCADE"), nullable=False)
    jam_pulang_baru = db.Column(db.Time, nullable=False)
    alasan = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum("menunggu", "disetujui", "ditolak", name="ext_status"), default="menunggu")
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    catatan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime, nullable=True)

    approver = db.relationship("User", foreign_keys=[approver_id])


class ExceptionRequest(db.Model):
    __tablename__ = "exceptions"
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("leave_requests.id", ondelete="CASCADE"), nullable=False)
    alasan = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum("menunggu", "disetujui", "ditolak", name="exc_status"), default="menunggu")
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    catatan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime, nullable=True)

    approver = db.relationship("User", foreign_keys=[approver_id])


class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    judul = db.Column(db.String(150), nullable=False)
    pesan = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    tipe = db.Column(db.String(50), default="info")  # info, warning, success, error
    dibaca = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    aksi = db.Column(db.String(100), nullable=False)
    objek = db.Column(db.String(200), nullable=True)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User")


class SystemSetting(db.Model):
    __tablename__ = "settings"
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    deskripsi = db.Column(db.String(255), nullable=True)
