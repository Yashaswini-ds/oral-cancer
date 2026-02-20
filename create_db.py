from app import app, db
from models import Appointment

with app.app_context():
    db.create_all()
    print("Database tables created (including Appointment if it didn't exist).")
