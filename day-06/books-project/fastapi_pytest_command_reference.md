# FastAPI Books Server — HTTP Pytest Test Bench

## Test Architecture

This test bench treats the FastAPI application as a real HTTP service.

```text
pytest
  |
  | HTTP requests using requests
  v
Uvicorn
  |
  v
FastAPI application
  |
  v
SQLite (books.db)
```

The pytest code does **not** import `TestClient`.

It uses the `requests` library to make actual HTTP requests to the Uvicorn server.

---

## 1. Install Dependencies

```bash
pip install fastapi uvicorn requests pytest
```

Using `uv`:

```bash
uv add fastapi uvicorn requests pytest
```

---

## 2. Start the FastAPI Server

Open Terminal 1:

```bash
uvicorn books_server:app --reload
```

The default server URL is:

```text
http://127.0.0.1:8000
```

Verify the API manually:

```text
http://127.0.0.1:8000/docs
```

---

## 3. Run the HTTP Test Bench

Open Terminal 2 in the project directory:

```bash
pytest test_books_server_http.py -v
```

The tests will make real HTTP requests to:

```text
http://127.0.0.1:8000
```

---

## 4. Run All Tests

```bash
pytest -v
```

---

## 5. Run One Test

Create book:

```bash
pytest test_books_server_http.py::test_create_book -v
```

Get book:

```bash
pytest test_books_server_http.py::test_get_book -v
```

Update book:

```bash
pytest test_books_server_http.py::test_update_book -v
```

Delete book:

```bash
pytest test_books_server_http.py::test_delete_book -v
```

---

## 6. Run Tests by Keyword

Create:

```bash
pytest -k "create" -v
```

Get:

```bash
pytest -k "get" -v
```

Update:

```bash
pytest -k "update" -v
```

Delete:

```bash
pytest -k "delete" -v
```

Not-found:

```bash
pytest -k "not_found" -v
```

Invalid/validation:

```bash
pytest -k "invalid or missing" -v
```

---

## 7. Configure a Different Server URL

The test bench uses:

```text
http://127.0.0.1:8000
```

by default.

You can override it using the `BASE_URL` environment variable.

### Windows CMD

```cmd
set BASE_URL=http://127.0.0.1:8000
pytest -v
```

### Windows PowerShell

```powershell
$env:BASE_URL="http://127.0.0.1:8000"
pytest -v
```

### Linux/macOS

```bash
BASE_URL=http://127.0.0.1:8000 pytest -v
```

For example, if the server runs on port 9000:

```powershell
$env:BASE_URL="http://127.0.0.1:9000"
pytest -v
```

---

## 8. Server Availability Check

The test suite contains a session-level fixture that first calls:

```text
GET /books/
```

If the Uvicorn server is not running, pytest reports a clear error telling you to start:

```bash
uvicorn books_server:app --reload
```

This is useful because the test bench depends on an externally running server.

---

## 9. Test Coverage

The HTTP test bench covers:

| HTTP | Endpoint | Test Coverage |
|---|---|---|
| POST | `/books/` | Create, missing title, missing author, invalid ID |
| GET | `/books/` | Retrieve books, verify created book |
| GET | `/books/{book_id}` | Valid book, 404, invalid ID |
| PUT | `/books/{book_id}` | Update, 404, missing fields, invalid ID |
| DELETE | `/books/{book_id}` | Delete, 404, invalid ID |

---

## 10. Expected Status Codes

| Situation | Expected |
|---|---:|
| Successful POST | 200 |
| Successful GET | 200 |
| Successful PUT | 200 |
| Successful DELETE | 200 |
| Book not found | 404 |
| Invalid path parameter | 422 |
| Missing required request field | 422 |
| Invalid Pydantic field | 422 |

---

## 11. Important Difference from TestClient

### Previous approach

```python
from fastapi.testclient import TestClient

client = TestClient(app)

response = client.get("/books/")
```

This tests the application in-process.

### Current approach

```python
import requests

response = requests.get(
    "http://127.0.0.1:8000/books/",
    timeout=5,
)
```

This tests the actual HTTP interface exposed by Uvicorn.

Therefore:

```text
TestClient approach
pytest -> FastAPI

HTTP approach
pytest -> HTTP -> Uvicorn -> FastAPI
```

The HTTP approach is closer to an external API/client test.

---

## 12. Recommended Workshop Workflow

### Terminal 1 — Server

```bash
uvicorn books_server:app --reload
```

### Terminal 2 — Tests

```bash
pytest test_books_server_http.py -v
```

### Run a single endpoint test

```bash
pytest test_books_server_http.py::test_create_book -v
```

### Run the complete suite

```bash
pytest test_books_server_http.py -v
```

---

## 13. Debugging

Show detailed output:

```bash
pytest test_books_server_http.py -v -s
```

Stop at first failure:

```bash
pytest test_books_server_http.py -v -x
```

Show short tracebacks:

```bash
pytest test_books_server_http.py -v --tb=short
```

Run previously failed tests:

```bash
pytest test_books_server_http.py --lf -v
```

---

## 14. Coverage

Install:

```bash
pip install pytest-cov
```

Run:

```bash
pytest test_books_server_http.py -v --cov=books_server --cov-report=term-missing
```

Generate HTML coverage:

```bash
pytest test_books_server_http.py --cov=books_server --cov-report=html
```

Open:

```text
htmlcov/index.html
```

---

## 15. Recommended Command

For normal development:

```bash
pytest test_books_server_http.py -v
```

For development plus coverage:

```bash
pytest test_books_server_http.py -v --cov=books_server --cov-report=term-missing
```

---

## 16. Key Testing Principle

The application and the test bench are separate processes:

```text
+----------------------+          HTTP          +----------------------+
|                      |  --------------------> |                      |
|   pytest             |       requests        |   Uvicorn             |
|   test_books_        |                        |   FastAPI             |
|   server_http.py     |  <-------------------- |   books_server.py      |
|                      |       response        |                      |
+----------------------+                         +----------+-----------+
                                                           |
                                                           v
                                                     books.db
```

This means the test bench validates the API from the perspective of an external client.

It is therefore appropriate for testing:

- HTTP methods
- URLs
- request JSON
- response JSON
- HTTP status codes
- Pydantic validation
- 404 behavior
- CRUD behavior
- actual server accessibility
