from werkzeug.security import generate_password_hash, check_password_hash

try:
    print("Testing default hash...")
    pw_hash = generate_password_hash("password123")
    print(f"Default hash success: {pw_hash[:10]}...")
    
    print("Testing scrypt hash...")
    scrypt_hash = generate_password_hash("password123", method='scrypt')
    print(f"Scrypt hash success: {scrypt_hash[:10]}...")
    
except Exception as e:
    print(f"Hashing failed: {e}")
