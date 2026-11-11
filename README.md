# FastAPI Learning

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-Learning%20Project-lightgrey)

A hands-on FastAPI learning project that progressively demonstrates how to
build a small REST API with Python. The current API serves student data from a
local JSON file and covers core FastAPI concepts such as routes, path
parameters, query parameters, validation, filtering, sorting, and pagination.
It also includes a standalone introduction to Pydantic data models and
validation.

> This is an educational project, not a production-ready application.

## Contents

- [Features](#features)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Getting started](#getting-started)
- [API reference](#api-reference)
- [Pydantic fundamentals](#pydantic-fundamentals)
- [Validation and errors](#validation-and-errors)
- [Interactive documentation](#interactive-documentation)
- [Learning roadmap](#learning-roadmap)

## Features

- FastAPI application with simple GET endpoints.
- Student records loaded from [`students.json`](students.json).
- Path parameter lookup for individual students.
- Case-insensitive filtering by course.
- Sorting by name, age, or marks in ascending or descending order.
- Pagination with validated page and page-size parameters.
- Pydantic models with type hints, field constraints, email validation, custom
  validators, and computed fields.
- Automatic interactive API documentation through Swagger UI and ReDoc.
- Clear HTTP errors for missing students and invalid sorting options.

## Project structure

```text
FastAPI-Learning/
├── main.py          # FastAPI application and route definitions
├── pydantic_basics.py # Pydantic fundamentals and validation examples
├── students.json    # Sample student data
├── pyproject.toml   # Project metadata and dependencies
├── .gitignore       # Ignored local, cache, and build files
├── LICENSE          # MIT license
└── README.md        # Project documentation
```

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management

The project declares FastAPI and Uvicorn in
[`pyproject.toml`](pyproject.toml).

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/gyr0byte/FastAPI-Learning.git
cd FastAPI-Learning
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start the development server

```bash
uv run uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Returns a welcome message. |
| `GET` | `/hello` | Returns a simple hello message. |
| `GET` | `/student` | Returns all students. |
| `GET` | `/student/{id}` | Returns one student by ID, such as `S001`. |
| `GET` | `/filter?course=Python` | Returns students enrolled in a course. |
| `GET` | `/sort?sort_by=marks&order=desc` | Sorts students by a supported field and order. |
| `GET` | `/paginate?page=1&limit=2` | Returns one page of students with metadata. |

### Sorting

The `/sort` endpoint accepts:

| Parameter | Allowed values |
| --- | --- |
| `sort_by` | `marks`, `age`, `name` |
| `order` | `asc`, `desc` |

Example:

```text
GET http://127.0.0.1:8000/sort?sort_by=marks&order=desc
```

### Pagination

The `/paginate` endpoint accepts:

| Parameter | Default | Constraints |
| --- | --- | --- |
| `page` | `1` | Must be at least `1` |
| `limit` | `2` | Must be between `1` and `100` |

Example:

```text
GET http://127.0.0.1:8000/paginate?page=1&limit=2
```

The response contains the requested `page`, the `limit`, the
`total_students` count, and the page's `students` list:

```json
{
  "page": 1,
  "limit": 2,
  "total_students": 7,
  "students": [
    {
      "id": "S001",
      "name": "Gaurav Dulal",
      "age": 20,
      "email": "gaurav@example.com",
      "course": "Python",
      "marks": 92
    },
    {
      "id": "S002",
      "name": "John Doe",
      "age": 22,
      "email": "john@example.com",
      "course": "Java",
      "marks": 88
    }
  ]
}
```

### Other examples

```text
GET http://127.0.0.1:8000/student/S001
GET http://127.0.0.1:8000/filter?course=python
```

## Pydantic fundamentals

[`pydantic_basics.py`](pydantic_basics.py) is a standalone learning module
covering the progression from unvalidated dictionaries to structured,
validated models:

- `SimpleStudent` demonstrates `BaseModel` and Python type hints.
- `RuleStudent` demonstrates required fields, default values, optional fields,
  and `Field` constraints such as `min_length`, `gt`, `ge`, and `le`.
- `EmailStudent` demonstrates validation with `EmailStr`.
- `Student` combines field constraints, email validation, a custom
  `field_validator`, and a computed `grade` field based on marks.
- Student names are normalized to title case and must contain only letters and
  spaces.

Run the lesson directly with:

```bash
uv run python pydantic_basics.py
```

The example prints a validated student with the calculated grade:

```text
S001 John Doe 20 Python 80 john@example.com A
```

## Validation and errors

- An unknown student ID returns HTTP `404`.
- An unsupported sort field returns HTTP `404`.
- An unsupported sort order returns HTTP `404`.
- `page` values below `1` are rejected by FastAPI validation.
- `limit` values below `1` or above `100` are rejected by FastAPI validation.
- A page beyond the available data returns an empty `students` list.

## Interactive documentation

With the server running, FastAPI provides:

- [Swagger UI](http://127.0.0.1:8000/docs) for exploring and trying endpoints.
- [ReDoc](http://127.0.0.1:8000/redoc) for a clean API reference.
- [OpenAPI schema](http://127.0.0.1:8000/openapi.json) in JSON format.

## Learning roadmap

Planned topics for future iterations include:

- Integrating the Pydantic models with FastAPI response models
- POST, PUT, and DELETE endpoints
- Full CRUD operations
- Database integration with PostgreSQL and SQLAlchemy
- Dependency injection
- CORS configuration
- Automated API testing
- Docker and deployment

## License

This project is available under the [MIT License](LICENSE).
