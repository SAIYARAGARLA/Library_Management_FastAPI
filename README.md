# Library Management System - FastAPI

A backend Library Management System built using FastAPI, SQLAlchemy, MySQL, and Pydantic.

The application provides APIs for managing categories, books, members, and book borrowing/returning.

---

## Technologies Used

- Python 3.9+
- FastAPI
- Uvicorn
- SQLAlchemy
- MySQL
- MySQL Connector
- Pydantic
- Python Dotenv
- Swagger UI

---

## Project Structure

```text
Library_Management_FastAPI/
│
├── app/
│   ├── main.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── category.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrow_record.py
│   │
│   ├── schemas/
│   │   ├── category.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrow.py
│   │
│   ├── routers/
│   │   ├── category.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrow.py
│   │
│   └── services/
│
├── .env
├── .gitignore
├── requirements.txt
├── library_schema.sql
└── README.md
```

---

## Setup

### 1. Create the MySQL database

Create a database named:

```text
library_db
```

The required database tables can be created using:

```text
library_schema.sql
```

### 2. Configure the database

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/library_db
```

Replace `YOUR_PASSWORD` with your local MySQL password.

Do not upload the `.env` file to GitHub.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

The application runs at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Main API Endpoints

### Categories

| Method | Endpoint | Description |
|---|---|---|
| POST | `/categories` | Create category |
| GET | `/categories` | Get categories |
| GET | `/categories/{category_id}` | Get category |
| PUT | `/categories/{category_id}` | Update category |
| DELETE | `/categories/{category_id}` | Delete category |

### Books

| Method | Endpoint | Description |
|---|---|---|
| POST | `/books` | Create book |
| GET | `/books` | Get books |
| GET | `/books/{book_id}` | Get book |
| PUT | `/books/{book_id}` | Update book |
| DELETE | `/books/{book_id}` | Delete book |

### Members

| Method | Endpoint | Description |
|---|---|---|
| POST | `/members` | Create member |
| GET | `/members` | Get members |
| GET | `/members/{member_id}` | Get member |
| PUT | `/members/{member_id}` | Update member |
| DELETE | `/members/{member_id}` | Delete member |

### Borrow & Return

| Method | Endpoint | Description |
|---|---|---|
| POST | `/borrow` | Borrow a book |
| PUT | `/return/{borrow_id}` | Return a book |
| GET | `/members/{member_id}/books` | View member's borrowed books |
| GET | `/books/{book_id}/borrow-history` | View book borrow history |
| GET | `/borrow/overdue` | View overdue books |

---

## Features

- Category CRUD
- Book CRUD
- Member CRUD
- Borrow and return management
- Book search by title and author
- Book filtering by category
- Pagination
- Unique ISBN validation
- Unique email validation
- Unique category name validation
- Phone number validation
- Maximum 3 active books per member
- 14-day borrowing period
- Automatic available-copy management
- Overdue book handling
- Pydantic validation
- SQLAlchemy ORM
- MySQL database
- HTTP error handling

---

## Business Rules

- A book must exist before it can be borrowed.
- Only active members can borrow books.
- A member can borrow a maximum of 3 active books.
- A member cannot borrow the same book twice without returning it.
- A book cannot be borrowed when no copies are available.
- The due date is 14 days after the borrow date.
- Available copies decrease when a book is borrowed.
- Available copies increase when a book is returned.
- A late return is marked as `Overdue`.
- A currently borrowed book cannot be deleted.
- A category containing books cannot be deleted.
- Required fields are validated using Pydantic.

---

## Database Tables

```text
categories
books
members
borrow_records
```

Relationships:

```text
Category 1 ──── * Books

Member 1 ──── * Borrow Records

Book 1 ──── * Borrow Records
```

---

## Validation and Error Handling

The application uses Pydantic validation and FastAPI HTTP exceptions.

Common status codes:

```text
200 OK
201 Created
400 Bad Request
404 Not Found
409 Conflict
422 Unprocessable Entity
```

Examples of validation:

- Invalid email
- Invalid phone number
- Duplicate email
- Duplicate ISBN
- Duplicate category name
- Invalid book or member ID
- Invalid pagination values
- Available copies greater than total copies
- Negative available copies

---

## Security

Database credentials are stored in the `.env` file.

The `.env` file is included in `.gitignore` and should not be committed to GitHub.

Example:

```env
DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/library_db
```

Use your actual password only in your local `.env` file.

---

## Assumptions

- A member can have a maximum of 3 active borrowed books at a time.
- A borrowed book is considered active when its `return_date` is NULL.
- The due date is calculated as 14 days from the borrow date.
- A late returned book is marked with status `Overdue`.
- An inactive member cannot borrow books.
- A member cannot borrow the same book again until the previous borrowing is returned.
- A category cannot be deleted while books are associated with it.
- A member cannot be deleted when borrow records exist for that member.
- A book cannot be deleted while it is currently borrowed.
- Phone numbers are validated as 10 to 15 digits.
- ISBN, email, and category name must be unique.
- Database credentials are stored locally in `.env` and are not committed to GitHub.