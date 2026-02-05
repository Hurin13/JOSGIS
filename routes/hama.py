from flask import Blueprint, render_template, request, redirect, url_for, session
from models.db import db
from models.hama import HamaPenyakit
from models.lahan import DataLahan

hama_bp = Blueprint('hama', __name__)

@hama_bp.route('/lahan/<int:id_lahan>/hama')
def tampil_hama(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    lahan = DataLahan.query.get_or_404(id_lahan)
    data_hama = HamaPenyakit.query.filter_by(id_lahan=id_lahan).all()
    return render_template('lahan/hama.html', lahan=lahan, data_hama=data_hama)

@hama_bp.route('/lahan/<int:id_lahan>/hama/tambah', methods=['POST'])
def tambah_hama(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data dari form
    tanggal = request.form.get('tanggal')
    jenis_hama = request.form.get('jenis_hama')
    tingkat_serangan_hama = request.form.get('tingkat_serangan_hama')
    luas_terdampak = request.form.get('luas_terdampak')
    pengendalian_dilakukan = True if request.form.get('pengendalian_dilakukan') == 'ya' else False

    jenis_pengendalian_hama = request.form.get('jenis_pengendalian_hama')
    keterangan_pengendalian_hama = request.form.get('keterangan_pengendalian_hama')
    jenis_pengendalian_penyakit = request.form.get('jenis_pengendalian_penyakit')
    keterangan_pengendalian_penyakit = request.form.get('keterangan_pengendalian_penyakit')

    # Buat objek
    data = HamaPenyakit(
        id_lahan=id_lahan,
        tanggal=tanggal,
        jenis_hama=jenis_hama,
        tingkat_serangan_hama=tingkat_serangan_hama,
        luas_terdampak=luas_terdampak,
        pengendalian_dilakukan=pengendalian_dilakukan,
        jenis_pengendalian_hama=jenis_pengendalian_hama,
        keterangan_pengendalian_hama=keterangan_pengendalian_hama,
        jenis_pengendalian_penyakit=jenis_pengendalian_penyakit,
        keterangan_pengendalian_penyakit=keterangan_pengendalian_penyakit
    )

    db.session.add(data)
    db.session.commit()
    return redirect(url_for('hama.tampil_hama', id_lahan=id_lahan))
