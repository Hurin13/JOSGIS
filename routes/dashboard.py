from flask import Blueprint, render_template, session, redirect, url_for
from sqlalchemy import text
from models.monitoring import Monitoring
from models.lahan import DataLahan
from models.pemeliharaan import PemeliharaanTanaman
from models.hama import HamaPenyakit
from models.lingkungan import LingkunganCuaca
from models.permasalahan import PermasalahanLapang  # <- Tambahan
from models.db import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    nama_petani = session.get('user_nama', 'Pengguna')
    user_id = session['user_id']

    # Ambil data lahan
    sql = text("""
        SELECT id_lahan, nama_lahan, luas_lahan, tahun_tanam, varietas_kakao, ST_AsGeoJSON(titik_ordinat) as geojson
        FROM data_lahan WHERE id_pemilik = :user_id
    """)
    result = db.session.execute(sql, {'user_id': user_id})
    lahan_list = result.fetchall()

    # Ambil data petani
    sql_petani = text("""
            SELECT id_pemilik, nama_petani, alamat_petani, no_telepon, ST_AsGeoJSON(titik_rumah) as geojson
            FROM petani WHERE id_pemilik = :user_id
        """)
    result_petani = db.session.execute(sql_petani, {'user_id': user_id})
    petani_list = result_petani.fetchall()
    petani = {
        "id_pemilik": petani_list[0][0],
        "nama_petani" : petani_list[0][1],
        "alamat_petani" : petani_list[0][2],
        "no_telepon" : petani_list[0][3],
        "titik_rumah" : petani_list[0][4],
    }

    # Ambil 5 riwayat monitoring terbaru
    monitoring = (
        db.session.query(Monitoring, DataLahan.nama_lahan)
        .join(DataLahan, Monitoring.id_lahan == DataLahan.id_lahan)
        .filter(DataLahan.id_pemilik == user_id)
        .order_by(Monitoring.tanggal_monitoring.desc())
        .limit(5)
        .all()
    )

    # Ambil 5 riwayat pemeliharaan terbaru
    pemeliharaan = (
        db.session.query(PemeliharaanTanaman, DataLahan.nama_lahan)
        .join(DataLahan, PemeliharaanTanaman.id_lahan == DataLahan.id_lahan)
        .filter(DataLahan.id_pemilik == user_id)
        .order_by(PemeliharaanTanaman.tanggal_aplikasi.desc())
        .limit(5)
        .all()
    )

    # Ambil 5 riwayat hama terbaru
    hama = (
        db.session.query(HamaPenyakit, DataLahan.nama_lahan)
        .join(DataLahan, HamaPenyakit.id_lahan == DataLahan.id_lahan)
        .filter(DataLahan.id_pemilik == user_id)
        .order_by(HamaPenyakit.tanggal.desc())
        .limit(5)
        .all()
    )

    # Ambil 5 riwayat lingkungan cuaca terbaru
    lingkungan = (
        db.session.query(LingkunganCuaca, DataLahan.nama_lahan)
        .join(DataLahan, LingkunganCuaca.id_lahan == DataLahan.id_lahan)
        .filter(DataLahan.id_pemilik == user_id)
        .order_by(LingkunganCuaca.tanggal.desc())
        .limit(5)
        .all()
    )

    # Ambil 5 riwayat permasalahan lapang terbaru
    permasalahan = (
        db.session.query(PermasalahanLapang, DataLahan.nama_lahan)
        .join(DataLahan, PermasalahanLapang.id_lahan == DataLahan.id_lahan)
        .filter(DataLahan.id_pemilik == user_id)
        .order_by(PermasalahanLapang.tanggal.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'dashboard.html',
        nama=nama_petani,
        lahan=lahan_list,
        monitoring=monitoring,
        pemeliharaan=pemeliharaan,
        hama=hama,
        lingkungan=lingkungan,
        permasalahan=permasalahan,  # <- Kirim ke template
        petani=petani
    )
