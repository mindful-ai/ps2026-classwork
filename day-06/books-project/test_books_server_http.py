import os

import pytest
import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session", autouse=True)
def server_is_running():
    """Verify that the Uvicorn server is reachable before running tests."""
    try:
        response = requests.get(f"{BASE_URL}/books/", timeout=5)
    except requests.RequestException as exc:
        pytest.fail(
            f"FastAPI server is not reachable at {BASE_URL}. "
            f"Start it with: uvicorn books_server:app --reload\n{exc}"
        )

    assert response.status_code == 200


# ---------------------------------------------------------------------
# POST /books/
# ---------------------------------------------------------------------

def test_create_book():
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
    }

    response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]


def test_create_book_without_title():
    payload = {
        "author": "Robert C. Martin",
    }

    response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


def test_create_book_without_author():
    payload = {
        "title": "Clean Code",
    }

    response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


def test_create_book_with_invalid_id_type():
    payload = {
        "id": "not-an-integer",
        "title": "Clean Code",
        "author": "Robert C. Martin",
    }

    response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# GET /books/
# ---------------------------------------------------------------------

def test_get_books():
    response = requests.get(
        f"{BASE_URL}/books/",
        timeout=5,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_books_contains_created_book():
    payload = {
        "title": "Python Testing",
        "author": "Test Author",
    }

    create_response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert create_response.status_code == 200

    book_id = create_response.json()["id"]

    response = requests.get(
        f"{BASE_URL}/books/",
        timeout=5,
    )

    assert response.status_code == 200

    books = response.json()
    book = next((item for item in books if item["id"] == book_id), None)

    assert book is not None
    assert book["title"] == payload["title"]
    assert book["author"] == payload["author"]


# ---------------------------------------------------------------------
# GET /books/{book_id}
# ---------------------------------------------------------------------

def test_get_book():
    payload = {
        "title": "Python",
        "author": "Guido van Rossum",
    }

    create_response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert create_response.status_code == 200

    book_id = create_response.json()["id"]

    response = requests.get(
        f"{BASE_URL}/books/{book_id}",
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]


def test_get_book_not_found():
    response = requests.get(
        f"{BASE_URL}/books/999999999",
        timeout=5,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_get_book_invalid_id():
    response = requests.get(
        f"{BASE_URL}/books/abc",
        timeout=5,
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# PUT /books/{book_id}
# ---------------------------------------------------------------------

def test_update_book():
    create_payload = {
        "title": "Old Title",
        "author": "Old Author",
    }

    create_response = requests.post(
        f"{BASE_URL}/books/",
        json=create_payload,
        timeout=5,
    )

    assert create_response.status_code == 200

    book_id = create_response.json()["id"]

    update_payload = {
        "title": "New Title",
        "author": "New Author",
    }

    response = requests.put(
        f"{BASE_URL}/books/{book_id}",
        json=update_payload,
        timeout=5,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == update_payload["title"]
    assert data["author"] == update_payload["author"]


def test_update_book_not_found():
    payload = {
        "title": "New Title",
        "author": "New Author",
    }

    response = requests.put(
        f"{BASE_URL}/books/999999999",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_update_book_missing_title():
    payload = {
        "author": "New Author",
    }

    response = requests.put(
        f"{BASE_URL}/books/999999999",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


def test_update_book_missing_author():
    payload = {
        "title": "New Title",
    }

    response = requests.put(
        f"{BASE_URL}/books/999999999",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


def test_update_book_invalid_id():
    payload = {
        "title": "New Title",
        "author": "New Author",
    }

    response = requests.put(
        f"{BASE_URL}/books/abc",
        json=payload,
        timeout=5,
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------
# DELETE /books/{book_id}
# ---------------------------------------------------------------------

def test_delete_book():
    payload = {
        "title": "Delete Me",
        "author": "Test Author",
    }

    create_response = requests.post(
        f"{BASE_URL}/books/",
        json=payload,
        timeout=5,
    )

    assert create_response.status_code == 200

    book_id = create_response.json()["id"]

    response = requests.delete(
        f"{BASE_URL}/books/{book_id}",
        timeout=5,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Book {book_id} deleted successfully"
    }

    # Verify deletion through the HTTP API.
    get_response = requests.get(
        f"{BASE_URL}/books/{book_id}",
        timeout=5,
    )

    assert get_response.status_code == 404


def test_delete_book_not_found():
    response = requests.delete(
        f"{BASE_URL}/books/999999999",
        timeout=5,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_delete_book_invalid_id():
    response = requests.delete(
        f"{BASE_URL}/books/abc",
        timeout=5,
    )

    assert response.status_code == 422
