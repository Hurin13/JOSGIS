from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db
from models.petani import Petani
import requests
# ✅ TAMBAHAN: Impor objek google dari Flask-Dance
from flask_dance.contrib.google import google

auth_bp = Blueprint('auth', __name__)
def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {'User-Agent': 'flask-app-mahardhika'}

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', '')
    except Exception as e:
        print("Reverse geocoding failed:", e)

    return ''


# ROUTE REGISTER
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # ✅ PERBAIKAN: Jika user sudah login, arahkan ke dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))
    if request.method == 'POST':
        nik = request.form['nik']
        nama = request.form['nama']
        gender = request.form['gender']
        no_hp = request.form['no_hp']
        email = request.form['email']
        password = request.form['password']
        titik_lat = request.form['titik_lat']
        titik_lng = request.form['titik_lng']
        alamat = request.form['alamat']

        if not nik.isdigit() or len(nik) != 16:
            flash("NIK harus terdiri dari 16 digit angka.", "error")
            return redirect(url_for('auth.register'))

        if Petani.query.filter_by(nik=nik).first():
            flash("NIK sudah terdaftar.", "error")
            return redirect(url_for('auth.register'))

        if Petani.query.filter_by(email_petani=email).first():
            flash("Email sudah terdaftar.", "error")
            return redirect(url_for('auth.register'))

        new_petani = Petani(
            nik=nik,
            nama_petani=nama,
            gender=gender,
            no_telepon=no_hp,
            email_petani=email,
            password_hash=generate_password_hash(password),
            alamat_petani=alamat,
            titik_rumah=f'SRID=4326;POINT({titik_lng} {titik_lat})'
        )

        db.session.add(new_petani)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ROUTE LOGIN
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # ✅ PERBAIKAN: Jika user sudah login, arahkan ke dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        petani = Petani.query.filter_by(email_petani=email).first()
        if petani and petani.password_hash and check_password_hash(petani.password_hash, password):
            session['user_id'] = petani.id_pemilik
            session['user_nama'] = petani.nama_petani
            flash("Login successful!", "success")
            return redirect(url_for('dashboard.dashboard'))

        flash('Email atau password salah', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


# ✅ TAMBAHAN: Rute login via Google
@auth_bp.route('/login-google', endpoint='login_google')
def login_google():
    if not google.authorized:
        return redirect(url_for('google.login'))
    try:
        resp = google.get('/oauth2/v2/userinfo')
        resp.raise_for_status()
        google_info = resp.json()
    except Exception as e:
        # ✅ KOREKSI: Tangani error token expired secara khusus
        if "token_expired" in str(e):
            flash("Your Google login session has expired. Please try again.", 'error')
            # Arahkan kembali ke halaman login Google
            return redirect(url_for('google.login'))
        else:
            # Tangani error lainnya seperti biasa
            flash(f'Gagal mengambil informasi dari Google: {str(e)}', 'error')
            return redirect(url_for('auth.login'))

    # Gunakan metode bantu yang baru dibuat untuk mencari atau membuat pengguna
    user = Petani.create_or_get_from_google(google_info)

    # Simpan informasi pengguna di sesi
    session['logged_in'] = True
    session['user_id'] = user.id_pemilik
    session['user_nama'] = user.nama_petani
    session['is_admin'] = False

    if user.needs_profile_completion():
        flash('Please complete your profile to continue.', 'info')
        return redirect(url_for('auth.complete_profile'))

    flash('Successfully logged in with Google!', 'success')
    return redirect(url_for('dashboard.dashboard'))


# Di auth.py

@auth_bp.route('/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    # Check if user is logged in
    if not session.get('user_id'):
        flash('You must log in first.', 'error')
        return redirect(url_for('auth.login'))

    # Get current user
    user = Petani.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))

    # Check if user is Google user and needs profile completion
    if not user.google_id or not user.needs_profile_completion():
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        nik = request.form['nik']
        gender = request.form['gender']
        no_telepon = request.form['no_telepon']
        alamat = request.form['alamat']
        titik_lat = request.form['titik_lat']
        titik_lng = request.form['titik_lng']
        password = request.form.get('password')  # ✅ Tambahan: Dapatkan password dari formulir

        # Validate NIK
        if not nik.isdigit() or len(nik) != 16:
            flash("NIK harus terdiri dari 16 digit angka.", "error")
            return render_template('complete_profile.html')

        # Check if NIK already exists (excluding current user)
        existing_nik = Petani.query.filter(Petani.nik == nik, Petani.id_pemilik != user.id_pemilik).first()
        if existing_nik:
            flash("NIK sudah terdaftar oleh pengguna lain.", "error")
            return render_template('complete_profile.html')

        # Update user profile
        try:
            user.nik = nik
            user.gender = gender
            user.no_telepon = no_telepon
            user.alamat_petani = alamat
            user.titik_rumah = f'SRID=4326;POINT({titik_lng} {titik_lat})'

            # ✅ Tambahan: Simpan password jika disediakan
            if password:
                user.password_hash = generate_password_hash(password)

            db.session.commit()
            flash("Profile completed successfully!", "success")
            return redirect(url_for('dashboard.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return render_template('complete_profile.html')

    return render_template('complete_profile.html')


# ROUTE LOGOUT
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reverse_geocode', methods=['POST'])
def get_address_from_coords():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    alamat = reverse_geocode(lat, lon)
    return {'alamat': alamat}
