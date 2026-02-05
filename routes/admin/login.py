# routes/admin/login.py

from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models.admin import find_admin_by_username
from routes.admin import admin_bp  # ✅ Mengimpor Blueprint dari __init__.py


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Menangani rute login admin.
    """
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin_data = find_admin_by_username(username)

        if admin_data and check_password_hash(admin_data.password, password):
            session['is_admin'] = True
            session['admin_id'] = admin_data.id
            session['username'] = admin_data.username

            flash('Login berhasil! Selamat datang, ' + admin_data.username + '.', 'success')

            return redirect(url_for('admin.dashboard'))
        else:
            flash('Username atau password salah.', 'error')

    return render_template('admin/login.html')
