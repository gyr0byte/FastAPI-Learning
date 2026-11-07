# FastAPI Learning

An introductory FastAPI project that serves student data from
[`students.json`](students.json). The current implementation focuses on
GET endpoints, path and query parameters, validation, filtering, and sorting.

## What is implemented

- FastAPI application created in [`main.py`](main.py).
- Student data loaded from a local JSON file.
- Interactive API documentation generated automatically by FastAPI.
- 404 responses for unknown student IDs and invalid sorting options.
- Case-insensitive course filtering.
- Student sorting by name, age, or marks in ascending or descending order.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/)

The project uses FastAPI and declares its dependencies in
[`pyproject.toml`](pyproject.toml).

## Setup

Clone the repository and install the project dependencies:

```bash
git clone https://github.com/gyr0byte/FastAPI-Learning.git
cd FastAPI-Learning
uv sync
```

## Run the application

Start the development server with:

```bash
uv run --with uvicorn uvicorn main:app --reload
```

The API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
FastAPI's interactive Swagger UI is available at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Returns a welcome message. |
| `GET` | `/hello` | Returns a simple hello message. |
| `GET` | `/student` | Returns all students from `students.json`. |
| `GET` | `/student/{id}` | Returns one student by ID, such as `S001`. |
| `GET` | `/filter?course=Python` | Returns students enrolled in the specified course. |
| `GET` | `/sort?sort_by=marks&order=desc` | Sorts students by `marks`, `age`, or `name`. |

### Sorting options

- `sort_by`: `marks`, `age`, or `name`
- `order`: `asc` or `desc`

Invalid student IDs, sort fields, and sort orders return an HTTP 404 response
with an explanatory error message.

## Example requests

```text
GET http://127.0.0.1:8000/student/S001
GET http://127.0.0.1:8000/filter?course=python
GET http://127.0.0.1:8000/sort?sort_by=marks&order=desc
```

## Next learning topics

- POST, PUT, and DELETE endpoints
- Pydantic models and request validation
- CRUD operations
- Database integration with PostgreSQL and SQLAlchemy
- Dependency injection, CORS, testing, Docker, and deployment

This repository is a learning project rather than a production application.
