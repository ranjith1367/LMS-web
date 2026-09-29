from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
print(bcrypt.generate_password_hash("Admin@123").decode("utf-8"))
print(bcrypt.generate_password_hash("Arun@123").decode("utf-8"))
print(bcrypt.generate_password_hash("Ravi Shankar").decode("utf-8"))
print(bcrypt.generate_password_hash("Sathish@123").decode("utf-8"))
print(bcrypt.generate_password_hash("Pradeep@27").decode("utf-8"))
