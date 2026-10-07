# FastAPI Book CRUD Example

This project demonstrates a simple CRUD API for managing book information using **FastAPI**.

---

## 📌 FastAPI Code (`main.py`)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Book Model
class Book(BaseModel):
    title: str
    author: str

# In-memory Database
books_db = {}

# Create Book
@app.post("/books/")
def create_book(book: Book):
    if book.title in books_db:
        raise HTTPException(status_code=400, detail="Book already exists")
    books_db[book.title] = book
    return {"message": "Book added successfully", "book": book}

# Read Book
@app.get("/books/{title}")
def read_book(title: str):
    if title not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[title]

# Update Book
@app.put("/books/{title}")
def update_book(title: str, updated_book: Book):
    if title not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    books_db[title] = updated_book
    return {"message": "Book updated successfully", "book": updated_book}

# Delete Book
@app.delete("/books/{title}")
def delete_book(title: str):
    if title not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    del books_db[title]
    return {"message": "Book deleted successfully"}
```

---

## 📌 Testing with Postman

1. **Create a Book (POST)**  
   **Endpoint:** `http://127.0.0.1:8000/books/`  
   **Body (JSON):**
   ```json
   {
     "title": "Atomic Habits",
     "author": "James Clear"
   }
   ```

2. **Get a Book (GET)**  
   **Endpoint:** `http://127.0.0.1:8000/books/Atomic Habits`

3. **Update a Book (PUT)**  
   **Endpoint:** `http://127.0.0.1:8000/books/Atomic Habits`  
   **Body (JSON):**
   ```json
   {
     "title": "Atomic Habits",
     "author": "James Clear - Updated"
   }
   ```

4. **Delete a Book (DELETE)**  
   **Endpoint:** `http://127.0.0.1:8000/books/Atomic Habits`
```

---

## 📌 Run the API

Run the following command to start FastAPI:

```bash
uvicorn main:app --reload
```

Open your browser at: **http://127.0.0.1:8000/docs** to test interactively.
