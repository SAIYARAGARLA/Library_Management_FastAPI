from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    isbn: str = Field(..., min_length=1, max_length=20)
    category_id: int = Field(..., gt=0)
    total_copies: int = Field(..., gt=0)
    available_copies: int = Field(..., ge=0)
    published_year: int = Field(..., gt=0)


class BookResponse(BaseModel):
    book_id: int
    title: str
    author: str
    isbn: str
    category_id: int
    total_copies: int
    available_copies: int
    published_year: int

    class Config:
        from_attributes = True