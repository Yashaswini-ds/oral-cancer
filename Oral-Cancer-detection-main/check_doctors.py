import sqlite3

def check_doctors():
    conn = sqlite3.connect('instance/oral_cancer.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, specialization FROM user WHERE role='doctor'")
    doctors = cursor.fetchall()
    conn.close()
    
    if doctors:
        print(f"Found {len(doctors)} doctors:")
        for doc in doctors:
            print(doc)
    else:
        print("No doctors found in the database.")

if __name__ == "__main__":
    check_doctors()
