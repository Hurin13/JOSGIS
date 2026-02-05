from models.db import db

class LingkunganCuaca(db.Model):
    __tablename__ = 'lingkungan_cuaca'

    id_lingkungan_cuaca = db.Column(db.Integer, primary_key=True)
    id_lahan = db.Column(db.Integer, db.ForeignKey('data_lahan.id_lahan', ondelete='CASCADE'), nullable=False)
    tanggal = db.Column(db.Date)
    curah_hujan = db.Column(db.Float)
    drainase = db.Column(db.Enum('baik', 'sedang', 'buruk', name='drainase_enum'))
    naungan = db.Column(db.Enum('terlalu banyak', 'cukup', 'kurang', name='naungan_enum'))
    foto_lingkungan = db.Column(db.String(255))

    lahan = db.relationship('DataLahan', backref=db.backref('lingkungan_cuaca', lazy=True))
