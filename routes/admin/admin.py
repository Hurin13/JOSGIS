# routes/admin/admin.py
from datetime import datetime, date, timedelta

from flask import render_template, session, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash
from models.db import db
from models.admin import Admin
from models.petani import Petani
from models.lahan import DataLahan
from models.monitoring import Monitoring
from models.pemeliharaan import PemeliharaanTanaman
from models.hama import HamaPenyakit
from models.lingkungan import LingkunganCuaca
from models.permasalahan import PermasalahanLapang
from routes.admin import admin_bp



@admin_bp.route('/tambah_admin', methods=['GET', 'POST'])
def tambah_admin():
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'error')
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        username = request.form['username']
        nama_lengkap = request.form['nama_lengkap']
        password = request.form['password']

        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            flash('Username ini sudah terdaftar. Gunakan username lain.', 'error')
            return redirect(url_for('admin.tambah_admin'))

        # ✅ Hapus argumen method='sha256'
        hashed_password = generate_password_hash(password)

        try:
            new_admin = Admin(
                username=username,
                nama_lengkap=nama_lengkap,
                password=hashed_password
            )
            db.session.add(new_admin)
            db.session.commit()
            flash('Akun admin baru berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {e}', 'error')
            return redirect(url_for('admin.tambah_admin'))

    return render_template('admin/tambah_admin.html')


# Rute Edit dan Hapus Data Monitoring (Admin)
@admin_bp.route('/edit_monitoring_admin/<int:id_monitoring>', methods=['GET', 'POST'])
def edit_monitoring_admin(id_monitoring):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    monitoring_data = Monitoring.query.get_or_404(id_monitoring)

    if request.method == 'POST':
        try:
            # Memperbarui semua kolom yang bisa diedit dari form
            monitoring_data.tanggal_monitoring = datetime.strptime(request.form['tanggal_monitoring'],
                                                                   '%Y-%m-%d').date()
            monitoring_data.jumlah_pohon_mati = int(request.form.get('jumlah_pohon_mati', 0))
            monitoring_data.jenis_hama = request.form.get('jenis_hama', '')
            monitoring_data.produktivitas = float(request.form.get('produktivitas', 0.0))
            monitoring_data.tinggi_tanaman = float(request.form.get('tinggi_tanaman', 0.0))
            monitoring_data.daun_menguning = 'daun_menguning' in request.form
            monitoring_data.kerusakan_batang = request.form.get('kerusakan_batang', '')

            db.session.commit()
            flash('Data monitoring berhasil diperbarui.', 'success')

            # ✅ PERBAIKAN: Mengambil id_pemilik dari relasi lahan
            return redirect(url_for('admin.user_detail', user_id=monitoring_data.lahan.id_pemilik))
        except ValueError as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Kesalahan format data (mis. harus angka, bukan teks). Detail: {e}', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Terjadi kesalahan server. Detail: {e}', 'error')

    return render_template('admin/edit_monitoring.html', data=monitoring_data)


