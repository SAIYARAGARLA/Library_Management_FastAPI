from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# =========================================================
# CREATE CATEGORY
# =========================================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing_category = (
        db.query(Category)
        .filter(Category.category_name == category.category_name)
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists"
        )

    new_category = Category(
        category_name=category.category_name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# =========================================================
# GET CATEGORIES WITH PAGINATION
# =========================================================

@router.get(
    "",
    response_model=list[CategoryResponse]
)
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return (
        db.query(Category)
        .offset(skip)
        .limit(limit)
        .all()
    )


# =========================================================
# GET CATEGORY BY ID
# =========================================================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(Category)
        .filter(Category.category_id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


# =========================================================
# UPDATE CATEGORY
# =========================================================

@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing_category = (
        db.query(Category)
        .filter(Category.category_id == category_id)
        .first()
    )

    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    duplicate_category = (
        db.query(Category)
        .filter(
            Category.category_name == category.category_name,
            Category.category_id != category_id
        )
        .first()
    )

    if duplicate_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists"
        )

    existing_category.category_name = category.category_name
    existing_category.description = category.description

    db.commit()
    db.refresh(existing_category)

    return existing_category


# =========================================================
# DELETE CATEGORY
# =========================================================

@router.delete(
    "/{category_id}"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    existing_category = (
        db.query(Category)
        .filter(Category.category_id == category_id)
        .first()
    )

    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if existing_category.books:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category because books are associated with it"
        )

    db.delete(existing_category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }