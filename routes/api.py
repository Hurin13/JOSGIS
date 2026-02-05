from flask import Blueprint, jsonify, session, redirect, url_for, request
from sqlalchemy import text, func
from models.db import db
from models.monitoring import Monitoring
from models.lahan import DataLahan
from models.lingkungan import LingkunganCuaca
from models.hama import HamaPenyakit
from models.pemeliharaan import PemeliharaanTanaman
from datetime import datetime, timedelta
import requests

api_bp = Blueprint('api', __name__)


@api_bp.route('/chart-data')
def get_chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    selected_farm = request.args.get('farm_id', type=int)

    farm_filter = ""
    params = {'user_id': user_id}
    if selected_farm:
        farm_filter = "AND dl.id_lahan = :farm_id"
        params['farm_id'] = selected_farm

    farm_info = db.session.execute(text("""
        SELECT id_lahan, nama_lahan, luas_lahan, varietas_kakao, tahun_tanam
        FROM data_lahan 
        WHERE id_pemilik = :user_id
        ORDER BY nama_lahan
    """), {'user_id': user_id}).fetchall()

    productivity_data = db.session.execute(text(f"""
        SELECT 
            DATE_TRUNC('month', m.tanggal_monitoring) as month,
            AVG(m.produktivitas) as avg_productivity
        FROM monitoring_tanaman m
        JOIN data_lahan dl ON m.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {farm_filter}
        AND m.tanggal_monitoring >= NOW() - INTERVAL '6 months'
        AND m.produktivitas IS NOT NULL
        GROUP BY DATE_TRUNC('month', m.tanggal_monitoring)
        ORDER BY month
    """), params).fetchall()

    rainfall_data = db.session.execute(text(f"""
        SELECT 
            DATE_TRUNC('month', lc.tanggal) as month,
            AVG(lc.curah_hujan) as avg_rainfall
        FROM lingkungan_cuaca lc
        JOIN data_lahan dl ON lc.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {farm_filter}
        AND lc.tanggal >= NOW() - INTERVAL '6 months'
        AND lc.curah_hujan IS NOT NULL
        GROUP BY DATE_TRUNC('month', lc.tanggal)
        ORDER BY month
    """), params).fetchall()

    health_data = db.session.execute(text(f"""
        SELECT 
            COUNT(CASE WHEN m.daun_menguning = true THEN 1 END) as daun_menguning,
            COUNT(CASE WHEN m.kerusakan_batang IS NOT NULL AND m.kerusakan_batang != '' THEN 1 END) as kerusakan_batang,
            COUNT(CASE WHEN m.jumlah_pohon_mati > 0 THEN 1 END) as pohon_mati,
            COUNT(*) as total_monitoring
        FROM monitoring_tanaman m
        JOIN data_lahan dl ON m.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {farm_filter}
        AND m.tanggal_monitoring >= NOW() - INTERVAL '3 months'
    """), params).fetchone()

    pest_data = db.session.execute(text(f"""
        SELECT 
            hp.tingkat_serangan_hama,
            COUNT(*) as count
        FROM hama_penyakit hp
        JOIN data_lahan dl ON hp.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {farm_filter}
        AND hp.tanggal >= NOW() - INTERVAL '6 months'
        AND hp.tingkat_serangan_hama IS NOT NULL
        GROUP BY hp.tingkat_serangan_hama
    """), params).fetchall()

    maintenance_data = db.session.execute(text(f"""
        SELECT 
            COUNT(CASE WHEN pt.pemangkasan_kakao = true THEN 1 END) as pemangkasan,
            COUNT(CASE WHEN pt.pemupukan = true THEN 1 END) as pemupukan,
            COUNT(CASE WHEN pt.penyiangan_gulma = true THEN 1 END) as penyiangan
        FROM pemeliharaan_tanaman pt
        JOIN data_lahan dl ON pt.id_lahan = dl.id_lahan
        WHERE dl.id_pemilik = :user_id {farm_filter}
        AND pt.tanggal_aplikasi >= NOW() - INTERVAL '6 months'
    """), params).fetchone()

    variety_data = db.session.execute(text(f"""
        SELECT 
            dl.varietas_kakao,
            SUM(dl.luas_lahan) as total_luas
        FROM data_lahan dl
        WHERE dl.id_pemilik = :user_id {farm_filter}
        GROUP BY dl.varietas_kakao
    """), params).fetchall()

    selected_farm_info = None
    if selected_farm:
        selected_farm_info = next((farm for farm in farm_info if farm.id_lahan == selected_farm), None)

    return jsonify({
        'selected_farm': {
            'id_lahan': selected_farm_info.id_lahan if selected_farm_info else None,
            'nama_lahan': selected_farm_info.nama_lahan if selected_farm_info else 'Semua Lahan'
        } if selected_farm_info or not selected_farm else {'id_lahan': None, 'nama_lahan': 'Semua Lahan'},
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
                health_data.total_monitoring - health_data.daun_menguning - health_data.kerusakan_batang - health_data.pohon_mati) if health_data else 0
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


@api_bp.route('/profile-data')
def get_profile_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    # Ambil data petani
    petani_data = db.session.execute(text("""
        SELECT id_pemilik, nama_petani, email_petani, nik, alamat_petani, 
               no_telepon, gender, ST_AsGeoJSON(titik_rumah) as geojson
        FROM petani WHERE id_pemilik = :user_id
    """), {'user_id': user_id}).fetchone()

    if not petani_data:
        return jsonify({'error': 'Profile not found'}), 404

    return jsonify({
        'id_pemilik': petani_data.id_pemilik,
        'nama_petani': petani_data.nama_petani,
        'email_petani': petani_data.email_petani,
        'nik': petani_data.nik,
        'alamat_petani': petani_data.alamat_petani,
        'no_telepon': petani_data.no_telepon,
        'gender': petani_data.gender,
        'titik_rumah': petani_data.geojson
    })


@api_bp.route('/reverse_geocode', methods=['POST'])
def reverse_geocode():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')

        if not lat or not lon:
            return jsonify({'error': 'Latitude and longitude are required'}), 400

        # Use Nominatim (OpenStreetMap) for reverse geocoding
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'zoom': 18,
            'addressdetails': 1,
            'accept-language': 'id'  # Indonesian language preference
        }

        headers = {
            'User-Agent': 'WebGIS-Petani-Kakao/1.0'  # Required by Nominatim
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()

            # Extract address components
            address_parts = []
            address = result.get('address', {})

            # Build address string in Indonesian format
            if address.get('house_number'):
                address_parts.append(address['house_number'])
            if address.get('road'):
                address_parts.append(address['road'])
            if address.get('village') or address.get('suburb'):
                address_parts.append(address.get('village') or address.get('suburb'))
            if address.get('city_district') or address.get('town'):
                address_parts.append(address.get('city_district') or address.get('town'))
            if address.get('city') or address.get('county'):
                address_parts.append(address.get('city') or address.get('county'))
            if address.get('state'):
                address_parts.append(address.get('state'))
            if address.get('postcode'):
                address_parts.append(address['postcode'])

            alamat = ', '.join(filter(None, address_parts))

            # Fallback to display_name if no detailed address
            if not alamat:
                alamat = result.get('display_name', f'Koordinat: {lat}, {lon}')

            return jsonify({
                'alamat': alamat,
                'detail': address
            })
        else:
            return jsonify({
                'alamat': f'Koordinat: {lat}, {lon}',
                'detail': {}
            })

    except requests.RequestException as e:
        # Network error - return coordinates as fallback
        return jsonify({
            'alamat': f'Koordinat: {lat}, {lon}',
            'detail': {},
            'error': 'Network error during geocoding'
        })
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
