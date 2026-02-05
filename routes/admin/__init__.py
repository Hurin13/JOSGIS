# routes/admin/__init__.py
from flask import Blueprint

# Definisi Blueprint di sini
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ✅ Impor dan daftarkan rute-rute admin
from . import login
from . import dashboard
from . import edit_lahan
from . import admin
from . import api_admin # Ini akan menjalankan kode di api_admin.py

# ✅ Mendaftarkan Blueprint api_admin_bp dengan URL /api
from routes.admin.api_admin import api_admin_bp # Impor blueprint dari file api_admin.py
admin_bp.register_blueprint(api_admin_bp, url_prefix='/api') # Gunakan url_prefix di sini
