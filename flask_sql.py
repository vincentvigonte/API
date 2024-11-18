from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    published_year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    quantity = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "published_year": self.published_year,
            "isbn": self.isbn,
            "quantity": self.quantity,
        }

@app.route("/api/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify({"success": True, "data": [book.to_dict() for book in books]}), HTTPStatus.OK

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    return jsonify({"success": True, "data": book.to_dict()}), HTTPStatus.OK

@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    required_fields = ["title", "author", "isbn"]

    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), HTTPStatus.BAD_REQUEST

    new_book = Book(
        title=data['title'],
        author=data['author'],
        genre=data.get('genre'),
        published_year=data.get('published_year'),
        isbn=data['isbn'],
        quantity=data.get('quantity', 1)
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({"success": True, "data": new_book.to_dict()}), HTTPStatus.CREATED

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided for update"}), HTTPStatus.BAD_REQUEST

    for key in ["title", "author", "genre", "published_year", "isbn", "quantity"]:
        if key in data:
            setattr(book, key, data[key])

    db.session.commit()

    return jsonify({"success": True, "data": book.to_dict()}), HTTPStatus.OK

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(book)
    db.session.commit()

    return jsonify({"success": True, "data": "Book deleted successfully"}), HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)
