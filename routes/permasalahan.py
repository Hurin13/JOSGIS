from flask import Blueprint, render_template, request, redirect, url_for, current_app
from models.db import db
from models.permasalahan import PermasalahanLapang
import os

permasalahan_bp = Blueprint('permasalahan', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@permasalahan_bp.route('/permasalahan/lahan/<int:id_lahan>', methods=['GET', 'POST'])
def permasalahan_lahan(id_lahan):
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        deskripsi = request.form['deskripsi']
        tindakan_penanganan = request.form['tindakan_penanganan']
        catatan_tambahan = request.form['catatan_tambahan']

        # Upload foto
        foto_file = request.files['foto_lapangan']
        foto_filename = None
        if foto_file and foto_file.filename != '':
            foto_filename = foto_file.filename
            foto_path = os.path.join(UPLOAD_FOLDER, 'permasalahan', foto_filename)
            foto_file.save(foto_path)

        data = PermasalahanLapang(
            id_lahan=id_lahan,
            tanggal=tanggal,
            deskripsi=deskripsi,
            tindakan_penanganan=tindakan_penanganan,
            catatan_tambahan=catatan_tambahan,
            foto_lapangan=foto_filename
        )
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('permasalahan.permasalahan_lahan', id_lahan=id_lahan))

    data_permasalahan = PermasalahanLapang.query.filter_by(id_lahan=id_lahan).all()
    return render_template('lahan/permasalahan.html', lahan_id=id_lahan, data_permasalahan=data_permasalahan)
