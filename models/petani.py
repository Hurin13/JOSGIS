# models/petani.py

from models.db import db
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String


class Petani(db.Model):
    __tablename__ = 'petani'

    id_pemilik = db.Column(db.Integer, primary_key=True)
    nama_petani = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    alamat_petani = db.Column(db.Text)
    no_telepon = db.Column(db.String(20))
    email_petani = db.Column(db.String(100), unique=True, nullable=False)
    nik = db.Column(db.String(50), unique=True, nullable=False)
    titik_rumah = db.Column(Geometry(geometry_type='POINT', srid=4326))
    password_hash = db.Column(db.Text, nullable=True)  # ✅ PERBAIKAN: Set nullable=True jika mengizinkan login tanpa password

    google_id = db.Column(db.String(255), unique=True, nullable=True)
    google_email = db.Column(db.String(100), unique=True, nullable=True)

    @classmethod
    def create_or_get_from_google(cls, google_info):
        """
        Mencari petani berdasarkan google_id atau google_email. Jika tidak ditemukan,
        buat entri baru di database.
        """
        google_id = google_info.get('id')
        google_email = google_info.get('email')
        google_name = google_info.get('name')

        # ✅ PERBAIKAN: Cari pengguna terlebih dahulu
        petani = cls.query.filter_by(google_id=google_id).first()

        if not petani:
            # Jika tidak ditemukan, coba cari berdasarkan email
            petani = cls.query.filter_by(email_petani=google_email).first()
            if petani:
                # Jika user ditemukan via email, update dengan google_id-nya
                petani.google_id = google_id
                db.session.commit()
                return petani

        if not petani:
            # Jika user belum ada, buat entri baru
            petani = cls(
                nama_petani=google_name,
                email_petani=google_email,
                # ✅ PERBAIKAN: Buat NIK unik dari google_id
                nik='G-' + google_id,
                alamat_petani='-',
                no_telepon='-',
                gender='-',
                password_hash=None,  # ✅ PERBAIKAN: Gunakan None, bukan placeholder string
                google_id=google_id,
                google_email=google_email
            )
            db.session.add(petani)
            db.session.commit()
        return petani

    def needs_profile_completion(self):
        """
        Check if Google user needs to complete their profile.
        Returns True if user logged in via Google and has incomplete profile data.
        """
        if not self.google_id:
            return False

        incomplete_fields = [
            self.nik.startswith('G-') or not self.nik,
            self.gender == '-' or not self.gender,
            self.alamat_petani == '-' or not self.alamat_petani,
            self.no_telepon == '-' or not self.no_telepon,
            not self.titik_rumah
        ]

        return any(incomplete_fields)

def get_all_petani():
    """Mengambil semua objek Petani dari database."""
    return Petani.query.all()
