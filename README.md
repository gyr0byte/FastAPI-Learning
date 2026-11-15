# Student Registry

A student records REST API built with FastAPI, accompanied by a Streamlit data dashboard and a vanilla HTML/CSS/JS web client.

## Overview

This is an educational learning project built while following a FastAPI tutorial, expanded with two distinct frontends that consume the same backend API. The FastAPI service provides full CRUD operations, filtering, sorting, and pagination over student records stored in a local JSON file. Both frontends—an interactive Streamlit application and a lightweight vanilla HTML/CSS/JavaScript web interface—share the same visual design language and communicate with the backend. The repository also includes a step-by-step tutorial script demonstrating Pydantic validation fundamentals.

## Features

### Backend (FastAPI)
- **CRUD operations**: Endpoints to list all students, retrieve a student by ID, create new records, partially update existing records, and delete records.
- **Pydantic validation**: Enforces type hints, field lengths, numeric bounds, valid email formats, and alphabetical name restrictions with automatic title-casing.
- **Computed fields**: Automatically computes student letter grades (`A+`, `A`, `B`, `C`, `F`) based on marks upon creation and update.
- **Query filtering**: Case-insensitive filtering by course name via `/filter`.
- **Query sorting**: Sorting by `marks`, `age`, or `name` in ascending or descending order via `/sort`.
- **Pagination**: Slices records by `page` and `limit` with input constraints via `/paginate`.
- **CORS enabled**: Configured with `CORSMiddleware` to allow local cross-origin browser requests.
- **Interactive API docs**: Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`) documentation.

### Streamlit UI (`app.py`)
- **Overview metrics**: Live stat cards showing total student count, course count, class average marks with passing count, top scorer, and a segmented grade distribution bar.
- **Roster view**:
  - Search filter across student name, email, and ID.
  - Course filter using `st.pills`.
  - Field sorting and direction toggle using `st.segmented_control`.
  - Marks range slider filter (0–100).
  - Configurable page size (5, 10, 20, 50 rows per page) with pagination controls.
  - Interactive table (`st.dataframe`) featuring a progress bar column for marks and single-row selection.
  - Profile side panel for selected students displaying a conic-gradient marks ring, letter grade chip, class and course rank, and comparison against class average.
- **Modal dialogs** (via `@st.dialog`):
  - Add student dialog with auto-suggested next ID (`S###`), live grade preview, delta vs. class average, and inline validation errors that appear after inputs are touched.
  - Edit student dialog with prefilled data, changed-field detection, and visual diff display (old struck through in red, new in green).
  - Delete student dialog requiring typing the student ID to confirm before enabling a red delete button.
- **Insights tab**:
  - Horizontal bar chart of average marks by course with class average dashed reference line (Altair).
  - Grade distribution bar chart with count labels.
  - Interactive age vs. marks scatter plot with zoom/pan and pass cutoff line (60 marks).
- **Activity tab**:
  - Live API request audit log recording HTTP method, path, response code, and latency in milliseconds.
  - CSV export button to download the entire registry with computed grades.
- **Sidebar**:
  - Editable API base URL input.
  - Pulsing connection status indicator (online/offline).
  - Quick find form to look up any student by ID using the singular `/student/{id}` endpoint.
  - Collapsible reference listing all backend endpoints.
- **Theme support**: Automatically detects Streamlit light and dark themes with matched custom CSS tokens.

### Web UI (`web/`)
- **Pure vanilla stack**: Built using standard HTML5, CSS3, and ES6+ JavaScript with zero build steps, npm packages, or external frameworks.
- **Shared editorial visual identity**: Warm color palette, Google Fonts (`Instrument Serif`, `Geist`, `Geist Mono`), custom grade chips, and course dot indicators.
- **Live overview stats**: Real-time cards for student count, class average, top scorer, and segmented grade distribution bar.
- **Toolbar & controls**:
  - Course filter dropdown.
  - Sort field dropdown and Asc/Desc segmented toggle.
  - Search input with debouncing and instant ID lookup on Enter.
  - Rows per page selector (5, 10, 20, 50).
- **Interactive table**:
  - Skeleton loading state with shimmer animation during network requests.
  - Coloured course dot assigned from an 8-color palette based on alphabetical course name index.
  - Marks column with a mini visual progress bar and numeric value.
  - Hover-revealed quick edit and delete action buttons (always visible on mobile).
  - Keyboard accessible: Enter opens the selected row.
- **Slide-in drawer**:
  - Slides in from the right over a dimmed backdrop scrim; closes via Escape key or scrim click.
  - Read-only profile view with a conic-gradient marks ring, grade chip, course rank, and class average delta bar.
  - Integrated create and edit form with course `<datalist>` auto-completion, marks slider with live preview, and inline field error validation.
