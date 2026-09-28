from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberResponse


router = APIRouter(
    prefix="/members",
    tags=["Members"]
)


# =========================================================
# CREATE MEMBER
# =========================================================

@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED
)
def create_member(
    member: MemberCreate,
    db: Session = Depends(get_db)
):
    existing_member = (
        db.query(Member)
        .filter(Member.email == member.email)
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    new_member = Member(
        name=member.name,
        email=member.email,
        phone=member.phone,
        address=member.address,
        membership_date=member.membership_date,
        is_active=member.is_active
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


# =========================================================
# GET MEMBERS WITH PAGINATION
# =========================================================

@router.get(
    "",
    response_model=list[MemberResponse]
)
def get_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return (
        db.query(Member)
        .offset(skip)
        .limit(limit)
        .all()
    )


# =========================================================
# GET MEMBER BY ID
# =========================================================

@router.get(
    "/{member_id}",
    response_model=MemberResponse
)
def get_member(
    member_id: int,
    db: Session = Depends(get_db)
):
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

    return member


# =========================================================
# UPDATE MEMBER
# =========================================================

@router.put(
    "/{member_id}",
    response_model=MemberResponse
)
def update_member(
    member_id: int,
    member: MemberCreate,
    db: Session = Depends(get_db)
):
    existing_member = (
        db.query(Member)
        .filter(Member.member_id == member_id)
        .first()
    )

    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    duplicate_member = (
        db.query(Member)
        .filter(
            Member.email == member.email,
            Member.member_id != member_id
        )
        .first()
    )

    if duplicate_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    existing_member.name = member.name
    existing_member.email = member.email
    existing_member.phone = member.phone
    existing_member.address = member.address
    existing_member.membership_date = member.membership_date
    existing_member.is_active = member.is_active

    db.commit()
    db.refresh(existing_member)

    return existing_member


# =========================================================
# DELETE MEMBER
# =========================================================

@router.delete(
    "/{member_id}"
)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db)
):
    existing_member = (
        db.query(Member)
        .filter(Member.member_id == member_id)
        .first()
    )

    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    if existing_member.borrow_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete member because borrow records exist"
        )

    db.delete(existing_member)
    db.commit()

    return {
        "message": "Member deleted successfully"
    }