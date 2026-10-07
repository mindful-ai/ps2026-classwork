from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI(title="Book CRUD API with SQLite")

# ----------------------------
# Database setup
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------------------
# Pydantic models
# ----------------------------
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str

# ----------------------------
# CRUD Endpoints
# ----------------------------

@app.post("/books/", response_model=Book)
def create_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)",
                   (book.title, book.author))
    conn.commit()
    book.id = cursor.lastrowid
    conn.close()
    return book

@app.get("/books/", response_model=List[Book])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    return [Book(**dict(row)) for row in rows]

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(**dict(row))

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET title = ?, author = ? WHERE id = ?",
                   (book.title, book.author, book_id))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.close()
    book.id = book_id
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.close()
    return {"message": f"Book {book_id} deleted successfully"}