- **Delete modal**: Native HTML `<dialog>` confirmation requiring the exact student ID to be typed before enabling the delete action.
- **Request line**: Live status bar displaying the method, path, HTTP status code, and latency in milliseconds for the most recent API call.
- **Theme toggle**: Light and dark mode toggle persisted to `localStorage` with system preference (`prefers-color-scheme`) fallback.
- **Responsive design**: Custom layouts with breakpoints at 900px and 640px, plus `prefers-reduced-motion` compliance.

## Project Structure

```text
FastAPI-Learning/
├── main.py              # FastAPI application defining endpoints, Pydantic models, and CORS
├── app.py               # Streamlit dashboard frontend (Roster, Insights, Activity tabs)
├── pydantic_basics.py   # Standalone tutorial demonstrating Pydantic validation concepts
├── students.json        # Local JSON data store containing student records keyed by ID
├── pyproject.toml       # Python project configuration and dependency specifications
├── .gitignore           # Git ignore patterns for virtual environments, caches, and temp files
├── LICENSE              # Project license file (MIT License)
└── web/                 # Vanilla frontend application
    ├── index.html       # Semantic HTML5 layout and drawer/dialog markup
    ├── styles.css       # Complete CSS with design tokens, themes, animations, and responsiveness
    └── app.js           # Vanilla JavaScript API client, state management, and DOM controller
```

## Tech Stack

| Component | Technology | Minimum / Declared Version |
|---|---|---|
| **Language** | Python | `>= 3.10` (declared in `pyproject.toml`) |
| **Backend Framework** | FastAPI | `>= 0.115.0` (declared in `pyproject.toml`) |
| **ASGI Server** | Uvicorn | `>= 0.30.0` (declared in `pyproject.toml` with `[standard]`) |
| **Data Validation** | Pydantic | `>= 2.0` (requires `pydantic[email]` or `email-validator`) |
| **Dashboard UI** | Streamlit | `>= 1.50.0` (requires `st.pills`, `st.segmented_control`, `@st.dialog`, `width="stretch"`) |
| **Data Analysis** | Pandas | `>= 2.0.0` |
| **Data Visualization** | Altair | `>= 5.0.0` |
| **HTTP Client** | Requests | `>= 2.31.0` |
| **Web UI** | HTML5 / CSS3 / JavaScript | Native browser standards (no node / npm / bundler) |
| **Typography** | Google Fonts | `Instrument Serif`, `Geist`, `Geist Mono` |

## Getting Started

### Prerequisites

- Python 3.10 or newer installed on your system.

### 1. Clone and Set Up Environment

#### Using `uv` (Recommended)

```powershell
# Clone the repository
git clone https://github.com/gyr0byte/FastAPI-Learning.git
cd FastAPI-Learning

# Sync dependencies and install frontend packages
uv sync
uv pip install "pydantic[email]" streamlit pandas altair requests
```

#### Using Standard `pip`

On Windows (PowerShell):
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install fastapi "uvicorn[standard]" "pydantic[email]" streamlit pandas altair requests
```

On macOS / Linux (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" "pydantic[email]" streamlit pandas altair requests
```

### 2. Run the Backend API

Start the Uvicorn development server from the repository root:

```powershell
uvicorn main:app --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc alternative: `http://127.0.0.1:8000/redoc`

### 3. Run the Streamlit Dashboard

In a separate terminal window with your virtual environment active:

```powershell
streamlit run app.py
```

The Streamlit UI will open in your default browser at `http://localhost:8501`.

### 4. Run the Vanilla Web UI

You can open `web/index.html` directly in any modern browser, or serve it using Python's built-in HTTP server:

```powershell
python -m http.server 5500 --directory web
```

Then visit `http://127.0.0.1:5500` in your browser. Ensure the FastAPI backend is running on `http://127.0.0.1:8000`.

## API Reference

Source of truth: `main.py`. Base URL: `http://127.0.0.1:8000`.

