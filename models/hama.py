# models/hama.py

from models.db import db
from sqlalchemy.orm import relationship # ✅ Tambahkan baris ini

class HamaPenyakit(db.Model):
    __tablename__ = 'hama_penyakit'

    id_serangan = db.Column(db.Integer, primary_key=True)
    id_lahan = db.Column(db.Integer, db.ForeignKey('data_lahan.id_lahan'), nullable=False)
    tanggal = db.Column(db.Date)
    jenis_hama = db.Column(db.String(50))
    tingkat_serangan_hama = db.Column(db.Enum('rendah', 'sedang', 'tinggi', name='tingkat_serangan_enum'))
    luas_terdampak = db.Column(db.Float)
    pengendalian_dilakukan = db.Column(db.Boolean)

    jenis_pengendalian_hama = db.Column(db.Enum('mekanis', 'kimia', 'hayati', 'lainnya', name='jenis_pengendalian_enum'))
    keterangan_pengendalian_hama = db.Column(db.String(100))

    jenis_pengendalian_penyakit = db.Column(db.Enum('mekanis', 'kimia', 'hayati', 'lainnya', name='jenis_pengendalian_enum'))
    keterangan_pengendalian_penyakit = db.Column(db.String(100))

    lahan = relationship('DataLahan', back_populates='hama_reports')
