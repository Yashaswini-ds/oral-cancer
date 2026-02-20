from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    if inspector.has_table('user'):
        columns = [c['name'] for c in inspector.get_columns('user')]
        print(f"User columns: {columns}")
        if 'specialization' in columns:
            print("Status: Column 'specialization' EXISTS.")
        else:
            print("Status: Column 'specialization' MISSING.")
    else:
        print("Table 'user' does not exist.")
