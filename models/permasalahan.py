from models.db import db
from sqlalchemy.orm import relationship

class PermasalahanLapang(db.Model):
    __tablename__ = 'permasalahan_lapang'

    id_permasalahan_lapang = db.Column(db.Integer, primary_key=True)
    id_lahan = db.Column(db.Integer, db.ForeignKey('data_lahan.id_lahan', ondelete='CASCADE'), nullable=False)
    tanggal = db.Column(db.Date)
    deskripsi = db.Column(db.Text)
    tindakan_penanganan = db.Column(db.Text)
    catatan_tambahan = db.Column(db.Text)
    foto_lapangan = db.Column(db.String(255))

    lahan = relationship('DataLahan', back_populates='permasalahan_reports')
