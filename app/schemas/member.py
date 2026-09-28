from datetime import date

from pydantic import BaseModel, EmailStr, Field


class MemberCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    email: EmailStr

    phone: str = Field(
        ...,
        pattern=r"^\d{10,15}$"
    )

    address: str = Field(
        ...,
        min_length=1,
        max_length=250
    )

    membership_date: date

    is_active: bool = True


class MemberResponse(BaseModel):
    member_id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    membership_date: date
    is_active: bool

    class Config:
        from_attributes = True