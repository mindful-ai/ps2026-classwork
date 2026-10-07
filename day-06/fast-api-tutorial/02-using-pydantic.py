# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Book model
class Book(BaseModel):
    title: str
    author: str

# In-memory storage
books = {}

# Create a book
@app.post("/books/{book_id}")
def create_book(book_id: int, book: Book):
    if book_id in books:
        raise HTTPException(status_code=400, detail="Book already exists")
    books[book_id] = book
    return {"message": "Book created", "book": book}

# Read all books
@app.get("/books")
def get_all_books():
    return books

# Read a specific book
@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]

# Update a book
@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    books[book_id] = book
    return {"message": "Book updated", "book": book}

# Delete a book
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    del books[book_id]
    return {"message": "Book deleted"}
