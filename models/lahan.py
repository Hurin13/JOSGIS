from models.db import db
from sqlalchemy.orm import relationship

class DataLahan(db.Model):
    __tablename__ = 'data_lahan'

    id_lahan = db.Column(db.Integer, primary_key=True)
    id_pemilik = db.Column(db.Integer, db.ForeignKey('petani.id_pemilik'), nullable=False)
    nama_lahan = db.Column(db.String(100))
    luas_lahan = db.Column(db.Float)
    titik_ordinat = db.Column(db.Text)  # Simpan sebagai WKT (Well-Known Text)
    tahun_tanam = db.Column(db.Integer)
    varietas_kakao = db.Column(db.String(100))
    bukti_luas_sertifikat = db.Column(db.String(255))

    petani = db.relationship('Petani', backref='lahan')

    # ✅ PERBAIKAN: Gunakan back_populates di sini, dan tambahkan overlaps
    #monitoring_reports = relationship('Monitoring', back_populates='lahan', overlaps="monitoring")
    pemeliharaan_reports = relationship('PemeliharaanTanaman', back_populates='lahan', overlaps="pemeliharaan")
    hama_reports = relationship('HamaPenyakit', back_populates='lahan', overlaps="hama")
    lingkungan_reports = relationship('LingkunganCuaca', back_populates='lahan', overlaps="lingkungan")
    permasalahan_reports = relationship('PermasalahanLapang', back_populates='lahan', overlaps="permasalahan")