| Method | Path | Parameters | Success Status | Success Response | Error Codes | Notes |
|---|---|---|---|---|---|---|
| `GET` | `/` | None | `200 OK` | `["Hello and welcome to FastAPI!"]` | None | Greeting endpoint. |
| `GET` | `/hello` | None | `200 OK` | `["Hello, World!"]` | None | Greeting endpoint. |
| `GET` | `/student` | None | `200 OK` | `{ "S001": {...}, ... }` | None | Returns dictionary of all students keyed by student ID. |
| `GET` | `/student/{id}` | Path: `id` (str) | `200 OK` | `{ "name": ..., "age": ..., ... }` | `404` | Returns single student record without `id` inside. Singular path `/student/{id}`. |
| `GET` | `/filter` | Query: `course` (str, required) | `200 OK` | `{ "S003": {...}, ... }` | `422` | Case-insensitive course filter. Returns dict keyed by ID. Does not sort. |
| `GET` | `/sort` | Query: `sort_by` (str), `order` (str) | `200 OK` | `[ { "id": "S001", ... }, ... ]` | `404`, `422` | `sort_by`: `marks`\|`age`\|`name`. `order`: `asc`\|`desc`. Returns list with `id` included. Returns 404 on invalid option. |
| `GET` | `/paginate` | Query: `page` (int, ge=1, default=1), `limit` (int, 1–100, default=2) | `200 OK` | `{ "page": 1, "limit": 2, "total_students": 8, "students": [...] }` | `422` | Server-side pagination. Slices records into pages. |
| `POST` | `/create` | Body: `Student` JSON | `201 Created` | `{ "message": "...", "student": {...} }` | `400`, `422` | Creates student. Computes `grade`. Returns 400 if ID already exists. |
| `PUT` | `/update/{id}` | Path: `id` (str), Body: `StudentUpdate` JSON | `200 OK` | `{ "message": "...", "student": {...} }` | `404`, `422` | Partial update; sends only changed fields. Re-computes `grade`. |
| `DELETE` | `/delete/{student_id}` | Path: `student_id` (str) | `200 OK` | `{ "message": "..." }` | `404` | Deletes student by ID and saves JSON file. |

### Validation Rules

Defined in `Student` and `StudentUpdate` Pydantic models in `main.py`:

- **Student ID (`id`)**: String, required on create. Expected format: `S###` (e.g. `S001`).
- **Name (`name`)**:
  - On create (`Student`): 2 to 100 characters (`min_length=2, max_length=100`).
  - On update (`StudentUpdate`): 2 to 50 characters (`min_length=2, max_length=50`).
  - Validation rule: Must contain only alphabetical characters and spaces (`@field_validator("name")`). Automatically capitalized to title case.
- **Age (`age`)**:
  - On create (`Student`): Integer between 1 and 100 (`gt=0, le=100`).
  - On update (`StudentUpdate`): Integer between 1 and 99 (`gt=0, lt=100`).
- **Course (`course`)**:
  - On create (`Student`): 2 to 100 characters (`min_length=2, max_length=100`).
  - On update (`StudentUpdate`): Up to 50 characters (`max_length=50`).
- **Marks (`marks`)**: Integer between 0 and 100 (`ge=0, le=100`).
- **Email (`email`)**: Valid email format validated by `EmailStr`.
- **Computed Grade (`grade`)**: Calculated dynamically via `@computed_field`:
  - `marks >= 90`: `A+`
  - `marks >= 80`: `A`
  - `marks >= 70`: `B`
  - `marks >= 60`: `C`
  - `marks < 60`: `F`

## Data Format

Student data is stored locally in [`students.json`](students.json) as a top-level JSON object. Each student ID serves as a key, and the value contains the record fields:

```json
{
    "S001": {
        "name": "Gaurav Dulal",
        "age": 20,
        "course": "AI",
        "marks": 100,
        "email": "gqurav69@gmail.com"
    },
    "S002": {
        "name": "John Doe",
        "age": 22,
        "course": "Java",
        "marks": 88,
        "email": "john@example.com"
    }
}
```

> **Important:** The student ID (e.g., `"S001"`) exists solely as the dictionary key in `students.json`. It is not stored as an internal attribute within the student object. The computed `grade` is also not persisted in `students.json`; it is derived at runtime by Pydantic.

## How the Layers Fit Together

```text
┌─────────────────────────┐         ┌─────────────────────────┐
│ Streamlit UI (app.py)   │         │ Web UI (web/index.html) │
│ - Altair charts         │         │ - Pure HTML / CSS / JS  │
│ - Dialogs & dataframes  │         │ - Drawer & native dialog│
└────────────┬────────────┘         └────────────┬────────────┘
             │                                   │
             │ HTTP (Requests)                   │ HTTP (Fetch API + CORS)
             ▼                                   ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Application (main.py)                               │
│ - CORSMiddleware (allow_origins=["*"])                      │
│ - Route handlers: /student, /filter, /sort, /paginate, etc. │
│ - Pydantic models: Student, StudentUpdate                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ json.load() / json.dump()
                              ▼
               ┌──────────────────────────────┐
               │ students.json (Local file)   │
               └──────────────────────────────┘
```

1. **Storage layer**: `students.json` holds the raw records.
2. **Backend API layer**: `main.py` reads and writes `students.json`. It handles validation, grading, route dispatch, error responses, and enables CORS so browser requests from the web UI are permitted without origin blocks.
3. **Frontend layers**: Both Streamlit (`app.py`) and Web (`web/app.js`) communicate exclusively through HTTP calls against the FastAPI endpoints. Both frontends replicate the Pydantic validation rules client-side so users receive instant field-level feedback before any network payload is dispatched.

## Pydantic Fundamentals Script

