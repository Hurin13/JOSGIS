# models/monitoring.py

from models.db import db
from sqlalchemy.orm import relationship # ✅ Tambahkan baris ini

class Monitoring(db.Model):
    __tablename__ = 'monitoring_tanaman'
    id_monitoring = db.Column(db.Integer, primary_key=True)
    id_lahan = db.Column(db.Integer, db.ForeignKey('data_lahan.id_lahan'), nullable=False)
    tanggal_monitoring = db.Column(db.Date)
    jumlah_pohon_mati = db.Column(db.Integer)
    jenis_hama = db.Column(db.String(100))
    produktivitas = db.Column(db.Float)
    tinggi_tanaman = db.Column(db.Float)
    daun_menguning = db.Column(db.Boolean)
    kerusakan_batang = db.Column(db.String(20))
    foto_tanaman = db.Column(db.String(255))

    lahan = relationship('DataLahan', backref=db.backref('monitoring_reports', lazy=True))
