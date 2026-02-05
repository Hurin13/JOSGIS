from models.db import db

# Model definition for the 'admin' table
class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)

# Functions interacting with the Admin model
def find_admin_by_username(username):
    """
    Find an admin by username using the Admin model.
    Returns an Admin object if found, otherwise None.
    """
    return Admin.query.filter_by(username=username).first()
