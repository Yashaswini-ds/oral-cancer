import sqlite3

def add_column():
    conn = sqlite3.connect('instance/oral_cancer.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE patient_record ADD COLUMN doctor_id INTEGER REFERENCES user(id)")
        conn.commit()
        print("Successfully added doctor_id column.")
    except sqlite3.OperationalError as e:
        print(f"Error (column might already exist): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
