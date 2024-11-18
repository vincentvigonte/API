from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from datetime import datetime

app = Flask(__name__)

# Update the database name here
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_number = db.Column(db.String(64), nullable=False, unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    middle_name = db.Column(db.String(64))
    sex = db.Column(db.String(10), nullable=False) 
    birthday = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_number": self.student_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "sex": self.sex,
            "birthday": self.birthday.strftime("%Y-%m-%d"),
        }

@app.route("/api/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify({"success": True, "data": [student.to_dict() for student in students]}), HTTPStatus.OK

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify(
            {
                "success": False, 
                "error": "Student not found"
            }
        ), HTTPStatus.NOT_FOUND
    
    return jsonify(
        {
            "success": True, 
            "data": student.to_dict()
        }
    ), HTTPStatus.OK

@app.route("/api/students", methods=["POST"])
def create_student():
    if not request.is_json:
        return jsonify(
            {
                "success": False,
                "error": "Content-type must be application/json"
            }
        ), HTTPStatus.BAD_REQUEST
    
    data = request.get_json()
    required_fields = ["student_number", "first_name", "last_name", "sex", "birthday"]

    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "success": False,
                    "error": f"Missing required field: {field}",
                }
            ), HTTPStatus.BAD_REQUEST

    birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()

    new_student = Student(
        student_number=data['student_number'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        middle_name=data.get('middle_name', ''), 
        sex=data['sex'], 
        birthday=birthday
    )

    db.session.add(new_student)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": new_student.to_dict(),
        }
    ), HTTPStatus.CREATED

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None: 
        return jsonify(
            {
                "success": False,
                "error":"Student not found"
            }
        ), HTTPStatus.NOT_FOUND
    
    data = request.get_json()

    if not data: 
        return jsonify(
            {
                "success": False,
                "error": "No data found. Provide data to update the student."
            }
        ), HTTPStatus.BAD_REQUEST
    
    update_fields = ["student_number", "first_name", "last_name", "middle_name", "sex", "birthday"]

    for key in update_fields: 
        if key in data: 
            if key == 'birthday':
                student.birthday = datetime.strptime(data[key], '%Y-%m-%d').date()
            else:
                setattr(student, key, data[key])
    
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": student.to_dict()
        }
    ), HTTPStatus.OK

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None: 
        return jsonify(
            {
                "success": False, 
                "error": "Student not found."
            }
        ), HTTPStatus.NOT_FOUND
    
    db.session.delete(student)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": "Student deleted successfully."
        }
    ), HTTPStatus.OK

@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {
            "success": False,
            "error": "Resource not found"
        }
    ), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_error(error):
    return jsonify(
        {
            "success": False,
            "error": "Internal Server Error"
        }
    ), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(debug=True)


