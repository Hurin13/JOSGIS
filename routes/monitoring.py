import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models.db import db
from models.monitoring import Monitoring

monitoring_bp = Blueprint('monitoring', __name__)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@monitoring_bp.route('/monitoring/<int:id_lahan>')
def tampil_monitoring(id_lahan):
    data_monitoring = Monitoring.query.filter_by(id_lahan=id_lahan).all()
    return render_template('lahan/monitoring.html', data_monitoring=data_monitoring, id_lahan=id_lahan)

@monitoring_bp.route('/monitoring/<int:id_lahan>/tambah', methods=['GET', 'POST'])
def tambah_monitoring(id_lahan):
    if request.method == 'POST':
        tanggal = request.form['tanggal_monitoring']
        pohon_mati = request.form.get('jumlah_pohon_mati', type=int)
        hama = request.form['jenis_hama']
        produktivitas = request.form.get('produktivitas', type=float)
        tinggi = request.form.get('tinggi_tanaman', type=float)
        daun_menguning = request.form.get('daun_menguning') == 'true'  # karena pakai select
        kerusakan = request.form['kerusakan_batang']
        foto = request.files['foto_tanaman']

        filename = None
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(UPLOAD_FOLDER, "monitoring", filename))

        data = Monitoring(
            id_lahan=id_lahan,
            tanggal_monitoring=tanggal,
            jumlah_pohon_mati=pohon_mati,
            jenis_hama=hama,
            produktivitas=produktivitas,
            tinggi_tanaman=tinggi,
            daun_menguning=daun_menguning,
            kerusakan_batang=kerusakan,
            foto_tanaman=filename
        )

        db.session.add(data)
        db.session.commit()

        flash('Berhasil menambahkan data monitoring!', 'success')
        return redirect(url_for('lahan.detail_lahan', id_lahan=id_lahan))

    return render_template('lahan/monitoring.html', id_lahan=id_lahan)
