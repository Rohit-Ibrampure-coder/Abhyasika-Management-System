from werkzeug.security import generate_password_hash

password = generate_password_hash("admin123")

print(password)