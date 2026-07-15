from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError
from extension import bcrypt
from db import get_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if not fullname or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long"}), 400

    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)",
                (fullname, email, hashed_password),
            )
            conn.commit()
    except e:
        jsonify({"success": False, "message": "db connection failed"})
    finally:
        conn.close()
    print(data)
    return jsonify({"success": True, "message": "User registered successfully."}), 201