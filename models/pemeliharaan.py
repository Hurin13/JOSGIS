from models.db import db

class PemeliharaanTanaman(db.Model):
    __tablename__ = 'pemeliharaan_tanaman'

    id_pemeliharaan = db.Column(db.Integer, primary_key=True)
    id_lahan = db.Column(db.Integer, db.ForeignKey('data_lahan.id_lahan'), nullable=False)
    pemangkasan_kakao = db.Column(db.Boolean)
    tanggal_pemangkasan_kakao = db.Column(db.Date)
    pemangkasan_penaung = db.Column(db.Boolean)
    tanggal_pemangkasan_penaung = db.Column(db.Date)
    penyiangan_gulma = db.Column(db.Boolean)
    pemupukan = db.Column(db.Boolean)
    tanggal_aplikasi = db.Column(db.Date)
    jenis_pupuk = db.Column(db.String(100))
    jumlah_dosis = db.Column(db.Float)

    lahan = db.relationship('DataLahan', backref='pemeliharaan')
