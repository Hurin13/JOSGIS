# edit_lahan.py

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from models.db import db
from routes.admin import admin_bp
from models.lahan import DataLahan  # Pastikan model DataLahan diimpor
# Import model-model laporan yang akan dihapus
from models.monitoring import Monitoring
from models.pemeliharaan import PemeliharaanTanaman
from models.hama import HamaPenyakit
from models.lingkungan import LingkunganCuaca
from models.permasalahan import PermasalahanLapang


@admin_bp.route('/edit_lahan/<int:id_lahan>', methods=['GET', 'POST'])
def edit_lahan_admin(id_lahan):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))

    # Ambil data lahan dengan GeoJSON
    lahan_data = db.session.execute(
        text("""
            SELECT id_lahan, id_pemilik, nama_lahan, tahun_tanam, varietas_kakao,
                   ST_AsGeoJSON(titik_ordinat) as titik_ordinat
            FROM data_lahan
            WHERE id_lahan = :id
        """),
        {'id': id_lahan}
    ).fetchone()

    if not lahan_data:
        flash("Lahan tidak ditemukan.")
        return redirect(url_for('admin.dashboard'))

    # Ambil id_pemilik sebelum data lahan diubah
    pemilik_lahan_id = lahan_data.id_pemilik

    if request.method == 'POST':
        nama = request.form['nama_lahan']
        tahun = request.form['tahun_tanam']
        varietas = request.form['varietas']
        geojson = request.form['titik_ordinat']

        luas_q = text("""
            SELECT ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:geo), 4326), 3857)) / 10000 AS luas
        """)
        luas = db.session.execute(luas_q, {'geo': geojson}).scalar()

        update_q = text("""
            UPDATE data_lahan
            SET nama_lahan = :nama, tahun_tanam = :tahun, varietas_kakao = :varietas,
                titik_ordinat = ST_SetSRID(ST_GeomFromGeoJSON(:geo),4326), luas_lahan = :luas
            WHERE id_lahan = :id
        """)
        db.session.execute(update_q, {
            'nama': nama,
            'tahun': tahun,
            'varietas': varietas,
            'geo': geojson,
            'luas': luas,
            'id': id_lahan
        })
        db.session.commit()
        flash('Lahan berhasil diperbarui.', 'success')

        return redirect(url_for('admin.user_detail', user_id=pemilik_lahan_id))

    return render_template('admin/edit_lahan.html', lahan=dict(lahan_data._mapping))


### Tambahan: Rute untuk Menghapus Lahan

@admin_bp.route('/hapus_lahan_admin/<int:id_lahan>', methods=['POST'])
def hapus_lahan_admin(id_lahan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'error')
        return redirect(url_for('admin.login'))

    lahan = DataLahan.query.get_or_404(id_lahan)

    # Ambil ID pemilik lahan sebelum data lahan dihapus
    petani_id = lahan.id_pemilik

    try:
        # Hapus semua laporan yang terkait
        Monitoring.query.filter_by(id_lahan=id_lahan).delete()
        PemeliharaanTanaman.query.filter_by(id_lahan=id_lahan).delete()
        HamaPenyakit.query.filter_by(id_lahan=id_lahan).delete()
        LingkunganCuaca.query.filter_by(id_lahan=id_lahan).delete()
        PermasalahanLapang.query.filter_by(id_lahan=id_lahan).delete()

        db.session.delete(lahan)
        db.session.commit()
        flash('Lahan dan semua laporan terkait berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menghapus lahan: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))
