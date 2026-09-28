from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.member import Member
from app.models.borrow_record import BorrowRecord
from app.schemas.borrow import BorrowCreate, BorrowResponse


router = APIRouter(
    tags=["Borrow & Return"]
)


@router.post(
    "/borrow",
    response_model=BorrowResponse,
    status_code=status.HTTP_201_CREATED
)
def borrow_book(
    borrow: BorrowCreate,
    db: Session = Depends(get_db)
):
    # Check book
    book = (
        db.query(Book)
        .filter(Book.book_id == borrow.book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Check member
    member = (
        db.query(Member)
        .filter(Member.member_id == borrow.member_id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Check member status
    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive member cannot borrow books"
        )

    # Check available copies
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available"
        )

    # Count currently borrowed books
    active_borrows = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.member_id == borrow.member_id,
            BorrowRecord.return_date.is_(None)
        )
        .count()
    )

    if active_borrows >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member cannot borrow more than 3 books"
        )

    # Check whether the member already has this book
    existing_borrow = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.book_id == borrow.book_id,
            BorrowRecord.member_id == borrow.member_id,
            BorrowRecord.return_date.is_(None)
        )
        .first()
    )

    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member has already borrowed this book"
        )

    # Calculate due date
    due_date = borrow.borrow_date + timedelta(days=14)

    # Create borrow record
    new_borrow = BorrowRecord(
        book_id=borrow.book_id,
        member_id=borrow.member_id,
        borrow_date=borrow.borrow_date,
        due_date=due_date,
        return_date=None,
        status="Borrowed"
    )

    # Decrease available copies
    book.available_copies -= 1

    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)

    return new_borrow


@router.put(
    "/return/{borrow_id}",
    response_model=BorrowResponse
)
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db)
):
    # Find borrow record
    borrow_record = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.borrow_id == borrow_id)
        .first()
    )

    if not borrow_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found"
        )

    # Check whether the book was already returned
    if borrow_record.return_date is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has already been returned"
        )

    # Set return date
    return_date = date.today()
    borrow_record.return_date = return_date

    # Mark status
    if return_date > borrow_record.due_date:
        borrow_record.status = "Overdue"
    else:
        borrow_record.status = "Returned"

    # Find the book
    book = (
        db.query(Book)
        .filter(Book.book_id == borrow_record.book_id)
        .first()
    )

    if book:
        book.available_copies += 1

        if book.available_copies > book.total_copies:
            book.available_copies = book.total_copies

    db.commit()
    db.refresh(borrow_record)

    return borrow_record


@router.get(
    "/members/{member_id}/books",
    response_model=list[BorrowResponse]
)
def get_member_books(
    member_id: int,
    db: Session = Depends(get_db)
):
    # Check member
    member = (
        db.query(Member)
        .filter(Member.member_id == member_id)
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Get currently borrowed books
    borrowed_books = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.member_id == member_id,
            BorrowRecord.return_date.is_(None)
        )
        .all()
    )

    return borrowed_books


@router.get(
    "/books/{book_id}/borrow-history",
    response_model=list[BorrowResponse]
)
def get_book_borrow_history(
    book_id: int,
    db: Session = Depends(get_db)
):
    # Check book
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

    # Get complete borrow history
    borrow_history = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.book_id == book_id)
        .order_by(BorrowRecord.borrow_id)
        .all()
    )

    return borrow_history


@router.get(
    "/borrow/overdue",
    response_model=list[BorrowResponse]
)
def get_overdue_books(
    db: Session = Depends(get_db)
):
    today = date.today()

    # Find currently borrowed books whose due date has passed
    overdue_records = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.return_date.is_(None),
            BorrowRecord.due_date < today
        )
        .all()
    )

    # Mark them as overdue
    for record in overdue_records:
        record.status = "Overdue"

    if overdue_records:
        db.commit()

        for record in overdue_records:
            db.refresh(record)

    return overdue_records