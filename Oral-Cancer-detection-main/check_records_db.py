from app import app, db, PatientRecord
import json

with app.app_context():
    records = PatientRecord.query.all()
    print(f"Total records: {len(records)}")
    for r in records:
        print(f"ID: {r.id}, Prediction: {r.prediction}, ImagePath: {r.image_path}, DoctorID: {r.doctor_id}")
        if r.prediction is None:
            print(f"WARNING: ID {r.id} has NULL prediction")
        if r.image_path is None:
             print(f"WARNING: ID {r.id} has NULL image_path")
