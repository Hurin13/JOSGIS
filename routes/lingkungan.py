from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.db import db
from models.lingkungan import LingkunganCuaca
from models.lahan import DataLahan
import os
from werkzeug.utils import secure_filename

lingkungan_bp = Blueprint('lingkungan', __name__)
UPLOAD_FOLDER = 'static/uploads'

@lingkungan_bp.route('/lahan/<int:id_lahan>/lingkungan', methods=['GET', 'POST'])
def tambah_lingkungan(id_lahan):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    lahan = DataLahan.query.get_or_404(id_lahan)

    if request.method == 'POST':
        tanggal = request.form.get('tanggal')
        curah_hujan = request.form.get('curah_hujan')
        drainase = request.form.get('drainase')
        naungan = request.form.get('naungan')

        # --- Upload file foto (opsional) ---
        foto_lingkungan = None  # inisialisasi biar aman
        file = request.files.get('foto_lingkungan')

        if file and file.filename:
            filename = secure_filename(file.filename)

            # pastikan folder tujuan ada
            save_dir = os.path.join(UPLOAD_FOLDER, "lingkungan")
            os.makedirs(save_dir, exist_ok=True)

            filepath = os.path.join(save_dir, filename)
            file.save(filepath)
            foto_lingkungan = filename  # hanya simpan nama file ke DB

        # --- Simpan data ke DB ---
        data = LingkunganCuaca(
            id_lahan=id_lahan,
            tanggal=tanggal,
            curah_hujan=curah_hujan,
            drainase=drainase,
            naungan=naungan,
            foto_lingkungan=foto_lingkungan  # bisa None jika tidak upload
        )

        db.session.add(data)
        db.session.commit()

        flash('Data lingkungan & cuaca berhasil disimpan.')
        return redirect(url_for('lingkungan.tambah_lingkungan', id_lahan=id_lahan))

    data_lingkungan = LingkunganCuaca.query.filter_by(id_lahan=id_lahan).all()

    return render_template('lahan/lingkungan.html', lahan=lahan, data_lingkungan=data_lingkungan)
