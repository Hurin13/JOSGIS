from flask import render_template, session, redirect, url_for,request, flash
from sqlalchemy.sql import text
from sqlalchemy import select
from models.db import db
from models.petani import Petani
from models.lahan import DataLahan
from models.monitoring import Monitoring
from models.pemeliharaan import PemeliharaanTanaman
from models.hama import HamaPenyakit
from models.lingkungan import LingkunganCuaca
from models.permasalahan import PermasalahanLapang
from routes.admin import admin_bp


@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))

    list_petani = db.session.execute(select(Petani)).scalars().all()
    total_petani = len(list_petani)

    return render_template('admin/dashboard.html',
                           users=list_petani,
                           total_users=total_petani)


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


@admin_bp.route('/user_detail/<int:user_id>')
def user_detail(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))

    # Mengambil data petani, termasuk lokasi rumah sebagai GeoJSON
    petani_raw = db.session.execute(text("""
        SELECT *, ST_AsGeoJSON(titik_rumah) as lokasi_rumah
        FROM petani 
        WHERE id_pemilik = :user_id
    """), {'user_id': user_id}).fetchone()

    if not petani_raw:
        return "Petani tidak ditemukan", 404
    petani = dict(petani_raw._mapping)

    # ✅ PERBAIKAN: Mengambil data lahan dan mengonversi lokasi ke GeoJSON
    lahan_raw = db.session.execute(text("""
        SELECT 
            *, ST_AsGeoJSON(titik_ordinat) as geojson_lokasi
        FROM data_lahan 
        WHERE id_pemilik = :user_id
    """), {'user_id': user_id}).fetchall()

    # Mengonversi setiap lahan menjadi dictionary
    lahan = [dict(row._mapping) for row in lahan_raw]

    # Ambil data monitoring, pemeliharaan, dll. (Kode sisanya tetap sama)
    monitoring = db.session.execute(
        select(Monitoring).join(DataLahan).filter(DataLahan.id_pemilik == user_id)
        .order_by(Monitoring.tanggal_monitoring.desc()).limit(5)
    ).scalars().all()

    pemeliharaan = db.session.execute(
        select(PemeliharaanTanaman).join(DataLahan).filter(DataLahan.id_pemilik == user_id)
        .order_by(PemeliharaanTanaman.tanggal_aplikasi.desc()).limit(5)
    ).scalars().all()

    hama = db.session.execute(
        select(HamaPenyakit).join(DataLahan).filter(DataLahan.id_pemilik == user_id)
        .order_by(HamaPenyakit.tanggal.desc()).limit(5)
    ).scalars().all()

    lingkungan = db.session.execute(
        select(LingkunganCuaca).join(DataLahan).filter(DataLahan.id_pemilik == user_id)
        .order_by(LingkunganCuaca.tanggal.desc()).limit(5)
    ).scalars().all()

    permasalahan = db.session.execute(
        select(PermasalahanLapang).join(DataLahan).filter(DataLahan.id_pemilik == user_id)
        .order_by(PermasalahanLapang.tanggal.desc()).limit(5)
    ).scalars().all()

    return render_template(
        'admin/user_detail.html',
        petani=petani,
        lahan=lahan,
        monitoring=monitoring,
        pemeliharaan=pemeliharaan,
        hama=hama,
        lingkungan=lingkungan,
        permasalahan=permasalahan
    )


@admin_bp.route('/edit_petani/<int:user_id>', methods=['GET', 'POST'])
def edit_petani(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.login'))

    petani = db.session.get(Petani, user_id)
    if not petani:
        return "Petani tidak ditemukan", 404

    if request.method == 'POST':
        petani.nama_petani = request.form['nama_petani']
        petani.email_petani = request.form['email_petani']
        petani.nik = request.form['nik']
        petani.alamat_petani = request.form['alamat_petani']
        petani.no_telepon = request.form['no_telepon']
        petani.gender = request.form['gender']

        db.session.commit()
        flash('Data petani berhasil diperbarui.', 'success')
        return redirect(url_for('admin.user_detail', user_id=petani.id_pemilik))

    return render_template('admin/edit_petani.html', petani=petani)


# Ganti fungsi hapus_petani yang sudah ada dengan kode ini
@admin_bp.route('/hapus_petani/<int:user_id>', methods=['POST'])
def hapus_petani(user_id):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    try:
        # 1. Cari semua lahan yang dimiliki oleh petani
        lahan_petani = db.session.query(DataLahan).filter_by(id_pemilik=user_id).all()
        lahan_ids = [lahan.id_lahan for lahan in lahan_petani]

        if lahan_ids:
            # 2. Hapus data dari tabel-tabel yang terkait dengan lahan-lahan tersebut
            # Menggunakan .in_() untuk menghapus semua data sekaligus
            Monitoring.query.filter(Monitoring.id_lahan.in_(lahan_ids)).delete(synchronize_session=False)
            PemeliharaanTanaman.query.filter(PemeliharaanTanaman.id_lahan.in_(lahan_ids)).delete(
                synchronize_session=False)
            HamaPenyakit.query.filter(HamaPenyakit.id_lahan.in_(lahan_ids)).delete(synchronize_session=False)
            LingkunganCuaca.query.filter(LingkunganCuaca.id_lahan.in_(lahan_ids)).delete(synchronize_session=False)
            PermasalahanLapang.query.filter(PermasalahanLapang.id_lahan.in_(lahan_ids)).delete(
                synchronize_session=False)

            # 3. Hapus data lahan petani
            DataLahan.query.filter_by(id_pemilik=user_id).delete(synchronize_session=False)

        # 4. Hapus data petani itu sendiri
        petani_to_delete = db.session.get(Petani, user_id)
        if petani_to_delete:
            db.session.delete(petani_to_delete)

        db.session.commit()
        flash('Petani dan semua data terkait berhasil dihapus.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus petani: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard'))
