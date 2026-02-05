from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import db
from models.pemeliharaan import PemeliharaanTanaman
from models.lahan import DataLahan

pemeliharaan_bp = Blueprint('pemeliharaan', __name__)

# 📌 Tampilkan halaman pemeliharaan lahan tertentu
@pemeliharaan_bp.route('/lahan/<int:id_lahan>/pemeliharaan')
def pemeliharaan_lahan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    lahan = DataLahan.query.get_or_404(id_lahan)
    data_pemeliharaan = PemeliharaanTanaman.query.filter_by(id_lahan=id_lahan).all()

    return render_template('lahan/pemeliharaan.html', lahan=lahan, data_pemeliharaan=data_pemeliharaan)

# 📌 Tambah data pemeliharaan
@pemeliharaan_bp.route('/lahan/<int:id_lahan>/pemeliharaan/tambah', methods=['POST'])
def tambah_pemeliharaan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    pemangkasan_kakao = 'pemangkasan_kakao' in request.form
    tanggal_pk = request.form.get('tanggal_pemangkasan_kakao') or None

    pemangkasan_penaung = 'pemangkasan_penaung' in request.form
    tanggal_pp = request.form.get('tanggal_pemangkasan_penaung') or None

    penyiangan_gulma = 'penyiangan_gulma' in request.form

    pemupukan = 'pemupukan' in request.form
    tanggal_pupuk = request.form.get('tanggal_aplikasi') or None
    jenis_pupuk = request.form.get('jenis_pupuk')
    dosis = request.form.get('jumlah_dosis') or 0

    # Jika jenis_pupuk == "Lainnya", ambil input text
    if jenis_pupuk == "Lainnya":
        jenis_pupuk = request.form.get('jenis_pupuk_lainnya')

    data = PemeliharaanTanaman(
        id_lahan=id_lahan,
        pemangkasan_kakao=pemangkasan_kakao,
        tanggal_pemangkasan_kakao=tanggal_pk,
        pemangkasan_penaung=pemangkasan_penaung,
        tanggal_pemangkasan_penaung=tanggal_pp,
        penyiangan_gulma=penyiangan_gulma,
        pemupukan=pemupukan,
        tanggal_aplikasi=tanggal_pupuk,
        jenis_pupuk=jenis_pupuk,
        jumlah_dosis=dosis
    )
    db.session.add(data)
    db.session.commit()

    flash('Data pemeliharaan berhasil ditambahkan')
    return redirect(url_for('pemeliharaan.pemeliharaan_lahan', id_lahan=id_lahan))
