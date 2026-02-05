import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from models.db import db

lahan_bp = Blueprint('lahan', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📌 Tampilkan daftar lahan
@lahan_bp.route('/lahan')
def kelola_lahan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    hasil = db.session.execute(
        text("""
            SELECT id_lahan, nama_lahan, luas_lahan, tahun_tanam,
                   varietas_kakao, bukti_luas_sertifikat,
                   ST_AsGeoJSON(titik_ordinat) as geojson
            FROM data_lahan WHERE id_pemilik = :id
        """),
        {'id': session['user_id']}
    )
    daftar_lahan = [dict(row._mapping) for row in hasil]

    return render_template('lahan/kelola_lahan.html', daftar_lahan=daftar_lahan)

# 📌 Tambah lahan
@lahan_bp.route('/lahan/tambah', methods=['GET', 'POST'])
def tambah_lahan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nama = request.form['nama_lahan']
        tahun = request.form['tahun_tanam']
        varietas = request.form['varietas']
        geojson = request.form['titik_ordinat']
        file = request.files['bukti']

        # Hitung luas dari GeoJSON (meter2 → hektar)
        luas_q = text("""
            SELECT ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:geo), 4326), 3857)) / 10000 AS luas
        """)
        luas = db.session.execute(luas_q, {'geo': geojson}).scalar()

        # Upload file jika ada
        sertifikat_filename = None  # Initialize sertifikat_filename to prevent undefined variable error
        if file and file.filename:
            filename = secure_filename(file.filename)
            path_file = os.path.join(UPLOAD_FOLDER, "sertifikat", filename)
            os.makedirs(os.path.dirname(path_file), exist_ok=True)  # Create directory if it doesn't exist
            file.save(path_file)
            sertifikat_filename = filename

        # Simpan ke database
        insert_q = text("""
            INSERT INTO data_lahan (
                id_pemilik, nama_lahan, tahun_tanam, varietas_kakao,
                titik_ordinat, luas_lahan, bukti_luas_sertifikat
            ) VALUES (
                :id_pemilik, :nama, :tahun, :varietas,
                ST_SetSRID(ST_GeomFromGeoJSON(:geo),4326), :luas, :sertifikat
            )
        """)
        db.session.execute(insert_q, {
            'id_pemilik': session['user_id'],
            'nama': nama,
            'tahun': tahun,
            'varietas': varietas,
            'geo': geojson,
            'luas': luas,
            'sertifikat': sertifikat_filename
        })
        db.session.commit()
        flash('Lahan berhasil ditambahkan!')
        return redirect(url_for('lahan.kelola_lahan'))

    return render_template('lahan/tambah_lahan.html')

# 📌 Hapus lahan
@lahan_bp.route('/lahan/hapus/<int:id_lahan>')
def hapus_lahan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    db.session.execute(
        text("DELETE FROM data_lahan WHERE id_lahan = :id AND id_pemilik = :user"),
        {'id': id_lahan, 'user': session['user_id']}
    )
    db.session.commit()
    flash("Lahan berhasil dihapus.")
    return redirect(url_for('lahan.kelola_lahan'))


# 📌 Lihat peta
@lahan_bp.route('/lahan/<int:id_lahan>/detail')
def detail_lahan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    lahan = db.session.execute(
        text("""
            SELECT id_lahan, nama_lahan, ST_AsGeoJSON(titik_ordinat) as geojson
            FROM data_lahan
            WHERE id_lahan = :id AND id_pemilik = :uid
        """),
        {'id': id_lahan, 'uid': session['user_id']}
    ).fetchone()

    if not lahan:
        flash("Lahan tidak ditemukan.")
        return redirect(url_for('lahan.kelola_lahan'))

    lahan_dict = dict(lahan._mapping)
    print("DEBUG GEOJSON:", lahan_dict.get('geojson'))  # ← Tambahkan ini

    return render_template('lahan/detail_lahan.html', lahan=lahan_dict)

@lahan_bp.route('/lahan/edit/<int:id_lahan>', methods=['GET', 'POST'])
def edit_lahan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data lahan dengan GeoJSON
    lahan = db.session.execute(
        text("""
            SELECT id_lahan, nama_lahan, tahun_tanam, varietas_kakao,
                   ST_AsGeoJSON(titik_ordinat) as titik_ordinat
            FROM data_lahan
            WHERE id_lahan = :id AND id_pemilik = :uid
        """),
        {'id': id_lahan, 'uid': session['user_id']}
    ).fetchone()

    if not lahan:
        flash("Lahan tidak ditemukan.")
        return redirect(url_for('lahan.kelola_lahan'))

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
            WHERE id_lahan = :id AND id_pemilik = :uid
        """)
        db.session.execute(update_q, {
            'nama': nama,
            'tahun': tahun,
            'varietas': varietas,
            'geo': geojson,
            'luas': luas,
            'id': id_lahan,
            'uid': session['user_id']
        })
        db.session.commit()
        flash('Lahan berhasil diperbarui.')
        return redirect(url_for('lahan.kelola_lahan'))

    return render_template('lahan/edit_lahan.html', lahan=dict(lahan._mapping))
