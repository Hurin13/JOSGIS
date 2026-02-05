class Config:
    # Replace with a secure random key in production
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:%40Gongyoo13@localhost:5432/web_gis_jambewangi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
