import pytest
from app import app, db, Book


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all() 
            db.session.add_all([
                Book(title="The Birthday Boy!", author="Siradz Sahiddin", year=1925),
                Book(title="Ang Guyabanong Hilaw", author="Ken Domingo Machari", year=1949)
            ])
            db.session.commit()
        yield client


def test_get_book(client):
    response = client.get("/api/books/2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Ang Guyabanong Hilaw"

    response = client.get("/api/books/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Book not found"


def test_create_book(client):
    new_book = {"title": "Tilapiang Masarap Sinawsaw sa Suka", "author": "Darwin Soriano III", "year": 2024}
    response = client.post("/api/books", json=new_book)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Tilapiang Masarap Sinawsaw sa Suka"


def test_create_book_missing_fields(client):
    incomplete_book = {"title": "Incomplete"}
    response = client.post("/api/books", json=incomplete_book)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Missing required field" in data["error"]


def test_update_book(client):
    update_data = {"title": "Updated Title", "year": 2023}
    response = client.put("/api/books/1", json=update_data) 
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["year"] == 2023

    # Test updating a non-existent book
    response = client.put("/api/books/999", json=update_data)  # Non-existent book
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Book not found"



def test_delete_book(client):
    response = client.delete("/api/books/1")  
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Book deleted successfully"


    # Test deleting a non-existent book
    response = client.delete("/api/books/999")  # Non-existent book
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Book not found"


def test_not_found_error(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Resource not found"