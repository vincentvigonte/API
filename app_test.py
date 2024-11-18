import pytest
import json
from app import app, db, Book

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/Library'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_get_all_books(test_client):
    response = test_client.get('/api/books')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert isinstance(data['data'], list)

def test_create_book(test_client):
    new_book = {
        "title": "The Art of War",
        "author": "Sun Tzu",
        "genre": "Philosophy",
        "published_year": 500,
        "isbn": "1234567890123",
        "quantity": 3
    }
    response = test_client.post('/api/books', json=new_book)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['title'] == "The Art of War"

def test_get_single_book(test_client):
    book = Book(
        title="Test Book",
        author="Author Name",
        genre="Test Genre",
        published_year=2022,
        isbn="1112223334445",
        quantity=1
    )
    db.session.add(book)
    db.session.commit()

    response = test_client.get(f'/api/books/{book.book_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['title'] == "Test Book"

def test_update_book(test_client):
    book = Book.query.first()
    update_data = {
        "title": "Updated Book Title",
        "quantity": 5
    }
    response = test_client.put(f'/api/books/{book.book_id}', json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['title'] == "Updated Book Title"
    assert data['data']['quantity'] == 5

def test_delete_book(test_client):
    book = Book.query.first()
    response = test_client.delete(f'/api/books/{book.book_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data'] == "Book deleted successfully."

    response = test_client.get(f'/api/books/{book.book_id}')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False

def test_create_book_missing_field(test_client):
    new_book = {
        "author": "Missing Title Author",
        "genre": "Missing Title Genre",
        "published_year": 2023,
        "isbn": "9876543210987"
    }
    response = test_client.post('/api/books', json=new_book)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert "Missing required field" in data['error']
