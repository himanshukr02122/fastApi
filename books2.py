"""
Docstring for books2
Home work

# 1. books by rating
# 2. update book
# 3. 
"""

from fastapi import FastAPI, Body, Query, Path, HTTPException
from pydantic import BaseModel, Field
from typing import Optional


app = FastAPI()

class Book:
    id: int
    published_date: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, published_date, title, author, description, rating):
        self.id=id
        self.published_date=published_date
        self.title=title
        self.author=author
        self.description=description
        self.rating=rating

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    published_date: int = Field(ge=2000, lt=2027)
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
         
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "published_date": 2012,
                "author": "Coding with Himanshu",
                "description": "A new description of a book",
                "rating": 4
            }
        }
    }

BOOKS = [
    Book(1, 2021, "Intro of Pythom", "Himanshu", "awesome book", 5),
    Book(2, 2024, "React Advance", "Himanshu", "Best Tutorial", 4),
    Book(3, 2025, "Calculus", "Rahi", "One of the most selling book", 5)
]

@app.get("/books")
async def get_all_books():
    return BOOKS

@app.post("/books/create-books")
async def create_book(book_request: BookRequest):
    try:
        new_book = Book(**book_request.model_dump())
        BOOKS.append(assign_book_id(new_book))
        return {
            "message": "New entry added",
            "book": new_book
        }
    except Exception as e:
        return {
            "error": str(e)
        }
@app.get("/books/{book_id}")
async def book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/books/update_book")
async def update_book(updated_book: BookRequest):
    book_updated = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id==updated_book.id:
            BOOKS[i]=updated_book
            book_updated=True
    if not book_updated:
        raise HTTPException(status_code=404, detail="Item not found to update!")


# filtering with query params
@app.get("/books/")
async def books_by_published_date(published_date: int = Query(ge=2000)):
    books_by_published_date = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_by_published_date.append(book)
    return books_by_published_date

    
def assign_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    print(book, "book---", book.id, BOOKS[-1].id, "BOOKS[-1].id", len(BOOKS))
    return book