@admin_bp.route('/hapus_monitoring_admin/<int:id_monitoring>', methods=['POST'])
def hapus_monitoring_admin(id_monitoring):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    monitoring_data = Monitoring.query.get_or_404(id_monitoring)
    petani_id = monitoring_data.lahan.id_pemilik
    try:
        db.session.delete(monitoring_data)
        db.session.commit()
        flash('Data monitoring berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))


# Rute Edit dan Hapus Data Pemeliharaan (Admin)
@admin_bp.route('/edit_pemeliharaan_admin/<int:id_pemeliharaan>', methods=['GET', 'POST'])
def edit_pemeliharaan_admin(id_pemeliharaan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    pemeliharaan_data = PemeliharaanTanaman.query.get_or_404(id_pemeliharaan)

    if request.method == 'POST':
        try:
            # ✅ Memperbarui semua kolom yang bisa diedit dari form
            pemeliharaan_data.pemangkasan_kakao = 'pemangkasan_kakao' in request.form
            pemeliharaan_data.tanggal_pemangkasan_kakao = datetime.strptime(
                request.form['tanggal_pemangkasan_kakao'], '%Y-%m-%d').date() if request.form[
                'tanggal_pemangkasan_kakao'] else None

            pemeliharaan_data.pemangkasan_penaung = 'pemangkasan_penaung' in request.form
            pemeliharaan_data.tanggal_pemangkasan_penaung = datetime.strptime(
                request.form['tanggal_pemangkasan_penaung'], '%Y-%m-%d').date() if request.form[
                'tanggal_pemangkasan_penaung'] else None

            pemeliharaan_data.penyiangan_gulma = 'penyiangan_gulma' in request.form

            pemeliharaan_data.pemupukan = 'pemupukan' in request.form
            pemeliharaan_data.tanggal_aplikasi = datetime.strptime(
                request.form['tanggal_aplikasi'], '%Y-%m-%d').date() if request.form['tanggal_aplikasi'] else None

            pemeliharaan_data.jenis_pupuk = request.form['jenis_pupuk']
            pemeliharaan_data.jumlah_dosis = float(request.form['jumlah_dosis']) if request.form[
                'jumlah_dosis'] else None

            db.session.commit()
            flash('Data pemeliharaan berhasil diperbarui.', 'success')

            # ✅ PERBAIKAN: Mengambil id_pemilik dari relasi lahan
            return redirect(url_for('admin.user_detail', user_id=pemeliharaan_data.lahan.id_pemilik))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(
                f'Gagal memperbarui data: Kesalahan format data. Pastikan semua kolom terisi dengan benar. Detail: {e}',
                'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Terjadi kesalahan server. Detail: {e}', 'error')

    return render_template('admin/edit_pemeliharaan.html', data=pemeliharaan_data)


@admin_bp.route('/hapus_pemeliharaan_admin/<int:id_pemeliharaan>', methods=['POST'])
def hapus_pemeliharaan_admin(id_pemeliharaan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    pemeliharaan_data = PemeliharaanTanaman.query.get_or_404(id_pemeliharaan)
    petani_id = pemeliharaan_data.lahan.id_pemilik
    try:
        db.session.delete(pemeliharaan_data)
        db.session.commit()
        flash('Data pemeliharaan berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))


# Rute Edit dan Hapus Data Hama (Admin)
@admin_bp.route('/edit_hama_admin/<int:id_serangan>', methods=['GET', 'POST'])
def edit_hama_admin(id_serangan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    hama_data = HamaPenyakit.query.get_or_404(id_serangan)

    if request.method == 'POST':
        try:
            # ✅ Memperbarui semua kolom hama_penyakit dari form
            hama_data.tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
            hama_data.jenis_hama = request.form['jenis_hama']
            hama_data.tingkat_serangan_hama = request.form['tingkat_serangan_hama']
            hama_data.luas_terdampak = float(request.form['luas_terdampak']) if request.form['luas_terdampak'] else None
            hama_data.pengendalian_dilakukan = 'pengendalian_dilakukan' in request.form

            # Kolom untuk jenis pengendalian
            if 'jenis_pengendalian_hama' in request.form:
                hama_data.jenis_pengendalian_hama = request.form['jenis_pengendalian_hama']
            else:
                hama_data.jenis_pengendalian_hama = None

            hama_data.keterangan_pengendalian_hama = request.form.get('keterangan_pengendalian_hama')

            if 'jenis_pengendalian_penyakit' in request.form:
                hama_data.jenis_pengendalian_penyakit = request.form['jenis_pengendalian_penyakit']
            else:
                hama_data.jenis_pengendalian_penyakit = None

            hama_data.keterangan_pengendalian_penyakit = request.form.get('keterangan_pengendalian_penyakit')

            db.session.commit()
            flash('Data hama berhasil diperbarui.', 'success')

            # ✅ Mengambil id_pemilik dari relasi lahan
            return redirect(url_for('admin.user_detail', user_id=hama_data.lahan.id_pemilik))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(
                f'Gagal memperbarui data: Kesalahan format data. Pastikan semua kolom terisi dengan benar. Detail: {e}',
                'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Terjadi kesalahan server. Detail: {e}', 'error')

    return render_template('admin/edit_hama.html', data=hama_data)


@admin_bp.route('/hapus_hama_admin/<int:id_serangan>', methods=['POST'])
def hapus_hama_admin(id_serangan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    hama_data = HamaPenyakit.query.get_or_404(id_serangan)
    petani_id = hama_data.lahan.id_pemilik
    try:
        db.session.delete(hama_data)
        db.session.commit()
        flash('Data hama berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))


# Rute Edit dan Hapus Data Lingkungan (Admin)
@admin_bp.route('/edit_lingkungan_admin/<int:id_lingkungan_cuaca>', methods=['GET', 'POST'])
def edit_lingkungan_admin(id_lingkungan_cuaca):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    lingkungan_data = LingkunganCuaca.query.get_or_404(id_lingkungan_cuaca)

    if request.method == 'POST':
        try:
            # ✅ Memperbarui semua kolom lingkungan_cuaca dari form
            lingkungan_data.tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
            lingkungan_data.curah_hujan = float(request.form['curah_hujan']) if request.form['curah_hujan'] else None
            lingkungan_data.drainase = request.form.get('drainase')
            lingkungan_data.naungan = request.form.get('naungan')
            # Catatan: 'foto_lingkungan' biasanya tidak diedit di form ini,
            # tetapi bisa ditambahkan jika diperlukan.

            db.session.commit()
            flash('Data lingkungan berhasil diperbarui.', 'success')

            # ✅ Mengambil id_pemilik dari relasi lahan
            return redirect(url_for('admin.user_detail', user_id=lingkungan_data.lahan.id_pemilik))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(
                f'Gagal memperbarui data: Kesalahan format data. Pastikan semua kolom terisi dengan benar. Detail: {e}',
                'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Terjadi kesalahan server. Detail: {e}', 'error')

    return render_template('admin/edit_lingkungan.html', data=lingkungan_data)


@admin_bp.route('/hapus_lingkungan_admin/<int:id_lingkungan>', methods=['POST'])
def hapus_lingkungan_admin(id_lingkungan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    lingkungan_data = LingkunganCuaca.query.get_or_404(id_lingkungan)
    petani_id = lingkungan_data.lahan.id_pemilik
    try:
        db.session.delete(lingkungan_data)
        db.session.commit()
        flash('Data lingkungan berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))


# Rute Edit dan Hapus Data Permasalahan (Admin)
@admin_bp.route('/edit_permasalahan_admin/<int:id_permasalahan_lapang>', methods=['GET', 'POST'])
def edit_permasalahan_admin(id_permasalahan_lapang):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    permasalahan_data = PermasalahanLapang.query.get_or_404(id_permasalahan_lapang)

    if request.method == 'POST':
        try:
            # ✅ Memperbarui semua kolom dari formulir
            permasalahan_data.tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d').date()
            permasalahan_data.deskripsi = request.form['deskripsi']
            permasalahan_data.tindakan_penanganan = request.form['tindakan_penanganan']
            permasalahan_data.catatan_tambahan = request.form['catatan_tambahan']

            # Catatan: 'foto_lapangan' tidak diupdate di sini. Jika diperlukan,
            # Anda harus menambahkan logika untuk menangani upload file.

            db.session.commit()
            flash('Data permasalahan berhasil diperbarui.', 'success')

            # ✅ Mengambil id_pemilik dari relasi lahan
            return redirect(url_for('admin.user_detail', user_id=permasalahan_data.lahan.id_pemilik))
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(
                f'Gagal memperbarui data: Kesalahan format data. Pastikan semua kolom terisi dengan benar. Detail: {e}',
                'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui data: Terjadi kesalahan server. Detail: {e}', 'error')

    return render_template('admin/edit_permasalahan.html', data=permasalahan_data)


@admin_bp.route('/hapus_permasalahan_admin/<int:id_permasalahan>', methods=['POST'])
def hapus_permasalahan_admin(id_permasalahan):
    if not session.get('is_admin'):
        flash('Anda tidak memiliki izin.', 'error')
        return redirect(url_for('admin.login'))

    permasalahan_data = PermasalahanLapang.query.get_or_404(id_permasalahan)
    petani_id = permasalahan_data.lahan.id_pemilik
    try:
        db.session.delete(permasalahan_data)
        db.session.commit()
        flash('Data permasalahan berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus data: {e}', 'error')

    return redirect(url_for('admin.user_detail', user_id=petani_id))
