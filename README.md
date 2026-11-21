<div align="center">

  <img src="assets/banner.svg" alt="FastAPI Learning Banner" width="100%">

  <h1 id="fastapi-learning-journey">FastAPI Learning Journey</h1>

  <p>A hands-on, step-by-step exploration of FastAPI, Pydantic data validation, and modern API architecture.</p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-%3E%3D0.115.0-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI Version"></a>
    <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic Version"></a>
    <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy Version"></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
    <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-%3E%3D1.50.0-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit Version"></a>
  </p>

  <p>
    <a href="#about">About</a> •
    <a href="#learning-path">Learning Path</a> •
    <a href="#concept-index">Concept Index</a> •
    <a href="#concepts-in-detail">Concepts in Detail</a> •
    <a href="#pydantic-fundamentals">Pydantic Fundamentals</a> •
    <a href="#practice-project-student-registry">Practice Project</a> •
    <a href="#postgresql-and-sqlalchemy-orm">PostgreSQL & SQLAlchemy</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#project-structure">Project Structure</a> •
    <a href="#progress-and-next-steps">Progress</a> •
    <a href="#known-limitations">Limitations</a> •
    <a href="#credits">Credits</a>
  </p>

</div>

---

## About

This repository documents a personal learning journey building RESTful web services with FastAPI and Python. Created while following along with a comprehensive video tutorial, each file and commit reflects an incremental step in mastering core backend topics—starting with simple route decorators, progressing to path and query parameters, exploring Pydantic data modeling, and finally integrating CRUD operations with persistent storage.

To put these backend principles into real-world practice, the repository also includes a complete **Student Registry** project powered by the learning API (with both Streamlit and vanilla web frontends), followed by a full architectural evolution to relational databases using **PostgreSQL** and **SQLAlchemy 2.0 ORM**—spanning both an initial prototyping script ([playground.py](FastAPIandPostgres/playground.py)) and a complete production-style database API ([FastAPIandPostgres/main.py](FastAPIandPostgres/main.py)).

> [!NOTE]
> This is primarily an educational codebase built to master FastAPI concepts through practical experimentation.
> <!-- TODO: tutorial link/credit -->

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Learning Path

The diagram below maps the progression of concepts explored in this codebase, in the order they were introduced and implemented:

```mermaid
flowchart TD
    A["1. Basic GET Endpoints"] --> B["2. JSON File Persistence"]
    B --> C["3. Path Parameters & 404 Handling"]
    C --> D["4. Query Filtering"]
    D --> E["5. Query Sorting & Validation"]
    E --> F["6. Pagination & Slicing Math"]
    F --> G["7. Pydantic Fundamentals"]
    G --> H["8. Request Bodies & POST Creation"]
    H --> I["9. Partial Updates with PUT"]
    I --> J["10. Resource Deletion"]
    J --> K["11. CORS Middleware"]
    K --> L["12. Full-Stack Frontends"]
    L --> M["13. Standalone ORM Exploration<br/>(playground.py)"]
    M --> N["14. Production Database API<br/>(FastAPIandPostgres/main.py)"]
```

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Concept Index

Every backend concept implemented in [main.py](main.py) is indexed below with its educational goal, exact code location, and an executable command:

