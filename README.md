# FastAPI Learning

Personal learning repository for studying FastAPI and Python backend development through structured lessons, exercises, and practical implementations.

## Objectives

- Build a solid foundation in Python backend development.
- Learn how to design and implement APIs with FastAPI.
- Practice validation, error handling, databases, deployment, and related backend workflows.
- Document progress and keep useful examples available for future reference.

## Technologies Being Explored

- Python
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- SQLAlchemy
- Docker and Docker Compose
- Cloud deployment platforms

## Learning Roadmap

- [ ] API fundamentals and client-server architecture
- [ ] FastAPI basics and Uvicorn
- [ ] HTTP methods (GET, POST, PUT, DELETE)
- [ ] Path parameters and query parameters
- [ ] HTTP status codes and error handling
- [ ] Filtering, sorting, and pagination
- [ ] Pydantic models and data validation
- [ ] CRUD operations
- [ ] Frontend integration and CORS
- [ ] PostgreSQL and SQLAlchemy
- [ ] Database sessions and dependency injection
- [ ] Docker and Docker Compose
- [ ] Cloud deployment

## Installation and Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python project and dependency management.

1. Install Python 3.10 or newer.
2. Install uv by following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
3. Clone this repository and change into its directory:

   ```bash
   git clone https://github.com/gyr0byte/FastAPI-Learning.git
   cd FastAPI-Learning
   ```

4. Create the project environment and install the declared dependencies:

   ```bash
   uv sync
   ```

5. Activate the environment if you want to use its commands directly:

   ```bash
   # Windows PowerShell
   .venv\Scripts\Activate.ps1

   # macOS/Linux
   source .venv/bin/activate
   ```

## Running a FastAPI Application

When an application module has been added to the repository, run it with Uvicorn using the module and application object defined by that implementation. For example:

```bash
uv run uvicorn <module>:<app> --reload
```

Replace `<module>:<app>` with the appropriate import path, such as `main:app`.

While the development server is running, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to use FastAPI's interactive API documentation.

## Future Projects and Practical Implementations

As the course progresses, this repository will collect small projects and practical implementations that apply the concepts in the roadmap. Each addition will be documented as the relevant topics are completed.

## Note

This repository documents my learning journey. It is not a finished production application.