[`pydantic_basics.py`](pydantic_basics.py) is a standalone tutorial demonstrating how Pydantic evolves data handling from unstructured dictionaries to robust, validated models.

### Step-by-Step Breakdown

1. **Step 1: The Problem with Plain Dictionaries** — Demonstrates that standard Python dicts permit invalid types, negative ages, impossible marks, and garbage email strings without complaint.
2. **Step 2: BaseModel and Type Hints** — Introduces `SimpleStudent(BaseModel)` to enforce types (`str`, `int`), raising `ValidationError` when incompatible data types are supplied.
3. **Step 3: Field Rules and Constraints** — Introduces `RuleStudent(BaseModel)` with `Field(...)`, setting minimum/maximum lengths (`min_length=2, max_length=100`), numerical boundaries (`gt=0, le=100, ge=0`), default values (`course="Python"`), and optional types (`str | None = None`).
4. **Step 4: Email Validation with `EmailStr`** — Uses `EmailStudent(BaseModel)` to validate email format using `EmailStr`.
5. **Step 5: Final Student Model** — Combines all previous techniques into a full `Student` model, adding:
   - A `@field_validator("name")` classmethod that rejects non-alphabetic names and normalizes names to title case.
   - A `@computed_field` property calculating the student's letter grade from their marks.
6. **Step 6: Model Serialization (`model_dump()`)** — Shows how to convert a validated model instance back into a standard Python dictionary for persistence or network transmission.
7. **Step 7: Validating Real Data** — Reads `students.json`, unpacks every record into the `Student` model (`Student(id=student_id, **info)`), and prints the validated records with their calculated grades.

### Running the Script

The script reads `students.json` using a relative file path (`open("students.json", "r")`), so **it must be executed from the project root**:

```powershell
python pydantic_basics.py
```

Expected output:
```text
S001 Gaurav Dulal 20 AI 100 gqurav69@gmail.com A+
S002 John Doe 22 Java 88 john@example.com A
S003 Jane Smith 21 Python 95 jane@example.com A+
S004 Alice Johnson 23 Python 90 alice@example.com A+
S005 Bob Brown 20 Java 85 bob@example.com A
S006 Charlie Davis 22 Python 89 charlie@example.com A
S007 David Evans 21 Java 92 david@example.com A+
S008 Ava Monroe 22 Python 89 ava@example.com A
...
```

## Known Limitations

- **File-based storage concurrency**: `main.py` uses `json.load()` and `json.dump()` directly on `students.json`. There is no file locking or transaction isolation; concurrent writes can cause data loss.
- **Permissive CORS configuration**: `main.py` sets `allow_origins=["*"]`, `allow_methods=["*"]`, and `allow_headers=["*"]`. This is appropriate for local learning, but should be restricted in production.
- **No authentication or authorization**: Endpoints are unprotected. Any client can read, update, or delete student records.
- **Model constraint discrepancies**:
  - `Student` (create) allows `name` up to 100 characters; `StudentUpdate` caps `name` at 50 characters.
  - `Student` allows `age` up to 100 (`le=100`); `StudentUpdate` caps `age` at 99 (`lt=100`).
  - `Student` requires `course` to have at least 2 characters; `StudentUpdate` specifies `max_length=50` without a `min_length`.
- **Non-standard status codes on `/sort`**: Querying `/sort` with an invalid `sort_by` or `order` value raises HTTP `404 Not Found` rather than the more standard `400 Bad Request` or `422 Unprocessable Entity`.
- **Root endpoint response types**: The `@app.get("/")` and `@app.get("/hello")` endpoints return Python `set` literals (e.g. `{"Hello, World!"}`), which serialize as JSON arrays rather than objects.
- **Path convention variations**: Individual retrieval uses `/student/{id}` (singular), while deletion uses `/delete/{student_id}` rather than a RESTful `DELETE /student/{id}`.

## Ideas for Next Steps

1. **Database persistence**: Migrate from `students.json` to SQLite or PostgreSQL using SQLAlchemy or SQLModel for ACID compliance and concurrent write safety.
2. **Automated testing**: Add automated unit and integration tests using `pytest` and HTTPX `TestClient` to verify all endpoints, constraints, and error codes.
3. **Authentication**: Implement JWT token authentication (e.g. OAuth2 password flow) to restrict write endpoints to authenticated administrators.
4. **API standardization**: Refactor endpoints to follow standard REST conventions (`POST /students`, `GET /students/{id}`, `PUT /students/{id}`, `DELETE /students/{id}`) and harmonize Pydantic constraints across create and update schemas.
5. **Containerization**: Add a `Dockerfile` and `docker-compose.yml` to package and run the FastAPI server, Streamlit app, and web server in isolated containers.

## Credits

This project was built as a hands-on learning exercise based on a FastAPI tutorial.

<!-- TODO: add tutorial link/credit -->