| Concept | What It Teaches | Where in the Code | Try It |
|---|---|---|---|
| **Root Routing** | Route decorators (`@app.get`) and basic response serialization | [main.py:17-23](main.py#L17-L23) | `curl -s http://127.0.0.1:8000/` |
| **Data Persistence** | Reading and writing JSON files via helper functions | [main.py:27-39](main.py#L27-L39) | `curl -s http://127.0.0.1:8000/student` |
| **Path Parameters** | Dynamic URL variables, `Path(...)` metadata, and HTTP 404 errors | [main.py:44-50](main.py#L44-L50) | `curl -s http://127.0.0.1:8000/student/S001` |
| **Query Filtering** | Filtering datasets with `Query(...)` string parameters | [main.py:60-70](main.py#L60-L70) | `curl -s "http://127.0.0.1:8000/filter?course=Python"` |
| **Query Sorting** | Multi-parameter sorting, parameter validation, and ID injection | [main.py:75-106](main.py#L75-L106) | `curl -s "http://127.0.0.1:8000/sort?sort_by=marks&order=desc"` |
| **Pagination Math** | Splitting datasets with `page` and `limit` boundary constraints | [main.py:123-148](main.py#L123-L148) | `curl -s "http://127.0.0.1:8000/paginate?page=1&limit=2"` |
| **Request Bodies** | Receiving JSON payloads, Pydantic models, and HTTP 201 | [main.py:159-201](main.py#L159-L201) | `curl -s -X POST http://127.0.0.1:8000/create -H "Content-Type: application/json" -d '{"id":"S010","name":"Grace Hopper","age":22,"course":"Computer Science","marks":98,"email":"grace@example.com"}'` |
| **Partial Updates** | Selective field replacement using `model_dump(exclude_unset=True)` | [main.py:203-247](main.py#L203-L247) | `curl -s -X PUT http://127.0.0.1:8000/update/S001 -H "Content-Type: application/json" -d '{"marks":95}'` |
| **Resource Deletion** | Removing dictionary entries and saving state to disk | [main.py:249-264](main.py#L249-L264) | `curl -s -X DELETE http://127.0.0.1:8000/delete/S010` |
| **CORS Middleware** | Permitting cross-origin browser requests from external frontends | [main.py:4,8](main.py#L4-L8) | `curl -s -I -H "Origin: http://localhost:5500" http://127.0.0.1:8000/student` |

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Concepts in Detail

<details>
<summary><strong>1. Basic GET Endpoints & Route Decorators</strong></summary>

FastAPI uses Python function decorators like `@app.get("/")` to bind specific HTTP methods and URL paths to endpoint handler functions. When a client visits the endpoint, FastAPI automatically serializes the returned Python data structures into a JSON HTTP response.

```python
@app.get("/")
def greet():
    return {"Hello and welcome to FastAPI!"}

@app.get("/hello")
def hello():
    return {"Hello, World!"}
```

> [!TIP]
> **Code Insight:** The return expression `{"Hello, World!"}` creates a Python `set` (single value enclosed in curly braces), not a dictionary. FastAPI serializes Python sets into JSON arrays, meaning the client receives `["Hello, World!"]`.
</details>

<details>
<summary><strong>2. File Persistence & Helper Functions</strong></summary>

Before moving to database engines, the project uses a straightforward flat-file approach with [students.json](students.json). Two helper functions—`load_data()` and `save_data()`—encapsulate reading and formatting JSON on disk with `indent=4` for human readability.

```python
def load_data():
    with open('students.json', 'r') as f:
        return json.load(f)

def save_data(data):
    with open('students.json', 'w') as f:
        json.dump(data, f, indent=4)
```

> [!NOTE]
> **Storage Structure:** In `students.json`, the student ID is the top-level dictionary key (e.g. `"S001"`), and the value contains the student's attributes without storing the ID redundantly inside the object.
</details>

<details>
<summary><strong>3. Path Parameters & 404 Error Handling</strong></summary>

Path parameters allow capturing dynamic values directly from the URL segment (e.g., `/student/{id}`). FastAPI's `Path(...)` utility supplies OpenAPI documentation metadata and examples, while `HTTPException(status_code=404)` halts execution cleanly when an ID does not exist in the record collection.

```python
@app.get("/student/{id}")
def get_id(id: str = Path(..., description="The ID of the student to retrieve", example="S001")):
    data = load_data()
    if id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
    return data[id]
```

> [!WARNING]
> **Singular Path:** Notice that the endpoint path is `/student/{id}` (singular). Requesting the plural form `/students/{id}` will return an automatic 404 Not Found from FastAPI's router.
</details>

<details>
<summary><strong>4. Query Parameters & Filtering</strong></summary>

Query parameters appear after the `?` in a URL (e.g., `/filter?course=Python`). Using `Query(...)` with an ellipsis (`...`) marks the parameter as required, while `example="Python"` provides documentation in the Swagger UI. The endpoint performs a case-insensitive match against student records.

```python
@app.get("/filter")
def filter_student(course: str = Query(..., description="The course to filter by", example="Python")):
    data = load_data()
    filtered = {}
    for student_id, info in data.items():
        if info['course'].lower() == course.lower():
            filtered[student_id] = info
    return filtered
```

> [!TIP]
> **Dictionary Output:** Unlike standard array responses, `/filter` preserves the original key-value mapping and returns a dictionary keyed by student ID.
</details>

<details>
<summary><strong>5. Query Sorting & Parameter Validation</strong></summary>

The `/sort` endpoint demonstrates validating user input against fixed allowlists (`SORT_FIELDS` and `SORT_ORDER`). It transforms the nested JSON dictionary into a flat list of objects with the student `id` included inside each dictionary so that Python's `sorted()` function can operate on the requested key.

```python
SORT_FIELDS = ["marks", "age", "name"]
SORT_ORDER = ["asc", "desc"]

@app.get("/sort")
def sort_students(
    sort_by: str = Query(..., description="The field to sort by", example="marks"),
    order: str = Query(..., description="The order to sort by", example="asc")
):
    if sort_by not in SORT_FIELDS or order not in SORT_ORDER:
        raise HTTPException(status_code=404, detail="Invalid sort parameter")
    data = load_data()
    students = [dict(info, id=sid) for sid, info in data.items()]
    return sorted(students, key=lambda x: x[sort_by], reverse=(order == "desc"))
```

> [!NOTE]
> **Status Code Gotcha:** The endpoint raises an HTTP 404 status code when passed an unknown sort field or order type, rather than the more conventional HTTP 400 or 422 error code.
</details>

<details>
<summary><strong>6. Pagination & Index Slicing Math</strong></summary>

Pagination divides large datasets into smaller chunks so clients don't have to load every record at once. Using `ge=1` and `le=100` on the `Query()` parameters enforces numeric boundaries at the framework level before the function runs.

```python
@app.get("/paginate")
def paginate_student(
    page: int = Query(1, ge=1, description="Which page you want (start from 1)"),
    limit: int = Query(2, ge=1, le=100, description="How many students on one page (1 to 100)")
):
    data = load_data()
    students = [dict(info, id=sid) for sid, info in data.items()]
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total_students": len(students),
        "students": students[start:end]
    }
```

> [!TIP]
> **Slicing Safety:** Python list slicing (`students[start:end]`) never raises an `IndexError` even if `end` exceeds the total list length; it simply returns the remaining items.
</details>

<details>
<summary><strong>7. Request Bodies & POST Resource Creation</strong></summary>

When an endpoint argument is type-annotated with a Pydantic model (`student: Student`), FastAPI parses the incoming JSON request body, validates every field against schema rules, and injects the instantiated model. The endpoint returns HTTP 201 Created upon success.

```python
@app.post("/create", status_code=201)
def create_student(student: Student):
    data = load_data()
    if student.id in data:
        raise HTTPException(status_code=400, detail="Student with this ID already exists")
    data[student.id] = student.model_dump(exclude={"id", "grade"})
    save_data(data)
    return {"message": "Student created successfully!", "student": student}
```

> [!NOTE]
> **Excluding Computed Data:** `student.model_dump(exclude={"id", "grade"})` ensures that the student ID (stored as the dict key) and the computed `grade` are excluded before saving, preventing schema pollution.
</details>

<details>
<summary><strong>8. Partial Updates with PUT & `exclude_unset=True`</strong></summary>

Updating records partially requires distinguishing between fields the client omitted versus fields explicitly set to `None`. The endpoint accepts a `StudentUpdate` model where all fields are optional, extracts only supplied fields using `model_dump(exclude_unset=True)`, merges them onto the existing data, and re-validates the combined record through `Student`.

```python
@app.put("/update/{id}")
def update_student(student_update: StudentUpdate, id: str = Path(...)):
    data = load_data()
    if id not in data:
        raise HTTPException(status_code=404, detail=f"Student with id '{id}' not found!")
    existing = data[id]
    update = student_update.model_dump(exclude_unset=True)
    for key, value in update.items():
        existing[key] = value
    student = Student(id=id, **existing)
    data[id] = student.model_dump(exclude={"id", "grade"})
    save_data(data)
    return {"message": "Student updated successfully!", "student": student}
```

> [!TIP]
> **Grade Recalculation:** Because the merged record is passed back through `Student(id=id, **existing)`, the `@computed_field` automatically recalculates the student's letter grade if their marks changed.
</details>

<details>
<summary><strong>9. Resource Deletion</strong></summary>

The DELETE endpoint takes a student ID from the URL path, checks whether the record exists in the in-memory dictionary, removes it with Python's `del` statement, and writes the updated dictionary back to `students.json`.

```python
@app.delete("/delete/{student_id}")
def delete_student(
    student_id: str = Path(..., description="The ID of the student to delete", examples=["S001"])
):
    data = load_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail=f"Student with id '{student_id}' not found!")
    del data[student_id]
    save_data(data)
    return {"message": f"Student with id '{student_id}' deleted successfully!"}
```

> [!WARNING]
> **Parameter Name Divergence:** The path parameter here is named `{student_id}`, whereas the retrieval and update endpoints name it `{id}`.
</details>

<details>
<summary><strong>10. Cross-Origin Resource Sharing (CORS)</strong></summary>

When a web frontend running on a different port or host (e.g. `http://localhost:5500`) issues HTTP requests to the FastAPI backend (`http://127.0.0.1:8000`), the browser blocks the response under the Same-Origin Policy unless the server sends appropriate CORS headers. FastAPI provides `CORSMiddleware` to handle preflight `OPTIONS` requests and grant origin access.

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

> [!NOTE]
> `allow_origins=["*"]` allows all origins, making local development with different ports seamless.
</details>

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Pydantic Fundamentals

Before integrating request validation into the FastAPI backend, the repository explores Pydantic in isolation through [pydantic_basics.py](pydantic_basics.py). This standalone teaching script walks through seven consecutive steps:

```
Step 1: The Problem      Plain dictionaries allow invalid types and missing keys
Step 2: BaseModel        Type hints enforce basic types with automatic coercion
Step 3: Field Rules      Numeric ranges (gt, le) and string lengths (min_length)
Step 4: EmailStr         Format validation ensuring emails follow standard syntax
Step 5: Custom Rules     @field_validator for alphabets-only + @computed_field for grades
Step 6: Serialization   model_dump() converts model instances back into Python dictionaries
Step 7: Real Data Validation Unpacking records from students.json into Student models
```

### Running the Teaching Script

```powershell
# From the project root:
python pydantic_basics.py
```

> [!WARNING]
> **Working Directory Notice:** Step 7 in [pydantic_basics.py](pydantic_basics.py#L122) uses a relative path: `open("students.json", "r")`. You must run the command from the repository root directory, otherwise Python will raise a `FileNotFoundError`.

### Expected Output

When executed, Step 7 validates every record in `students.json` and prints the normalized student details along with their dynamically computed letter grades:

```text
S001 Gaurav Dulal 20 AI 100 gqurav69@gmail.com A+
S002 John Doe 22 Java 88 john@example.com A
S003 Jane Smith 21 Python 95 jane@example.com A+
S004 Alice Johnson 23 Python 90 alice@example.com A+
S005 Bob Brown 20 Java 85 bob@example.com A
S006 Charlie Davis 22 Web Dev 78 charlie@example.com B
S007 Diana Prince 21 Data Science 92 diana@example.com A+
S008 Evan Wright 24 Cloud Computing 68 evan@example.com C
S009 Frank Miller 22 Cybersecurity 55 frank@example.com F
```

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Quick Start

### Prerequisites

- Python `>=3.10` (as declared in [pyproject.toml](pyproject.toml))
- Virtual environment tool (`uv` or standard Python `venv`)

### 1. Set Up the Environment

Using **uv** (recommended):

```powershell
# Windows PowerShell
uv venv
.venv\Scripts\activate
uv pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "pydantic[email]"
```

Using standard **pip**:

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate
pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "pydantic[email]"
```

> [!NOTE]
> On macOS or Linux, the only difference is activating the virtual environment via:
> ```bash
> source .venv/bin/activate
> ```

### 2. Run the FastAPI Backend

```powershell
uvicorn main:app --reload
```

The API starts at **`http://127.0.0.1:8000`**.

- Interactive Swagger documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3. (Optional) Install Frontend Dependencies

To run the Streamlit frontend, install its specific client libraries:

```powershell
pip install "streamlit>=1.50.0" pandas altair requests
```

### 4. (Optional) Database Setup for PostgreSQL

To run the PostgreSQL and SQLAlchemy scripts:

```powershell
# Copy the environment template
cp .env.example .env

# Configure DATABASE_URL in .env with your PostgreSQL credentials:
# DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# Install database dependencies
pip install sqlalchemy python-dotenv psycopg2-binary

# Run the standalone ORM playground:
python FastAPIandPostgres/playground.py

# Run the PostgreSQL-backed FastAPI service:
uvicorn FastAPIandPostgres.main:app --reload --port 8001
```

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Practice Project: Student Registry

As a practical application of the concepts learned, the repository includes **Student Registry**—a complete student management system that connects two independent frontend interfaces to the FastAPI backend.

### Architecture Overview

```mermaid
flowchart LR
    subgraph Clients["Frontend Clients"]
        direction TB
        UI1["Streamlit Dashboard<br/>(app.py)"]
        UI2["Vanilla Web Client<br/>(web/index.html)"]
    end

    subgraph Service["Backend Service"]
        API["FastAPI REST API<br/>(main.py)"]
    end

    subgraph Storage["Persistence Layer"]
        DB[("students.json<br/>(Keyed by ID)")]
    end

    UI1 -->|"HTTP Requests (port 8501)"| API
    UI2 -->|"Fetch API / CORS (port 5500)"| API
    API -->|"load_data() / save_data()"| DB
```

### Running the Frontends

| Frontend | How to Run | URL | Description |
|---|---|---|---|
| **Streamlit Dashboard** | `streamlit run app.py` | `http://localhost:8501` | Feature-rich analytics and administration UI |
| **Vanilla Web UI** | `python -m http.server 5500 --directory web` | `http://localhost:5500` | Lightweight, zero-build client |

> [!TIP]
> The web UI can also be opened by opening `web/index.html` directly in any modern browser, provided the backend is running with CORS enabled.

<!-- TODO: add screenshot - Streamlit Dashboard Roster and Insights tabs -->
<!-- TODO: add screenshot - Vanilla Web UI Roster and Drawer -->

### Key Frontend Features

- **Streamlit Dashboard ([app.py](app.py)):**
  - **Roster Tab**: Search by ID/name/email, filter by course pills (`st.pills`), sort fields with `st.segmented_control`, marks range slider, and selectable dataframe with marks progress bars.
  - **Student Profile Panel**: Conic-gradient marks ring, letter grade chip, class and course ranking, and delta comparison vs. class average.
  - **Modal Dialogs (`@st.dialog`)**: Next-ID suggestion (`S###`), real-time grade preview, inline validation errors, visual diff on updates, and typed confirmation on delete.
  - **Insights Tab**: Altair visualizations including average marks by course with class benchmark, grade distribution bar charts, and age vs. marks scatter plot.
  - **Activity Tab**: Real-time request log auditing method, endpoint, status, and latency in milliseconds, plus full CSV registry export.
  - **Theme Support**: Synchronized light and dark themes using custom CSS tokens.

- **Vanilla Web UI ([web/](web/)):**
  - **Zero Build Tools**: Built purely with semantic HTML5, CSS3, and ES6+ JavaScript.
  - **Drawer Interface**: Side drawer toggles between student profile inspection and create/edit forms without page reloads.
  - **Confirmation Dialog**: HTML5 native `<dialog>` element for safe deletion workflows.
  - **Live API Diagnostics**: Real-time server latency indicator and connection health checks.
  - **Client-Side Mirroring**: Validates fields client-side before sending requests to minimize server roundtrips.

<details>
<summary><strong>Complete API Reference Table</strong></summary>

| Method | Endpoint | Parameters | Success Status | Error Codes | Description |
|---|---|---|---|---|---|
| `GET` | `/` | None | `200 OK` | — | Welcome greeting array |
| `GET` | `/hello` | None | `200 OK` | — | Hello World greeting array |
| `GET` | `/student` | None | `200 OK` | — | Returns full dictionary of students keyed by ID |
| `GET` | `/student/{id}` | `id` (path, string) | `200 OK` | `404` | Retrieves one student without ID inside object |
| `GET` | `/filter` | `course` (query, string) | `200 OK` | `422` | Case-insensitive filter by course; returns dict |
| `GET` | `/sort` | `sort_by` (`marks`\|`age`\|`name`), `order` (`asc`\|`desc`) | `200 OK` | `404`, `422` | Returns sorted list of student objects with ID included |
| `GET` | `/paginate` | `page` (query, $\ge 1$), `limit` (query, $1 \dots 100$) | `200 OK` | `422` | Returns sliced student list with pagination metadata |
| `POST` | `/create` | Body: `Student` JSON | `201 Created` | `400`, `422` | Creates a new student record; rejects duplicate IDs |
| `PUT` | `/update/{id}` | `id` (path), Body: `StudentUpdate` JSON | `200 OK` | `404`, `422` | Partially updates fields and recalculates grade |
| `DELETE` | `/delete/{student_id}` | `student_id` (path, string) | `200 OK` | `404` | Deletes student record from JSON file |

#### Validation Rules & Grade Thresholds
- **Name**: Letters and spaces only; auto-titled; 2–100 characters on create, 2–50 characters on update.
- **Age**: Integer; 1–100 on create (`gt=0, le=100`), 1–99 on update (`gt=0, lt=100`).
- **Marks**: Integer; 0–100 (`ge=0, le=100`).
- **Course**: 2–100 characters on create, maximum 50 characters on update.
- **Email**: Valid email format verified by Pydantic's `EmailStr`.
- **Grade Calculation**:
  $$\text{Grade} = \begin{cases} \text{A+} & \text{if } \text{marks} \ge 90 \\ \text{A} & \text{if } \text{marks} \ge 80 \\ \text{B} & \text{if } \text{marks} \ge 70 \\ \text{C} & \text{if } \text{marks} \ge 60 \\ \text{F} & \text{otherwise} \end{cases}$$
</details>

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## PostgreSQL and SQLAlchemy ORM

To transition from flat-file storage toward production-grade persistence, the repository explores relational database management and object-relational mapping (ORM) in [`FastAPIandPostgres/playground.py`](FastAPIandPostgres/playground.py). 

This script intentionally isolates the database layer to test direct communication with PostgreSQL using **SQLAlchemy 2.0** before wiring sessions and models into FastAPI route handlers.

### Key Concepts Explored

1. **Environment Configuration (`python-dotenv`):**
   - Keeps credentials out of source control using `.env` (with a sample template provided in [`.env.example`](.env.example)).
   - Reads `DATABASE_URL` dynamically using `os.getenv("DATABASE_URL")`.

2. **Connection & Engine (`create_engine`):**
   - Creates the engine ("the road to the database") and executes a raw verification query (`SELECT version();`) inside a context-managed connection.

3. **Declarative ORM Modeling (`DeclarativeBase`):**
   - Defines a `StudentDB` class inheriting from SQLAlchemy's modern `DeclarativeBase`.
   - Maps class attributes to the `student_records` table with explicit column types, constraints, and keys:
     - `id`: String primary key (e.g. `"S001"`).
     - `name`: String (length 50, `nullable=False`).
     - `age`: Integer (`nullable=False`).
     - `course`: String (length 50, `nullable=False`).
     - `marks`: Integer (`nullable=False`).
     - `email`: String (`unique=True`, `nullable=False`).

4. **Schema Migration & Table Creation (`Base.metadata.create_all`):**
   - Binds to the engine and issues `CREATE TABLE IF NOT EXISTS` statements automatically.

5. **Session Management & CRUD Operations (`sessionmaker`):**
   - **Session Lifecycle:** `SessionLocal = sessionmaker(bind=engine)` creates scoped sessions for database transactions.
   - **Create (Insert):** Adds a record via `db.add(StudentDB(...))` and saves with `db.commit()` only if the record doesn't already exist (`if db.get(StudentDB, "S001") is None:`).
   - **Read (Query):** Queries all records using `db.query(StudentDB).all()`.
   - **Update (Mutate):** Retrieves an entity by primary key using `db.get(StudentDB, "S001")`, modifies attributes in Python (`gaurav.marks = 95`), and persists the change with `db.commit()`.

### Code Walkthrough

```python
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Step 1: Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Step 2: Create engine & test connection
engine = create_engine(DATABASE_URL)
with engine.connect() as connection:
    version = connection.execute(text("SELECT version();")).scalar()
    print(f"Connected to PostgreSQL: {version.split(',')[0]}")

# Step 3: Define Declarative ORM model
class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "student_records"
    id      = Column(String, primary_key=True)
    name    = Column(String(50), nullable=False)
    age     = Column(Integer, nullable=False)
    course  = Column(String(50), nullable=False)
    marks   = Column(Integer, nullable=False)
    email   = Column(String, unique=True, nullable=False)

# Create table schema
Base.metadata.create_all(bind=engine)

# Step 4: Session operations (Create & Update)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

if db.get(StudentDB, "S001") is None:
    db.add(StudentDB(
        id="S001", name="Gaurav Dulal", age=20,
        course="AI", marks=94, email="gqurav69@gmail.com"
    ))
    db.commit()

# Mutate and commit update
gaurav = db.get(StudentDB, "S001")
gaurav.marks = 95
db.commit()
print(f"Updated Marks for {gaurav.name}: {gaurav.marks}")
```

### Running the Database Playground

```powershell
# 1. Create .env from template
cp .env.example .env

# 2. Configure DATABASE_URL in .env:
# DATABASE_URL="postgresql://username:password@localhost:5432/fastapi_db"

# 3. Run the playground script:
python FastAPIandPostgres/playground.py
```

> [!TIP]
> **Learning Strategy:** Practicing SQLAlchemy in a standalone script before introducing FastAPI's `Depends` dependency injection simplifies debugging and ensures the database connection, ORM mappings, and transaction flows work independently.

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Project Structure

```text
FastAPI-Learning/
├── main.py                          # FastAPI service: endpoints, Pydantic models, CORS, and persistence
├── app.py                           # Streamlit dashboard: analytics, roster management, and modal dialogs
├── pydantic_basics.py               # Standalone teaching script: 7-step Pydantic fundamentals walkthrough
├── students.json                    # Flat JSON storage: student records keyed by student ID
├── .env.example                     # Example environment configuration for database credentials
├── pyproject.toml                   # Project configuration: Python version and package dependencies
├── LICENSE                          # MIT License
├── README.md                        # Comprehensive learning documentation and API reference
├── assets/
│   └── banner.svg                   # Custom hand-crafted repository header banner
├── FastAPIandPostgres/
│   └── playground.py                # Standalone SQLAlchemy 2.0 & PostgreSQL CRUD playground script
└── web/
    ├── index.html       # Vanilla HTML semantic structure for web UI
    ├── styles.css       # Complete responsive CSS styles, design tokens, and theme rules
    └── app.js           # Vanilla ES6+ JavaScript API client and interactive UI logic
```

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Progress and Next Steps

### Concepts Learned & Implemented

- [x] Basic routing with `@app.get` decorators and automatic JSON response serialization
- [x] Flat-file data persistence with Python `json.load()` and `json.dump()`
- [x] Path parameters with documentation metadata via `Path(...)`
- [x] Error handling with `HTTPException` and custom status codes
- [x] Query parameters for filtering with `Query(...)`
- [x] Query sorting with multi-field allowlists and reverse ordering
- [x] Pagination with arithmetic slice calculation and numeric bounds (`ge`, `le`)
- [x] Standalone Pydantic fundamentals: `BaseModel`, `Field`, `EmailStr`, `@field_validator`, `@computed_field`
- [x] Request body parsing and validation for POST requests with HTTP 201 Created
- [x] Partial updates with PUT using `model_dump(exclude_unset=True)` and dynamic grade recalculation
- [x] Resource deletion with HTTP DELETE
- [x] Cross-Origin Resource Sharing (CORS) with `CORSMiddleware`
- [x] Analytical frontend with Streamlit, Altair, and `@st.dialog`
- [x] Zero-build vanilla web frontend with HTML5 `<dialog>` and sliding drawer
- [x] PostgreSQL database integration & SQLAlchemy 2.0 ORM playground (engine connection, DeclarativeBase modeling, table creation, and session CRUD)

### Ideas for Next Steps

- [ ] **Database Integration in FastAPI**: Wire SQLAlchemy database sessions into FastAPI route handlers using dependency injection (`Depends`) to replace flat-file JSON persistence in `main.py`.
- [ ] **User Authentication**: Implement JWT token authentication and password hashing using OAuth2 password flow.
- [ ] **Automated Testing**: Write unit and integration test suites using `pytest` and `httpx.AsyncClient`.
- [ ] **Containerization**: Add a `Dockerfile` and `docker-compose.yml` for unified one-command deployment.

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Known Limitations

1. **File-Based Concurrency in Main API**: The primary FastAPI service ([main.py](main.py)) still relies on `students.json` without file locking. PostgreSQL and SQLAlchemy integration has begun in [FastAPIandPostgres/playground.py](FastAPIandPostgres/playground.py) and is slated to be wired into `main.py` in the next phase.
2. **Wildcard CORS Configuration**: The API is configured with `allow_origins=["*"]`, which is suitable for local development but too permissive for production environments.
3. **Model Validation Asymmetry**: Validation bounds differ between `Student` and `StudentUpdate` in [main.py](main.py):
   - `name`: max 100 characters on create vs. max 50 on update.
   - `age`: $\le 100$ on create vs. $< 100$ (max 99) on update.
   - `course`: minimum length of 2 characters required on create, but no minimum length on update.
4. **Non-Standard Sort Status Code**: Passing invalid `sort_by` or `order` values to `/sort` returns `HTTP 404` instead of standard client error codes (`400 Bad Request` or `422 Unprocessable Entity`).
5. **Non-RESTful Route Verbs**: Endpoints use action verbs in paths (e.g. `/create`, `/delete/{student_id}`) rather than canonical RESTful resource patterns (`POST /student`, `DELETE /student/{id}`).
6. **No Authentication or Authorization**: All endpoints are public and allow unauthenticated reads, writes, and deletions.

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>

---

## Credits

This project was built as a structured learning exercise while following an online FastAPI video tutorial:

<!-- TODO: tutorial link/credit -->

Special thanks to the open-source authors and maintainers of **FastAPI**, **Pydantic**, **Starlette**, and **Uvicorn**.

<sub><a href="#fastapi-learning-journey">↑ Back to top</a></sub>
