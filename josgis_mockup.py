from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'josgis_secret_key_2025'

# Setup static dan templates folder
app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')
app.static_folder = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/')
def dashboard():
    """Halaman dashboard JOSGIS mockup"""
    dashboard_data = {
        'total_lahan': '45.8 Ha',
        'total_petani': 24,
        'produktivitas': '3.0 ton/ha',
        'kesehatan_tanaman': 94,
        'panen_bulan_ini': '12.5 ton',
        'rata_curah_hujan': '85 mm'
    }
    return render_template('josgis_dashboard.html', data=dashboard_data)

@app.route('/monitoring')
def monitoring():
    """Halaman monitoring penyakit jeruk"""
    monitoring_data = {
        'total_lahan': '45.8 Ha',
        'total_petani': 24,
        'produktivitas': '3.0 ton/ha',
        'kesehatan_tanaman': 94,
        'panen_bulan_ini': '12.5 ton',
        'rata_curah_hujan': '85 mm'
    }
    return render_template('josgis_dashboard.html', data=monitoring_data)

if __name__ == '__main__':
    print("=" * 60)
    print("🍊 JOSGIS - Jeruk Semboro Geographic Information System")
    print("=" * 60)
    print("Akses aplikasi di: http://localhost:5000")
    print("Tekan CTRL+C untuk stop server")
    print("=" * 60)
    app.run(debug=True, port=5000)
