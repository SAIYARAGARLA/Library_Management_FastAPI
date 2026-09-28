from datetime import date

from pydantic import BaseModel, Field


class BorrowCreate(BaseModel):
    book_id: int = Field(..., gt=0)
    member_id: int = Field(..., gt=0)
    borrow_date: date


class BorrowResponse(BaseModel):
    borrow_id: int
    book_id: int
    member_id: int
    borrow_date: date
    due_date: date
    return_date: date | None = None
    status: str

    class Config:
        from_attributes = True