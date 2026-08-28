from flask import Blueprint, jsonify, request
from slugify import slugify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_connection
from utils.decorators import instructor_required
course_bp = Blueprint("courses", __name__)

@course_bp.route("/course", methods=["POST"])
@jwt_required()
def course():

    user_id = get_jwt_identity()
    # print(user_id)


    data = request.get_json()
    if not data:
        return jsonify({"success":False, "message":"No input is passed."}), 400
    
    title = data.get('title')
    price = data.get('price', 0)
    currency = data.get('currency', 'NGN')
    free_count = data.get('free_count', 1)
    description = data.get('description')
    thumbnail = data.get('thumbnail')
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
        # print(get_jwt_identity)
        cursor.execute("""SELECT * FROM Users 
                       WHERE id = %s""", (user_id))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({"success":  False,  "message": "User not found!"}), 404
        if user["role"] != "INSTRUCTOR":
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
    if not data:
        return jsonify({"success": False, "message": "Request body is required!"}), 400
    title = data.get('title')
    description = data.get('description')
    position = data.get('position')

    if not title:
        return jsonify({"success": False, "message": "Module title is required!"}), 400
    

    if not title.strip():
        return jsonify({"success": False, "message": "Module title cannot be empty!"}), 400
    
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
                        (course_id, title, description, module_position) VALUES
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
        return jsonify(
                        {
                        "success": False, 
                         "message": "Failed to create module", "error": str(e)}), 500
    finally:
        if conn:
            conn.close()
        

@course_bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):

    user_id = get_jwt_identity()
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM course 
                           WHERE id = %s AND instructor_id = %s""", 
                           (course_id, user_id))
            
            course = cursor.fetchone()

            if not course:
                return jsonify({"success": False, "message": "Course not found."}), 404
            
            return jsonify({"success": True, "message": f"Course found - {course["title"]}", "courses": course}), 200

        
    except Exception as e:
        return jsonify(
                        {
                        "success": False, 
                         "message": "Failed to create module", "error": str(e)}), 500
    

@course_bp.route("/<int:course_id>/modules", methods=["GET"])
@jwt_required()
def get_course_module(course_id):

    user_id = get_jwt_identity()
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM course 
                           WHERE id = %s AND instructor_id = %s""", 
                           (course_id, user_id))
            
            course = cursor.fetchone()

            if not course:
                return jsonify({"success": False, "message": "Course not found."}), 404
            
            cursor.execute("""
                            SELECT id, course_id, title, description, position FROM module 
                           WHERE course_id = %s ORDER BY position ASC
                        """, (course_id))
            
            module = cursor.fetchall()
            if not module:
                return jsonify({"success": False, "message": "Module not found."}), 404

            return jsonify({"success": True, "message": "All modules", 
                                "course": {
                                    "course_id": course["id"],
                                    "title": course["title"],
                                },
                                "modules": module
                                }), 200

        
    except Exception as e:
        return jsonify(
                        {
                        "success": False, 
                         "message": "Failed to retrieve module", "error": str(e)}), 500
    


@course_bp.route("/modules/<int:module_id>", methods=["GET"])
@jwt_required()
@instructor_required
def get_module(module_id):

    user_id = get_jwt_identity()

    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    m.id,
                    m.course_id,
                    m.title,
                    m.description,
                    m.module_position,
                    m.created_at,
                    m.updated_at
                FROM module m
                INNER JOIN course c
                    ON m.course_id = c.id
                WHERE m.id = %s
                AND c.instructor_id = %s
            """, (module_id, user_id))

            module = cursor.fetchone()

            if not module:
                return jsonify({
                    "success": False,
                    "message": "Module not found."
                }), 404

            return jsonify({
                "success": True,
                "module": module
            }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Failed to retrieve module.",
            "error": str(e)
        }), 500

    finally:
        if conn:
            conn.close()



@course_bp.route("/modules/<int:module_id>", methods=["PUT"])
@jwt_required()
@instructor_required
def update_module(module_id):

    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message":"Request body is required."})
    
    title = data.get("title")
    description = data.get("description")
    position = data.get("position")

    if not title:
        if not title.strip():
            return jsonify({"success": False, "message":  "Module title must not be empty."})
        
    if not description.strip():
        return jsonify({"success": False, "message":  "Module description must not be empty."})
    

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:

            cursor.execute("""
            SELECT m.id, m.title, m.description, m.module_position, c.id FROM module m
            INNER JOIN course c ON m.course_id = m.id               
            WHERE m.id = %s AND c.instructor_id = %s
        """, (module_id, user_id))
            
            module = cursor.fetchone()

            if not module:
                return jsonify({"success": False, "message":"Module not found or you do not own any module."}), 404
            
            new_title = title
            new_description = description 
            new_position = position

            cursor.execute("""
                                UPDATE module SET title = %s, description = %s, position = %s
                                WHERE id = %s;
                           """, new_title, new_description, new_position, module_id)

        conn.commit()
        return jsonify({
                    "success": True,
                    "message": "Module updated successfully.",
                    "module": {
                        "id": module_id,
                        "title": new_title,
                        "description": new_description
                    }
                }), 200
                
    except Exception as e:
        return jsonify({
                    "success": True,
                    "message": "Failed to update module."})
    finally:
        conn.close()



@course_bp.route("course/module/<int:module_id>", methods=["DELETE"])
@jwt_required()
@instructor_required
def delete_module(module_id):
    user_id = get_jwt_identity()
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.id FROM module m INNER JOIN course c ON m.course_id = c.id
                WHERE m.id = %s and c.instructor_id = %s
            """, (module_id, user_id))

            module = cursor.fetchone()
            if not module:
                return jsonify({"success": False , "message": "Module not found."}), 400
            
            cursor.execute("""
                    DELETE FROM module WHERE id = %s
                """, module)
            conn.commit()
            return jsonify({"success": True, "message": "Module has been deleted successfully."}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": "Failed deleting module."}), 500
    finally:
        conn.close()


@course_bp.route("course/module/lesson", methods=["POST"])
@jwt_required()
@instructor_required
def create_lesson():
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        return jsonify({"success":  False,  "message":"Request body is required."}), 400
    
