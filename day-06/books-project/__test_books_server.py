import sqlite3
import pytest
from fastapi.testclient import TestClient

import books_server


@pytest.fixture(scope="session")
def test_db(tmp_path_factory):
    """Create an isolated SQLite database for the entire test session."""
    db_path = tmp_path_factory.mktemp("data") / "test_books.db"

    def get_test_db_connection():
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # Replace the application's DB connection with the isolated test DB.
    books_server.get_db_connection = get_test_db_connection

    # Create the same schema used by the application.
    conn = get_test_db_connection()
    conn.execute(
        """
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    yield db_path


@pytest.fixture()
def client(test_db):
    """FastAPI test client."""
    # Keep each test independent.
    conn = sqlite3.connect(str(test_db))
    conn.execute("DELETE FROM books")
    conn.execute(
        "DELETE FROM sqlite_sequence WHERE name = 'books'"
    )
    conn.commit()
    conn.close()

    with TestClient(books_server.app) as test_client:
        yield test_client


# ---------------------------------------------------------------------
# POST /books/
# ---------------------------------------------------------------------

def test_create_book(client):
    response = client.post(
        "/books/",
        json={"title": "Clean Code", "author": "Robert C. Martin"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert C. Martin"


def test_create_book_without_title(client):
    response = client.post(
        "/books/",
        json={"author": "Robert C. Martin"},
    )

    assert response.status_code == 422


def test_create_book_without_author(client):
    response = client.post(
        "/books/",
        json={"title": "Clean Code"},
    )

    assert response.status_code == 422


def test_create_book_with_invalid_id_type(client):
    response = client.post(
        "/books/",
        json={
            "id": "not-an-integer",
            "title": "Clean Code",
            "author": "Robert C. Martin",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# GET /books/
# ---------------------------------------------------------------------

def test_get_books_empty(client):
    response = client.get("/books/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_books(client):
    client.post(
        "/books/",
        json={"title": "Book One", "author": "Author One"},
    )
    client.post(
        "/books/",
        json={"title": "Book Two", "author": "Author Two"},
    )

    response = client.get("/books/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Book One"
    assert data[1]["title"] == "Book Two"


# ---------------------------------------------------------------------
# GET /books/{book_id}
# ---------------------------------------------------------------------

def test_get_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "Python", "author": "Guido van Rossum"},
    )

    book_id = create_response.json()["id"]

    response = client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": book_id,
        "title": "Python",
        "author": "Guido van Rossum",
    }


def test_get_book_not_found(client):
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_get_book_invalid_id(client):
    response = client.get("/books/abc")

    assert response.status_code == 422


# ---------------------------------------------------------------------
# PUT /books/{book_id}
# ---------------------------------------------------------------------

def test_update_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "Old Title", "author": "Old Author"},
    )

    book_id = create_response.json()["id"]

    response = client.put(
        f"/books/{book_id}",
        json={"title": "New Title", "author": "New Author"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": book_id,
        "title": "New Title",
        "author": "New Author",
    }


def test_update_book_not_found(client):
    response = client.put(
        "/books/999",
        json={"title": "New Title", "author": "New Author"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_update_book_missing_title(client):
    response = client.put(
        "/books/1",
        json={"author": "New Author"},
    )

    assert response.status_code == 422


def test_update_book_missing_author(client):
    response = client.put(
        "/books/1",
        json={"title": "New Title"},
    )

    assert response.status_code == 422


def test_update_book_invalid_id(client):
    response = client.put(
        "/books/abc",
        json={"title": "New Title", "author": "New Author"},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# DELETE /books/{book_id}
# ---------------------------------------------------------------------

def test_delete_book(client):
    create_response = client.post(
        "/books/",
        json={"title": "Delete Me", "author": "Test Author"},
    )

    book_id = create_response.json()["id"]

    response = client.delete(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Book {book_id} deleted successfully"
    }

    # Confirm that the book is actually gone.
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404


def test_delete_book_not_found(client):
    response = client.delete("/books/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_delete_book_invalid_id(client):
    response = client.delete("/books/abc")

    assert response.status_code == 422
