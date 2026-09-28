from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id"),
        nullable=False
    )
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    published_year = Column(Integer, nullable=False)

    category = relationship("Category", backref="books")