from flask_bcrypt import Bcrypt 
# import secrets
from config import Config
bcrypt = Bcrypt()

# print(bcrypt.generate_password_hash("Admin123").decode("utf-8"))

# print(secrets.token_hex(32))
# print(secrets.token_hex(32))

print("Hello")

print("Google Client ID:", Config.GOOGLE_CLIENT_ID)
print("Google Client Secret:", bool(Config.GOOGLE_CLIENT_SECRET))