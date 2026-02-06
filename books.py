from fastapi import Body, FastAPI

app = FastAPI()

books = [
    {
        "title": "book1", "author": "Author 1", "subject": "Math" 
    },
    {
        "title": "book2", "author": "Author 2", "subject": "Science" 
    },
    {
        "title": "book7", "author": "Author 2", "subject": "Math" 
    },
    {
        "title": "book8", "author": "Author 3", "subject": "Science" 
    },
    {
        "title": "book3", "author": "Author 3", "subject": "Social Science" 
    },
    {
        "title": "book4", "author": "Author 4", "subject": "Software Engineering" 
    },
    {
        "title": "book5", "author": "Author 5", "subject": "Operating System" 
    },
    {
        "title": "book6", "author": "Author 6", "subject": "Trigonometry" 
    }
]

# get all books
@app.get("/books")
async def all_books():
    return books

# get my books
@app.get("/books/mybook")
async def mybook():
    return books[3]

# book by title - path param
@app.get("/books/{title}")
async def book_by_index(title: str):
    for book in books:
        if(book.get("title").casefold() == title.casefold()):
            return book

# query params

# get books by - query params
@app.get("/books/")
async def get_books_by_query(subject: str):
    books_by_subject = []
    for book in books:
        if book.get("subject").casefold() == subject.casefold():
            books_by_subject.append(book)
    return books_by_subject

# get book by path param and query param
@app.get("/books/{author}/")
async def get_books_by_author_subject(author: str, subject: str):
    books_by_subject = []
    for book in books:
        if book.get("author").casefold() == author.casefold() and \
            book.get("subject").casefold() == subject.casefold():
            books_by_subject.append(book)
    return books_by_subject

# POST Method --------------------------------------------------------------------

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    try:
        books.append(new_book)
        return {
            "new book has been added": new_book
        }
    except:
        return {
            "something went wrong!"
        }

# Put method

@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    print(updated_book.get("title"), "title book")
    try:
        for i in range(len(books)):
            if books[i].get("title").casefold() == updated_book.get("title").casefold():
                books[i] = updated_book
                return {"Book has been updated": updated_book}
        return "This book doesn't exist. Please create new book."
    except:
        return "Oops! Something went wrong!"
    
# Delete method

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    try:
        for i in range(len(books)):
            if(books[i].get("title").casefold()==book_title.casefold()):
                books.pop(i)
                return {"book with title {} has been removed.".format(book_title)}
        return {"book with title {} not present!".format(book_title)}
    except:
        return {"Something went wrong!"}

        