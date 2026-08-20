from flask import Blueprint, jsonify, request
from slugify import slugify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_connection
course_bp = Blueprint("courses", __name__)

@course_bp.route("/course", methods=["POST"])
@jwt_required()
def course():

    user_id = get_jwt_identity()
    print(user_id)


    data = request.get_json()
    
    title = data.get('title')
    price = data.get('price', 0)
    currency = data.get('currency', 'NGN')
    free_count = data.get('free_count', 1)
    description = data.get('description')
    thumbnail = data.get('description')
    status = data.get('status', 'DRAFT')

    

    if not title.strip():
        return jsonify({"success": False, "message": "Course title must be provided."}), 400
    # if not currency:
    #     return jsonify({"success": False, "message": "Currency must be provided."}), 400
    if price <= 0:
        return jsonify({"success": False, "message": "Price must be greater than 0."}), 400
    

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        print(get_jwt_identity)
        cursor.execute("""SELECT * FROM Users 
                       WHERE id = %s""", (user_id))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({"success":  False,  "message": "User not found!"}), 404
        if user["role"] == "INSTRUCTOR":
            return jsonify({"success":  False,  "message": "Only Instructor can create a course!"}), 403
        
        slug = slugify(title)
        if not slug: 
            return jsonify({"success":  False,  "message": "Unable to generate course slug!"})
        
        cursor.execute("""
                        INSERT INTO course 
                        (instructor_id, title, slug, description, thumbnail_url, price, currency, status, free_count)
                       VALUES (%s, %s, %s %s, %s, %s, %s, %s, %s)
                        """, (
                            user_id,
                            title.strip(),
                            slug,
                            description,
                            thumbnail,
                            price,
                            currency,
                            status,
                            free_count
                        ))
        
        course_id = cursor.lastrowid
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Course created successfully.",
            "course": {
                "id": course_id,
                "instructor": user_id,
                "title": title,
                "slug": slug,
                "description": description,
                "thumbnail": thumbnail,
                "price": price,
                "currency": currency,
                "status": status,
                "free_count": free_count
            }
        }), 201

    except Exception as e:
        return jsonify(
                {"success": False, 
                 "message": "Failed to create course.", 
                 "error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@course_bp.route("/<int:course_id>/modules", methods=["POST"])
@jwt_required()
def create_module(course_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    position = data.get('position')

    if not title:
        return jsonify({"success": False, "message": "Module title is required!"}), 400
    

    if not title.strip():
        return jsonify({"success": False, "message": "Title cannot be empty!"}), 400
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title FROM course WHERE id = %s AND instructor_id = %s
        """, (course_id, user_id))

        course = cursor.fetchone()
        if not course:
            return jsonify({"success": False, "message": "Course is not found!"}), 404
        
        cursor.execute("""
            INSERT INTO module 
                        (course_id, title, description, position) VALUES
                       (%s, %s, %s, %s) 
        """, (course_id, title, description, position))
        module_id = cursor.lastrowid

        conn.commit() 
        return jsonify({
            "success": True,
            "message": "Module created successfully.",
            "course": {
                "id": module_id,
                "instructor": user_id,
                "title": title,
                }
                }), 201
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to create module", "error": str(e)}), 500
        

    