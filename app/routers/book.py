from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.category import Category
from app.models.borrow_record import BorrowRecord
from app.schemas.book import BookCreate, BookResponse


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    category = (
        db.query(Category)
        .filter(Category.category_id == book.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    existing_book = (
        db.query(Book)
        .filter(Book.isbn == book.isbn)
        .first()
    )

    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ISBN already exists"
        )

    if book.available_copies > book.total_copies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available copies cannot exceed total copies"
        )

    new_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        category_id=book.category_id,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        published_year=book.published_year
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.get(
    "",
    response_model=list[BookResponse]
)
def get_books(
    title: str | None = None,
    author: str | None = None,
    category_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if title:
        query = query.filter(
            Book.title.ilike(f"%{title}%")
        )

    if author:
        query = query.filter(
            Book.author.ilike(f"%{author}%")
        )

    if category_id:
        query = query.filter(
            Book.category_id == category_id
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/{book_id}",
    response_model=BookResponse
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = (
        db.query(Book)
        .filter(Book.book_id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book


@router.put(
    "/{book_id}",
    response_model=BookResponse
)
def update_book(
    book_id: int,
    book: BookCreate,
    db: Session = Depends(get_db)
):
    existing_book = (
        db.query(Book)
        .filter(Book.book_id == book_id)
        .first()
    )

    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    category = (
        db.query(Category)
        .filter(Category.category_id == book.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    duplicate_book = (
        db.query(Book)
        .filter(
            Book.isbn == book.isbn,
            Book.book_id != book_id
        )
        .first()
    )

    if duplicate_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ISBN already exists"
        )

    if book.available_copies > book.total_copies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available copies cannot exceed total copies"
        )

    existing_book.title = book.title
    existing_book.author = book.author
    existing_book.isbn = book.isbn
    existing_book.category_id = book.category_id
    existing_book.total_copies = book.total_copies
    existing_book.available_copies = book.available_copies
    existing_book.published_year = book.published_year

    db.commit()
    db.refresh(existing_book)

    return existing_book


@router.delete(
    "/{book_id}"
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    existing_book = (
        db.query(Book)
        .filter(Book.book_id == book_id)
        .first()
    )

    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    active_borrow = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.return_date.is_(None)
        )
        .first()
    )

    if active_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a book that is currently borrowed"
        )

    db.delete(existing_book)
    db.commit()

    return {
        "message": "Book deleted successfully"
    }