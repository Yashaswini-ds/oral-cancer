from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'patient' or 'doctor'
    specialization = db.Column(db.String(150), nullable=True) # Only for doctors

class PatientRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Assigned doctor
    timestamp = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    
    # Store symptoms as individual columns for better querying query
    pain_level = db.Column(db.String(50))
    bleeding = db.Column(db.String(50))
    swelling = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    history = db.Column(db.Text)
    habits = db.Column(db.String(200)) # stored as comma separated string
    tobacco_years = db.Column(db.String(50))
    alcohol_years = db.Column(db.String(50))
    smoking_years = db.Column(db.String(50))
    trismus_test = db.Column(db.String(50))
    mouth_pain = db.Column(db.String(50))
    extra_details = db.Column(db.Text)
    
    status = db.Column(db.String(50), default="Pending")
    doctor_replies = db.Column(db.Text) # JSON string or simple text for now
    patient_replies = db.Column(db.Text) # JSON string or complicated text
    prediction = db.Column(db.String(100))
    confidence = db.Column(db.String(50))
    pdf_path = db.Column(db.String(200))
    audio_path = db.Column(db.String(200))
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('patient_records', lazy=True))
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref=db.backref('doctor_cases', lazy=True))
