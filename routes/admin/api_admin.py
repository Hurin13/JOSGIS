# routes/admin/api_admin.py

from flask import Blueprint, jsonify, session, request
from sqlalchemy import text, func
from models.db import db
from models.monitoring import Monitoring
from models.lahan import DataLahan
from models.lingkungan import LingkunganCuaca
from models.hama import HamaPenyakit
from models.pemeliharaan import PemeliharaanTanaman
from datetime import datetime, timedelta

api_admin_bp = Blueprint('api_admin', __name__)

@api_admin_bp.route('/chart-data')
def get_admin_chart_data():
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized access'}), 401

    user_id_to_filter = request.args.get('user_id', type=int)
    if not user_id_to_filter:
        return jsonify({'error': 'Missing user_id parameter'}), 400

    selected_farm = request.args.get('farm_id', type=int)

    params = {'user_id': user_id_to_filter}

    # ✅ PERBAIKAN UTAMA: Tambahkan alias 'dl.' di depan id_lahan
    lahan_id_filter = ""
    if selected_farm:
        lahan_id_filter = " AND dl.id_lahan = :farm_id"
        params['farm_id'] = selected_farm

    # Kueri ini tidak perlu alias 'dl' karena tidak ada JOIN
    farm_info = db.session.execute(text("""
        SELECT id_lahan, nama_lahan, luas_lahan, varietas_kakao, tahun_tanam
        FROM data_lahan
        WHERE id_pemilik = :user_id
        ORDER BY nama_lahan
    """), {'user_id': user_id_to_filter}).fetchall()

    # Kueri ini tetap menggunakan alias 'dl' karena mereka melakukan JOIN
    # ✅ Perbaikan: Gunakan 'lahan_id_filter' baru
    productivity_data = db.session.execute(text(f"""
        SELECT 
            DATE_TRUNC('month', m.tanggal_monitoring) as month,
            AVG(m.produktivitas) as avg_productivity
        FROM monitoring_tanaman m
        JOIN data_lahan dl ON m.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        AND m.tanggal_monitoring >= NOW() - INTERVAL '6 months'
        AND m.produktivitas IS NOT NULL
        GROUP BY DATE_TRUNC('month', m.tanggal_monitoring)
        ORDER BY month
    """), params).fetchall()

    # rainfall_data
    # ✅ Perbaikan: Gunakan 'lahan_id_filter' baru
    rainfall_data = db.session.execute(text(f"""
        SELECT
            DATE_TRUNC('month', lc.tanggal) as month,
            AVG(lc.curah_hujan) as avg_rainfall
        FROM lingkungan_cuaca lc
        JOIN data_lahan dl ON lc.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        AND lc.tanggal >= NOW() - INTERVAL '6 months'
        AND lc.curah_hujan IS NOT NULL
        GROUP BY DATE_TRUNC('month', lc.tanggal)
        ORDER BY month
    """), params).fetchall()

    # health_data
    # ✅ Perbaikan: Gunakan 'lahan_id_filter' baru
    health_data = db.session.execute(text(f"""
        SELECT
            COUNT(CASE WHEN m.daun_menguning = true THEN 1 END) as daun_menguning,
            COUNT(CASE WHEN m.kerusakan_batang IS NOT NULL AND m.kerusakan_batang != '' THEN 1 END) as kerusakan_batang,
            COUNT(CASE WHEN m.jumlah_pohon_mati > 0 THEN 1 END) as pohon_mati,
            COUNT(*) as total_monitoring
        FROM monitoring_tanaman m
        JOIN data_lahan dl ON m.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        AND m.tanggal_monitoring >= NOW() - INTERVAL '3 months'
    """), params).fetchone()

    # pest_data
    # ✅ Perbaikan: Gunakan 'lahan_id_filter' baru
    pest_data = db.session.execute(text(f"""
        SELECT
            hp.tingkat_serangan_hama,
            COUNT(*) as count
        FROM hama_penyakit hp
        JOIN data_lahan dl ON hp.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        AND hp.tanggal >= NOW() - INTERVAL '6 months'
        AND hp.tingkat_serangan_hama IS NOT NULL
        GROUP BY hp.tingkat_serangan_hama
    """), params).fetchall()

    # maintenance_data
    # ✅ Perbaikan: Gunakan 'lahan_id_filter' baru
    maintenance_data = db.session.execute(text(f"""
        SELECT
            COUNT(CASE WHEN pt.pemangkasan_kakao = true THEN 1 END) as pemangkasan,
            COUNT(CASE WHEN pt.pemupukan = true THEN 1 END) as pemupukan,
            COUNT(CASE WHEN pt.penyiangan_gulma = true THEN 1 END) as penyiangan
        FROM pemeliharaan_tanaman pt
        JOIN data_lahan dl ON pt.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        AND pt.tanggal_aplikasi >= NOW() - INTERVAL '6 months'
    """), params).fetchone()

    # variety_data
    # ✅ Perbaikan: Kueri ini tidak memiliki join, tetapi Anda ingin memfilter berdasarkan id_lahan.
    # Maka, filter `dl.id_lahan` juga harus dimasukkan di sini.
    variety_data = db.session.execute(text(f"""
        SELECT
            dl.varietas_kakao,
            SUM(dl.luas_lahan) as total_luas
        FROM data_lahan dl
        WHERE dl.id_pemilik = :user_id {lahan_id_filter}
        GROUP BY dl.varietas_kakao
    """), params).fetchall()

    selected_farm_info = None
    if selected_farm:
        selected_farm_info = next((farm for farm in farm_info if farm.id_lahan == selected_farm), None)

    # Determine the response structure for selected_farm
    if selected_farm and selected_farm_info:
        selected_farm_response = {
            'id_lahan': selected_farm_info.id_lahan,
            'nama_lahan': selected_farm_info.nama_lahan
        }
    else:
        selected_farm_response = {
            'id_lahan': None,
            'nama_lahan': 'Semua Lahan'
        }

    return jsonify({
        'selected_farm': selected_farm_response,
        'farm_info': [
            {
                'id_lahan': row.id_lahan,
                'nama_lahan': row.nama_lahan,
                'luas_lahan': float(row.luas_lahan),
                'varietas_kakao': row.varietas_kakao,
                'tahun_tanam': int(row.tahun_tanam) if row.tahun_tanam else None
            } for row in farm_info
        ],
        'productivity': [
            {
                'month': row.month.strftime('%Y-%m') if row.month else '',
                'value': float(row.avg_productivity) if row.avg_productivity else 0
            } for row in productivity_data
        ],
        'rainfall': [
            {
                'month': row.month.strftime('%Y-%m') if row.month else '',
                'value': float(row.avg_rainfall) if row.avg_rainfall else 0
            } for row in rainfall_data
        ],
        'health': {
            'daun_menguning': int(health_data.daun_menguning) if health_data else 0,
            'kerusakan_batang': int(health_data.kerusakan_batang) if health_data else 0,
            'pohon_mati': int(health_data.pohon_mati) if health_data else 0,
            'sehat': int(
                health_data.total_monitoring - health_data.daun_menguning - health_data.kerusakan_batang - health_data.pohon_mati) if health_data and health_data.total_monitoring > 0 else 0
        },
        'pest': [
            {
                'level': row.tingkat_serangan_hama,
                'count': int(row.count)
            } for row in pest_data
        ],
        'maintenance': {
            'pemangkasan': int(maintenance_data.pemangkasan) if maintenance_data else 0,
            'pemupukan': int(maintenance_data.pemupukan) if maintenance_data else 0,
            'penyiangan': int(maintenance_data.penyiangan) if maintenance_data else 0
        },
        'variety': [
            {
                'variety': row.varietas_kakao,
                'area': float(row.total_luas)
            } for row in variety_data
        ]
    })
