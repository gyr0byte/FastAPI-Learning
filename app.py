"""
Student Registry — Streamlit Frontend
Talking to FastAPI student backend (main.py)
"""

import csv
import html
import io
import math
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import altair as alt
import pandas as pd
import requests
import streamlit as st

# ─── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Student Registry", page_icon="📘", layout="wide")

# ─── Theme Detection & Tokens ───────────────────────────────────────────────────
try:
    _theme_type = st.context.theme.type
except Exception:
    _theme_type = "dark"

IS_DARK = _theme_type == "dark"

if IS_DARK:
    TOK_BG = "#111110"
    TOK_SURFACE = "#1a1916"
    TOK_INK = "#ecebe5"
    TOK_MUTED = "#9a968c"
    TOK_LINE = "#2a2825"
    TOK_ACCENT = "#86bfa9"
    TOK_DANGER = "#e0846f"
else:
    TOK_BG = "#f5f3ee"
    TOK_SURFACE = "#fffdf9"
    TOK_INK = "#1d1c19"
    TOK_MUTED = "#7a766c"
    TOK_LINE = "#e2ded4"
    TOK_ACCENT = "#2d5a4c"
    TOK_DANGER = "#b0412d"

GRADE_COLORS = {
    "A+": "#2d5a4c" if not IS_DARK else "#86bfa9",
    "A":  "#3d7a5c" if not IS_DARK else "#6daa8e",
    "B":  "#6b7a2d" if not IS_DARK else "#a8b86d",
    "C":  "#b8860b" if not IS_DARK else "#daa520",
    "F":  "#b0412d" if not IS_DARK else "#e0846f",
}

COURSE_PALETTE = [
    "#e07b5a", "#d4a843", "#7cb87a", "#5b9bd5",
    "#9b7cb8", "#d47ba0", "#5bbab5", "#b89b5a"
]

METHOD_COLORS = {
    "GET": TOK_ACCENT,
    "POST": "#3b82f6",
    "PUT": "#d97706",
    "DELETE": TOK_DANGER,
}

# ─── Custom CSS Injection ───────────────────────────────────────────────────────
# Hide default Streamlit chrome and inject design language styles
_custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root {
    --tok-bg: %(bg)s;
    --tok-surface: %(surface)s;
    --tok-ink: %(ink)s;
    --tok-muted: %(muted)s;
    --tok-line: %(line)s;
    --tok-accent: %(accent)s;
    --tok-danger: %(danger)s;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
header [data-testid="stDeployButton"] {display: none;}

.brand-heading {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 2.8rem;
    line-height: 1.1;
    color: var(--tok-ink);
}
.brand-heading em {
    font-style: italic;
    color: var(--tok-accent);
}
.brand-subtitle {
    font-family: 'Geist', sans-serif;
    font-size: 0.92rem;
    color: var(--tok-muted);
    margin-top: 4px;
}

.stat-card {
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 12px;
    padding: 18px 20px;
    height: 100%%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.stat-card .stat-label {
    font-family: 'Geist', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--tok-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.stat-card .stat-value {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 2.3rem;
    color: var(--tok-ink);
    line-height: 1.1;
}
.stat-card .stat-sub {
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    color: var(--tok-muted);
    margin-top: 6px;
}

.grade-chip {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
}

.course-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%%;
    margin-right: 6px;
    vertical-align: middle;
}

.request-line {
    font-family: 'Geist Mono', monospace;
    font-size: 0.82rem;
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 8px;
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0 16px 0;
}
.request-line .method {
    font-weight: 700;
    margin-right: 8px;
}
.request-line .status-ok {
    color: var(--tok-accent);
}
.request-line .status-err {
    color: var(--tok-danger);
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    padding: 5px 14px;
    border-radius: 999px;
    border: 1px solid var(--tok-line);
    background: var(--tok-surface);
    margin-bottom: 12px;
}
.status-pill .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%%;
}
.status-pill .dot.online {
    background: #22c55e;
    box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
    animation: pulse 2s infinite ease-in-out;
}
.status-pill .dot.offline {
    background: var(--tok-danger);
}
@keyframes pulse {
    0%%, 100%% { opacity: 1; }
    50%% { opacity: 0.4; }
}

.profile-panel {
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 14px;
    padding: 24px;
}
.profile-panel .profile-name {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 1.8rem;
    color: var(--tok-ink);
    line-height: 1.1;
}
.profile-panel .profile-id {
    font-family: 'Geist Mono', monospace;
    font-size: 0.82rem;
    color: var(--tok-muted);
    margin-top: 2px;
}
.profile-panel .profile-field {
    font-family: 'Geist', sans-serif;
    font-size: 0.88rem;
    color: var(--tok-ink);
    margin: 6px 0;
}
.profile-panel .profile-field-label {
    color: var(--tok-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.marks-ring {
    width: 110px;
    height: 110px;
    border-radius: 50%%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 14px auto;
}
.marks-ring .marks-ring-inner {
    width: 82px;
    height: 82px;
    border-radius: 50%%;
    background: var(--tok-surface);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.marks-ring .marks-value {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 2rem;
    color: var(--tok-ink);
    line-height: 1;
}
.marks-ring .marks-label {
    font-family: 'Geist', sans-serif;
    font-size: 0.7rem;
    color: var(--tok-muted);
}

.grade-bar {
    display: flex;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0;
    background: var(--tok-line);
}
.grade-bar-segment {
    height: 100%%;
}

.empty-state {
    text-align: center;
    padding: 48px 20px;
    color: var(--tok-muted);
    font-family: 'Geist', sans-serif;
}
.empty-state .empty-icon {
    font-size: 2.2rem;
    margin-bottom: 8px;
}

.diff-old {
    text-decoration: line-through;
    color: var(--tok-danger);
    margin-right: 6px;
}
.diff-new {
    color: var(--tok-accent);
    font-weight: 600;
}

.st-key-delete_confirm_container button[kind="primary"] {
    background-color: var(--tok-danger) !important;
    border-color: var(--tok-danger) !important;
    color: #ffffff !important;
}
</style>
""" % {
    "bg": TOK_BG,
    "surface": TOK_SURFACE,
    "ink": TOK_INK,
    "muted": TOK_MUTED,
    "line": TOK_LINE,
    "accent": TOK_ACCENT,
    "danger": TOK_DANGER,
}
st.markdown(_custom_css, unsafe_allow_html=True)


# ─── Session State Initialization ───────────────────────────────────────────────
def init_session_state():
    defaults = {
        "api_base": "http://127.0.0.1:8000",
        "activity_log": [],
        "last_request": None,
        "page": 1,
        "page_size": 10,
        "search_query": "",
        "course_filter": None,
        "sort_field": None,
        "sort_order": "↑ Asc",
        "marks_range": (0, 100),
        "connected": False,
        "toast_msg": None,
        "quick_find_result": None,
        "selected_student_id": None,
        "prev_course_filter": None,
        "prev_sort_field": None,
        "prev_sort_order": "↑ Asc",
        "prev_search_query": "",
        "prev_page_size": 10,
        "prev_marks_range": (0, 100),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()

# Display persisted toast survived across st.rerun()
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="✅")
    st.session_state.toast_msg = None


# ─── Unified API Helper & Custom Error ──────────────────────────────────────────
@dataclass
class ApiError(Exception):
    status: int
    detail: Any
    fields: dict = field(default_factory=dict)
    message: str = ""

    def __post_init__(self):
        if self.status == 422 and isinstance(self.detail, list):
            # Parse FastAPI 422 errors [{loc: [..., "field"], msg: "Value error, ..."}]
            for err in self.detail:
                loc = err.get("loc", [])
                field_name = loc[-1] if loc else "general"
                msg = err.get("msg", "")
                if msg.startswith("Value error, "):
                    msg = msg[len("Value error, "):]
                self.fields[str(field_name)] = msg
            self.message = "; ".join(self.fields.values())
        elif isinstance(self.detail, str):
            self.message = self.detail
        else:
            self.message = str(self.detail)
        super().__init__(self.message)


def api(method: str, path: str, body: Optional[dict] = None) -> Any:
    """Centralized HTTP wrapper with timing, activity logging, and ApiError parsing."""
    base = st.session_state.api_base.rstrip("/")
    url = f"{base}{path}"
    start = time.time()
    status = 0

    try:
        resp = requests.request(method, url, json=body, timeout=8)
        elapsed_ms = int((time.time() - start) * 1000)
        status = resp.status_code

        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status": status,
            "ms": elapsed_ms,
            "ok": 200 <= status < 300,
        }
        st.session_state.activity_log = [log_entry] + st.session_state.activity_log[:99]
        st.session_state.last_request = log_entry
        st.session_state.connected = True

        if 200 <= status < 300:
            return resp.json()
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            raise ApiError(status=status, detail=detail)

    except ApiError:
        raise
    except requests.exceptions.ConnectionError:
        elapsed_ms = int((time.time() - start) * 1000)
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status": 0,
            "ms": elapsed_ms,
            "ok": False,
        }
        st.session_state.activity_log = [log_entry] + st.session_state.activity_log[:99]
        st.session_state.last_request = log_entry
        st.session_state.connected = False
        raise ApiError(status=0, detail="Can't reach the API. Is `uvicorn main:app --reload` running?")
    except requests.exceptions.Timeout:
        elapsed_ms = int((time.time() - start) * 1000)
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status": 0,
            "ms": elapsed_ms,
            "ok": False,
        }
        st.session_state.activity_log = [log_entry] + st.session_state.activity_log[:99]
        st.session_state.last_request = log_entry
        st.session_state.connected = False
        raise ApiError(status=0, detail="Request timed out after 8 seconds.")
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status": 0,
            "ms": elapsed_ms,
            "ok": False,
        }
        st.session_state.activity_log = [log_entry] + st.session_state.activity_log[:99]
        st.session_state.last_request = log_entry
        raise ApiError(status=0, detail=str(e))


# ─── Pure Utility Helpers ───────────────────────────────────────────────────────
def compute_grade(marks: int) -> str:
    m = int(marks)
    if m >= 90:
        return "A+"
    elif m >= 80:
        return "A"
    elif m >= 70:
        return "B"
    elif m >= 60:
        return "C"
    else:
        return "F"


def grade_chip_html(grade: str) -> str:
    color = GRADE_COLORS.get(grade, TOK_MUTED)
    bg = color + "22"
    return f'<span class="grade-chip" style="background:{bg};color:{color};">{html.escape(grade)}</span>'


def course_dot_html(course: str, courses_sorted: list) -> str:
    idx = courses_sorted.index(course) if course in courses_sorted else 0
    color = COURSE_PALETTE[idx % len(COURSE_PALETTE)]
    return f'<span class="course-dot" style="background:{color};"></span>'


def get_next_id(all_students: dict) -> str:
    max_num = 0
    for sid in all_students.keys():
        match = re.match(r"^S(\d+)$", sid, re.IGNORECASE)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return f"S{max_num + 1:03d}"


def dict_to_list(d: dict) -> list:
    """Converts student dict { 'S001': {...} } to list of dicts with 'id' inserted."""
    result = []
    for sid, sdata in d.items():
        row = dict(sdata)
        row["id"] = sid
        result.append(row)
    return result


def render_request_line():
    """Renders the last API call in Geist Mono font."""
    req = st.session_state.last_request
    if req is None:
        return
    method = html.escape(req["method"])
    path = html.escape(req["path"])
    m_color = METHOD_COLORS.get(req["method"], TOK_MUTED)
    status_class = "status-ok" if req["ok"] else "status-err"
    status_text = f'{req["status"]} · {req["ms"]} ms' if req["status"] else f'ERR · {req["ms"]} ms'

    st.markdown(
        f'<div class="request-line">'
        f'<span><span class="method" style="color:{m_color};">{method}</span> {path}</span>'
        f'<span class="{status_class}">{html.escape(status_text)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─── Client-side Validation ─────────────────────────────────────────────────────
def validate_student_fields(data: dict, is_edit: bool = False, existing_ids: set = None) -> dict:
    """Mirrors server validation rules client-side."""
    errors = {}
    sid = data.get("id", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    course = data.get("course", "").strip() if data.get("course") else ""
    age = data.get("age")
    marks = data.get("marks")

    if not is_edit:
        if not sid:
            errors["id"] = "ID is required"
        elif not re.match(r"^S\d+$", sid, re.IGNORECASE):
            errors["id"] = "ID must be in format S### (e.g. S001)"
        elif existing_ids and sid in existing_ids:
            errors["id"] = "Student with this ID already exists"

    if not name:
        errors["name"] = "Name is required"
    elif not re.match(r"^[A-Za-z\s]+$", name):
        errors["name"] = "Name must contain only alphabets and spaces"
    elif is_edit:
        if len(name) < 2 or len(name) > 50:
            errors["name"] = "Name must be 2–50 characters"
    else:
        if len(name) < 2 or len(name) > 100:
            errors["name"] = "Name must be 2–100 characters"

    if age is None:
        errors["age"] = "Age is required"
    elif is_edit:
        if age <= 0 or age >= 100:
            errors["age"] = "Age must be 1–99"
    else:
        if age <= 0 or age > 100:
            errors["age"] = "Age must be 1–100"

    if not course:
        errors["course"] = "Course is required"
    elif is_edit:
        if len(course) > 50:
            errors["course"] = "Course cannot exceed 50 characters"
    else:
        if len(course) < 2 or len(course) > 100:
            errors["course"] = "Course must be 2–100 characters"

    if marks is None or marks < 0 or marks > 100:
        errors["marks"] = "Marks must be between 0 and 100"

    if not email:
        errors["email"] = "Email is required"
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors["email"] = "Invalid email format"

    return errors


# ─── Load Global Data (GET /student) ────────────────────────────────────────────
def load_all_data():
    all_dict = {}
    try:
        all_dict = api("GET", "/student")
        st.session_state.connected = True
    except ApiError:
        st.session_state.connected = False
        return {}, [], [], 0.0

    students_list = dict_to_list(all_dict)
    courses = sorted(set(s.get("course", "") for s in students_list if s.get("course")))
    avg_marks = 0.0
    if students_list:
        avg_marks = sum(s.get("marks", 0) for s in students_list) / len(students_list)
    return all_dict, students_list, courses, avg_marks


all_students_dict, all_students_list, all_courses, class_avg = load_all_data()


# ─── Dialogs ────────────────────────────────────────────────────────────────────
@st.dialog("＋ New Student", width="large")
def add_student_dialog():
    next_id = get_next_id(all_students_dict)
    existing_ids = set(all_students_dict.keys())

    c1, c2 = st.columns(2)
    with c1:
        new_id = st.text_input("Student ID", value=next_id, placeholder="e.g. S001")
    with c2:
        new_name = st.text_input("Full Name", placeholder="e.g. Jane Doe")

    c3, c4 = st.columns(2)
    with c3:
        new_email = st.text_input("Email", placeholder="e.g. jane@example.com")
    with c4:
        new_course = st.selectbox(
            "Course",
            options=all_courses,
            index=None,
            placeholder="Select or type course",
            accept_new_options=True,
        )

    c5, c6 = st.columns(2)
    with c5:
        new_age = st.number_input("Age", min_value=1, max_value=100, value=20)
    with c6:
        new_marks = st.slider("Marks", 0, 100, 75)

    # Live Grade Preview
    grade = compute_grade(new_marks)
    delta = new_marks - class_avg if class_avg > 0 else 0
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"

    st.markdown(
        f'<div style="font-family:\'Geist\',sans-serif;font-size:0.88rem;margin:10px 0;">'
        f'Grade Preview: {grade_chip_html(grade)} '
        f'<span style="color:{TOK_MUTED};font-size:0.82rem;">({delta_str} vs class average)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    data = {
        "id": new_id,
        "name": new_name,
        "email": new_email,
        "course": new_course or "",
        "age": new_age,
        "marks": new_marks,
    }

    touched = bool(new_name.strip() or new_email.strip() or new_course)
    errors = validate_student_fields(data, is_edit=False, existing_ids=existing_ids)

    if touched:
        for fld, msg in errors.items():
            st.caption(f"⚠️ **{fld.capitalize()}**: {msg}")

    can_submit = touched and len(errors) == 0

    if st.button("Create Student", type="primary", disabled=not can_submit, width="stretch"):
        body = {
            "id": new_id.strip(),
            "name": new_name.strip(),
            "age": int(new_age),
            "course": new_course.strip() if new_course else "",
            "marks": int(new_marks),
            "email": new_email.strip(),
        }
        try:
            api("POST", "/create", body)
            st.session_state.toast_msg = f"Student {new_id.strip()} created successfully!"
            st.rerun()
        except ApiError as e:
            if e.fields:
                for fld, msg in e.fields.items():
                    st.error(f"**{fld}**: {msg}")
            else:
                st.error(e.message)


@st.dialog("✏️ Edit Student", width="large")
def edit_student_dialog(student: dict):
    sid = student["id"]
    orig = {k: v for k, v in student.items() if k != "id"}

    st.markdown(
        f'<div style="font-family:\'Geist Mono\',monospace;color:{TOK_MUTED};font-size:0.85rem;margin-bottom:12px;">'
        f'Editing Record: <strong>{html.escape(sid)}</strong></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        e_name = st.text_input("Name", value=orig.get("name", ""))
    with c2:
        e_email = st.text_input("Email", value=orig.get("email", ""))

    course_options = list(all_courses)
    cur_course = orig.get("course", "")
    if cur_course and cur_course not in course_options:
        course_options.insert(0, cur_course)
    course_idx = course_options.index(cur_course) if cur_course in course_options else None

    c3, c4 = st.columns(2)
    with c3:
        e_course = st.selectbox(
            "Course",
            options=course_options,
            index=course_idx,
            accept_new_options=True,
        )
    with c4:
        e_age = st.number_input("Age", min_value=1, max_value=99, value=orig.get("age", 20))

    e_marks = st.slider("Marks", 0, 100, orig.get("marks", 0))

    # Calculate Changed Fields
    changes = {}
    if e_name.strip() != orig.get("name", ""):
        changes["name"] = e_name.strip()
    if e_email.strip() != orig.get("email", ""):
        changes["email"] = e_email.strip()
    if e_course and e_course.strip() != orig.get("course", ""):
        changes["course"] = e_course.strip()
    if e_age != orig.get("age", 0):
        changes["age"] = int(e_age)
    if e_marks != orig.get("marks", 0):
        changes["marks"] = int(e_marks)

    # Show Diff of Changed Fields
    if changes:
        st.markdown(
            f'<div style="font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};margin:12px 0 4px 0;font-weight:600;">'
            f'CHANGES DETECTED:</div>',
            unsafe_allow_html=True,
        )
        for field_name, new_val in changes.items():
            old_val = orig.get(field_name, "")
            st.markdown(
                f'<div style="font-family:\'Geist\',sans-serif;font-size:0.86rem;margin:2px 0;">'
                f'<strong>{html.escape(field_name)}</strong>: '
                f'<span class="diff-old">{html.escape(str(old_val))}</span> → '
                f'<span class="diff-new">{html.escape(str(new_val))}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No fields changed.")

    # Validation
    full_data = {
        "id": sid,
        "name": e_name,
        "email": e_email,
        "course": e_course or "",
        "age": e_age,
        "marks": e_marks,
    }
    errors = validate_student_fields(full_data, is_edit=True)
    for fld, msg in errors.items():
        st.caption(f"⚠️ **{fld.capitalize()}**: {msg}")

    can_save = len(changes) > 0 and len(errors) == 0

    if st.button("Save Changes", type="primary", disabled=not can_save, width="stretch"):
        try:
            api("PUT", f"/update/{sid}", changes)
            st.session_state.toast_msg = f"Student {sid} updated successfully!"
            st.rerun()
        except ApiError as e:
            if e.fields:
                for fld, msg in e.fields.items():
                    st.error(f"**{fld}**: {msg}")
            else:
                st.error(e.message)


@st.dialog("🗑️ Confirm Delete")
def delete_student_dialog(student: dict):
    sid = student["id"]
    name = student.get("name", "Student")

    st.markdown(
        f'<p style="font-family:\'Geist\',sans-serif;color:{TOK_INK};font-size:0.95rem;">'
        f'Are you sure you want to permanently delete <strong>{html.escape(name)}</strong> '
        f'(<code style="font-family:\'Geist Mono\',monospace;">{html.escape(sid)}</code>)?'
        f'</p>',
        unsafe_allow_html=True,
    )
    st.warning("This action cannot be undone.")

    confirm_input = st.text_input(
        f"Type student ID '{sid}' to confirm deletion",
        placeholder=sid,
        autocomplete="off",
    )

    is_confirmed = confirm_input.strip() == sid

    with st.container(key="delete_confirm_container"):
        if st.button(
            "🗑️ Delete Student",
            type="primary",
            disabled=not is_confirmed,
            width="stretch",
            key="delete_confirm_btn",
        ):
            try:
                api("DELETE", f"/delete/{sid}")
                st.session_state.toast_msg = f"Student {sid} deleted successfully!"
                if st.session_state.selected_student_id == sid:
                    st.session_state.selected_student_id = None

                # Adjust page if this delete empties the current page
                total_after = max(0, len(all_students_dict) - 1)
                max_page = max(1, math.ceil(total_after / st.session_state.page_size))
                if st.session_state.page > max_page:
                    st.session_state.page = max_page

                st.rerun()
            except ApiError as e:
                st.error(e.message)


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-family:\'Instrument Serif\',Georgia,serif;font-size:1.6rem;color:{TOK_INK};margin-bottom:8px;">'
        f'📘 Student <i style="color:{TOK_ACCENT};">Registry</i></div>',
        unsafe_allow_html=True,
    )

    new_base = st.text_input(
        "API Base URL",
        value=st.session_state.api_base,
        placeholder="http://127.0.0.1:8000",
    )
    if new_base.strip() != st.session_state.api_base:
        st.session_state.api_base = new_base.strip()
        st.session_state.page = 1
        st.rerun()

    # Connection Status Pill
    if st.session_state.connected:
        st.markdown(
            '<div class="status-pill"><span class="dot online"></span> Connected</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-pill"><span class="dot offline"></span> Offline</div>',
            unsafe_allow_html=True,
        )

    if st.button("🔄 Refresh Data", width="stretch"):
        st.rerun()

    st.divider()

    # Quick Find Section
    st.markdown(
        f'<p style="font-family:\'Geist\',sans-serif;font-size:0.88rem;color:{TOK_INK};font-weight:600;margin-bottom:6px;">'
        f'Quick Find</p>',
        unsafe_allow_html=True,
    )

    with st.form("quick_find_form", clear_on_submit=False):
        qf_id = st.text_input("Enter Student ID", placeholder="e.g. S001", label_visibility="collapsed")
        qf_submit = st.form_submit_button("Find Record", width="stretch")

    if qf_submit and qf_id.strip():
        try:
            # SINGULAR PATH: /student/{id}
            found = api("GET", f"/student/{qf_id.strip()}")
            st.session_state.quick_find_result = {"id": qf_id.strip(), **found}
            st.session_state.selected_student_id = qf_id.strip()
        except ApiError as e:
            st.error(e.message)
            st.session_state.quick_find_result = None

    if st.session_state.quick_find_result:
        q = st.session_state.quick_find_result
        q_grade = compute_grade(q.get("marks", 0))
        st.markdown(
            f'<div class="profile-panel" style="padding:16px;margin-top:8px;">'
            f'<div class="profile-name" style="font-size:1.4rem;">{html.escape(q.get("name", ""))}</div>'
            f'<div class="profile-id">{html.escape(q.get("id", ""))}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Course:</span> {html.escape(q.get("course", ""))}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Marks:</span> {q.get("marks", 0)} {grade_chip_html(q_grade)}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Age:</span> {q.get("age", 0)}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Email:</span> {html.escape(q.get("email", ""))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("✕ Clear Search", key="clear_qf_btn", width="stretch"):
            st.session_state.quick_find_result = None
            st.rerun()

    st.divider()

    # Endpoints Used Expander
    with st.expander("📡 Endpoints in Use"):
        eps = [
            ("GET", "/student"),
            ("GET", "/student/{id}"),
            ("GET", "/filter?course=X"),
            ("GET", "/sort?sort_by=...&order=..."),
            ("GET", "/paginate?page=N&limit=N"),
            ("POST", "/create"),
            ("PUT", "/update/{id}"),
            ("DELETE", "/delete/{id}"),
        ]
        for m, p in eps:
            mc = METHOD_COLORS.get(m, TOK_MUTED)
            st.markdown(
                f'<span style="font-family:\'Geist Mono\',monospace;font-size:0.78rem;">'
                f'<strong style="color:{mc};">{m}</strong> {html.escape(p)}'
                f'</span>',
                unsafe_allow_html=True,
            )


# ─── Header ─────────────────────────────────────────────────────────────────────
head_col, action_col = st.columns([4, 1])
with head_col:
    st.markdown(
        f'<div class="brand-heading">Student <em>Registry</em></div>'
        f'<div class="brand-subtitle">A front desk for your FastAPI student records.</div>',
        unsafe_allow_html=True,
    )
with action_col:
    if st.button(
        "＋ New student",
        type="primary",
        disabled=not st.session_state.connected,
        width="stretch",
    ):
        add_student_dialog()

# Friendly Error Banner when API is unreachable
if not st.session_state.connected and not all_students_dict:
    st.error("🔌 Can't reach the API. Is `uvicorn main:app --reload` running?")


# ─── Stat Cards ─────────────────────────────────────────────────────────────────
if all_students_list:
    total_cnt = len(all_students_list)
    courses_cnt = len(all_courses)
    passing_cnt = sum(1 for s in all_students_list if s.get("marks", 0) >= 60)

    top_stu = max(all_students_list, key=lambda s: s.get("marks", 0))

    # Grade distribution counts
    grade_counts = {"A+": 0, "A": 0, "B": 0, "C": 0, "F": 0}
    for s in all_students_list:
        g = compute_grade(s.get("marks", 0))
        grade_counts[g] = grade_counts.get(g, 0) + 1

    sc1, sc2, sc3, sc4 = st.columns(4)

    with sc1:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Students</div>'
            f'<div class="stat-value">{total_cnt}</div>'
            f'<div class="stat-sub">across {courses_cnt} course{"s" if courses_cnt != 1 else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc2:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Class Average</div>'
            f'<div class="stat-value">{class_avg:.1f}</div>'
            f'<div class="stat-sub">{passing_cnt} of {total_cnt} passing (60+)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc3:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Top Scorer</div>'
            f'<div class="stat-value">{top_stu.get("marks", 0)}</div>'
            f'<div class="stat-sub">{html.escape(top_stu.get("name", ""))} · {html.escape(top_stu.get("course", ""))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc4:
        seg_html = ""
        legend_html = []
        for g in ["A+", "A", "B", "C", "F"]:
            cnt = grade_counts[g]
            pct = (cnt / total_cnt) * 100 if total_cnt > 0 else 0
            if cnt > 0:
                seg_html += f'<div class="grade-bar-segment" style="width:{pct}%;background:{GRADE_COLORS[g]};"></div>'
            legend_html.append(f'{grade_chip_html(g)} <span style="font-size:0.75rem;color:{TOK_MUTED};">{cnt}</span>')

        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Grade Spread</div>'
            f'<div class="grade-bar">{seg_html}</div>'
            f'<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;">'
            f'{" ".join(legend_html)}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─── Request Line ───────────────────────────────────────────────────────────────
render_request_line()


# ─── Main Tabs ──────────────────────────────────────────────────────────────────
tab_roster, tab_insights, tab_activity = st.tabs(["📋 Roster", "📊 Insights", "📝 Activity"])


# ─── 1. Roster Tab ──────────────────────────────────────────────────────────────
with tab_roster:
    if not all_students_dict:
        st.markdown(
            f'<div class="empty-state">'
            f'<div class="empty-icon">📭</div>'
            f'<p>No students available. Make sure the FastAPI server is running or add your first student!</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Search & Rows-per-page controls
        ctrl_l, ctrl_r = st.columns([3, 1])
        with ctrl_l:
            search_val = st.text_input(
                "Search",
                placeholder="🔍 Search name, email, or ID…",
                label_visibility="collapsed",
                key="roster_search_input",
            )
            st.session_state.search_query = search_val
        with ctrl_r:
            page_sizes = [5, 10, 20, 50]
            cur_psize_idx = page_sizes.index(st.session_state.page_size) if st.session_state.page_size in page_sizes else 1
            psize_sel = st.selectbox(
                "Rows per page",
                options=page_sizes,
                index=cur_psize_idx,
                label_visibility="collapsed",
                key="roster_page_size_sel",
            )
            st.session_state.page_size = psize_sel

        # Course filter using st.pills
        pills_options = ["All"] + all_courses
        cur_pills_default = st.session_state.course_filter if st.session_state.course_filter in all_courses else "All"
        course_pill = st.pills("Course Filter", options=pills_options, default=cur_pills_default, key="course_pills_ctrl")
        st.session_state.course_filter = None if course_pill == "All" else course_pill

        # Sort-by segmented controls & Marks range slider
        sort_col1, sort_col2, sort_col3 = st.columns([2, 2, 3])
        with sort_col1:
            sort_by_sel = st.segmented_control(
                "Sort by",
                options=["None", "Marks", "Name", "Age"],
                default=st.session_state.sort_field or "None",
                key="sort_by_segmented",
            )
            st.session_state.sort_field = None if sort_by_sel == "None" else sort_by_sel

        with sort_col2:
            order_sel = st.segmented_control(
                "Order",
                options=["↑ Asc", "↓ Desc"],
                default=st.session_state.sort_order,
                key="sort_order_segmented",
            )
            order_sel = order_sel or "↑ Asc"
            st.session_state.sort_order = order_sel

        with sort_col3:
            marks_rng = st.slider(
                "Marks range",
                0,
                100,
                st.session_state.marks_range,
                key="marks_range_filter",
            )
            st.session_state.marks_range = marks_rng

        # Reset page on any control changes
        if (
            st.session_state.course_filter != st.session_state.prev_course_filter
            or st.session_state.sort_field != st.session_state.prev_sort_field
            or st.session_state.sort_order != st.session_state.prev_sort_order
            or st.session_state.search_query != st.session_state.prev_search_query
            or st.session_state.page_size != st.session_state.prev_page_size
            or st.session_state.marks_range != st.session_state.prev_marks_range
        ):
            st.session_state.page = 1
            st.session_state.prev_course_filter = st.session_state.course_filter
            st.session_state.prev_sort_field = st.session_state.sort_field
            st.session_state.prev_sort_order = st.session_state.sort_order
            st.session_state.prev_search_query = st.session_state.search_query
            st.session_state.prev_page_size = st.session_state.page_size
            st.session_state.prev_marks_range = st.session_state.marks_range

        # ── Fetch Table Data according to 3-tier rules ──
        c_filter = st.session_state.course_filter
        s_field = st.session_state.sort_field
        s_order = "asc" if st.session_state.sort_order == "↑ Asc" else "desc"
        sort_map = {"Marks": "marks", "Name": "name", "Age": "age"}
        page_num = st.session_state.page
        page_limit = st.session_state.page_size

        display_list = []
        total_items = 0
        error_msg = None

        try:
            if c_filter:
                # 1. Course selected -> GET /filter
                f_dict = api("GET", f"/filter?course={requests.utils.quote(c_filter)}")
                display_list = dict_to_list(f_dict)
                if s_field:
                    k = sort_map.get(s_field, "marks")
                    display_list.sort(key=lambda s: s.get(k, ""), reverse=(s_order == "desc"))

            elif s_field:
                # 2. Sort field chosen (no course) -> GET /sort
                k = sort_map.get(s_field, "marks")
                display_list = api("GET", f"/sort?sort_by={k}&order={s_order}")

            else:
                # 3. Neither -> GET /paginate (server-side)
                # If search or marks range active, use client dataset
                if search_val.strip() or marks_rng != (0, 100):
                    display_list = dict_to_list(all_students_dict)
                else:
                    pag_data = api("GET", f"/paginate?page={page_num}&limit={page_limit}")
                    total_items = pag_data.get("total_students", 0)
                    display_list = pag_data.get("students", [])

        except ApiError as e:
            error_msg = e.message

        # Client-side filtering (Marks range + Search query)
        if c_filter or s_field or search_val.strip() or marks_rng != (0, 100):
            # Apply marks range
            display_list = [s for s in display_list if marks_rng[0] <= s.get("marks", 0) <= marks_rng[1]]

            # Apply client search query
            if search_val.strip():
                q = search_val.strip().lower()
                display_list = [
                    s for s in display_list
                    if q in s.get("name", "").lower()
                    or q in s.get("email", "").lower()
                    or q in s.get("id", "").lower()
                ]

            total_items = len(display_list)
            total_pages = max(1, math.ceil(total_items / page_limit))
            if page_num > total_pages:
                page_num = total_pages
                st.session_state.page = page_num

            start_idx = (page_num - 1) * page_limit
            end_idx = start_idx + page_limit
            paginated_students = display_list[start_idx:end_idx]
        else:
            total_pages = max(1, math.ceil(total_items / page_limit))
            paginated_students = display_list

        if error_msg:
            st.error(error_msg)

        # ── Two-Column Layout: Table + Right-hand Profile Panel ──
        table_col, profile_col = st.columns([3, 2])

        with table_col:
            if paginated_students:
                table_rows = []
                for s in paginated_students:
                    grade = compute_grade(s.get("marks", 0))
                    table_rows.append({
                        "ID": s.get("id", ""),
                        "Name": s.get("name", ""),
                        "Course": s.get("course", ""),
                        "Age": s.get("age", 0),
                        "Marks": s.get("marks", 0),
                        "Grade": grade,
                        "Email": s.get("email", ""),
                    })

                df = pd.DataFrame(table_rows)

                # Unique key resets selection when filter/page changes
                view_key = f"roster_{c_filter}_{s_field}_{s_order}_{page_num}_{page_limit}_{search_val}_{marks_rng}"

                column_config = {
                    "Marks": st.column_config.ProgressColumn(
                        "Marks",
                        min_value=0,
                        max_value=100,
                        format="%d",
                    ),
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "Grade": st.column_config.TextColumn("Grade", width="small"),
                }

                event = st.dataframe(
                    df,
                    column_config=column_config,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key=view_key,
                    width="stretch",
                )

                # Pager controls
                pg1, pg2, pg3 = st.columns([1, 2, 1])
                with pg1:
                    if st.button("← Prev", disabled=page_num <= 1, width="stretch", key="btn_prev_pg"):
                        st.session_state.page = max(1, page_num - 1)
                        st.rerun()
                with pg2:
                    start_disp = (page_num - 1) * page_limit + 1 if total_items > 0 else 0
                    end_disp = min(page_num * page_limit, total_items)
                    st.markdown(
                        f'<div style="text-align:center;font-family:\'Geist\',sans-serif;font-size:0.85rem;color:{TOK_MUTED};padding:6px 0;">'
                        f'{start_disp}–{end_disp} of {total_items} · page {page_num} of {total_pages}</div>',
                        unsafe_allow_html=True,
                    )
                with pg3:
                    if st.button("Next →", disabled=page_num >= total_pages, width="stretch", key="btn_next_pg"):
                        st.session_state.page = page_num + 1
                        st.rerun()

                # Get selected student from table selection
                selected_student = None
                if event and event.selection and event.selection.rows:
                    sel_idx = event.selection.rows[0]
                    if sel_idx < len(paginated_students):
                        selected_student = paginated_students[sel_idx]
                        st.session_state.selected_student_id = selected_student.get("id")

                elif st.session_state.selected_student_id:
                    # Keep selected if in all_students_dict
                    sid = st.session_state.selected_student_id
                    if sid in all_students_dict:
                        selected_student = {"id": sid, **all_students_dict[sid]}

            else:
                st.markdown(
                    f'<div class="empty-state">'
                    f'<div class="empty-icon">🔍</div>'
                    f'<p>No students match your filter criteria.</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                selected_student = None

        with profile_col:
            if selected_student:
                s = selected_student
                s_name = html.escape(s.get("name", ""))
                s_id = html.escape(s.get("id", ""))
                s_marks = s.get("marks", 0)
                s_grade = compute_grade(s_marks)
                s_course = html.escape(s.get("course", ""))
                s_age = s.get("age", 0)
                s_email = html.escape(s.get("email", ""))

                # Ranks computation
                sorted_overall = sorted(all_students_list, key=lambda x: x.get("marks", 0), reverse=True)
                rank_overall = next((i + 1 for i, x in enumerate(sorted_overall) if x.get("id") == s.get("id")), 1)

                course_peers = [x for x in all_students_list if x.get("course") == s.get("course")]
                sorted_course = sorted(course_peers, key=lambda x: x.get("marks", 0), reverse=True)
                rank_course = next((i + 1 for i, x in enumerate(sorted_course) if x.get("id") == s.get("id")), 1)

                # Conic gradient ring
                ring_color = GRADE_COLORS.get(s_grade, TOK_ACCENT)
                deg = (s_marks / 100) * 360

                # vs Class Average
                delta = s_marks - class_avg
                delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
                delta_color = TOK_ACCENT if delta >= 0 else TOK_DANGER

                st.markdown(
                    f'<div class="profile-panel">'
                    f'<div class="profile-name">{s_name}</div>'
                    f'<div class="profile-id">{s_id}</div>'
                    f'<div class="marks-ring" style="background:conic-gradient({ring_color} {deg}deg, {TOK_LINE} {deg}deg);">'
                    f'<div class="marks-ring-inner">'
                    f'<span class="marks-value">{s_marks}</span>'
                    f'<span class="marks-label">/ 100</span>'
                    f'</div>'
                    f'</div>'
                    f'<div style="text-align:center;margin:4px 0 10px 0;">{grade_chip_html(s_grade)}</div>'
                    f'<div style="text-align:center;font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};margin-bottom:14px;">'
                    f'Rank #{rank_overall} overall · #{rank_course} in {s_course}</div>'
                    f'<hr style="border:none;border-top:1px solid {TOK_LINE};margin:12px 0;">'
                    f'<div class="profile-field"><span class="profile-field-label">Course</span><br>'
                    f'{course_dot_html(s.get("course", ""), all_courses)}{s_course}</div>'
                    f'<div class="profile-field"><span class="profile-field-label">Age</span><br>{s_age} years old</div>'
                    f'<div class="profile-field"><span class="profile-field-label">Email</span><br>{s_email}</div>'
                    f'<hr style="border:none;border-top:1px solid {TOK_LINE};margin:12px 0;">'
                    f'<div style="font-family:\'Geist\',sans-serif;font-size:0.78rem;color:{TOK_MUTED};font-weight:600;text-transform:uppercase;margin-bottom:6px;">vs Class Average</div>'
                    f'<div style="display:flex;align-items:center;gap:10px;">'
                    f'<div style="flex:1;height:8px;background:{TOK_LINE};border-radius:4px;position:relative;">'
                    f'<div style="height:100%;width:{min(s_marks, 100)}%;background:{ring_color};border-radius:4px;"></div>'
                    f'<div style="position:absolute;top:-4px;left:{min(class_avg, 100)}%;width:2px;height:16px;background:{TOK_MUTED};"></div>'
                    f'</div>'
                    f'<span style="font-family:\'Geist Mono\',monospace;font-size:0.84rem;color:{delta_color};font-weight:600;">{delta_str}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("✏️ Edit", width="stretch", key="btn_edit_profile"):
                        edit_student_dialog(s)
                with b_col2:
                    if st.button("🗑️ Delete", width="stretch", key="btn_delete_profile"):
                        delete_student_dialog(s)
            else:
                st.markdown(
                    f'<div class="empty-state" style="margin-top:28px;">'
                    f'<div class="empty-icon">👈</div>'
                    f'<div style="font-family:\'Instrument Serif\',Georgia,serif;font-size:1.6rem;color:{TOK_INK};">No one selected</div>'
                    f'<p style="margin-top:4px;">Click any row in the table to view their full profile.</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ─── 2. Insights Tab ────────────────────────────────────────────────────────────
with tab_insights:
    if not all_students_list:
        st.info("No student data available to visualize.")
    else:
        # Chart styling colors matching active theme
        c_axis = alt.Axis(
            labelColor=TOK_MUTED,
            titleColor=TOK_MUTED,
            gridColor=TOK_LINE,
            domainColor=TOK_LINE,
            tickColor=TOK_LINE,
        )

        # ── Chart 1: Average Marks by Course ──
        st.markdown(
            f'<div style="font-family:\'Geist\',sans-serif;font-size:1.05rem;font-weight:600;color:{TOK_INK};margin:14px 0 6px 0;">'
            f'Average Marks by Course</div>',
            unsafe_allow_html=True,
        )

        course_avgs = []
        for c in all_courses:
            peers = [s for s in all_students_list if s.get("course") == c]
            if peers:
                avg = sum(s.get("marks", 0) for s in peers) / len(peers)
                course_avgs.append({"Course": c, "Average Marks": round(avg, 1), "Students": len(peers)})

        if course_avgs:
            df_course = pd.DataFrame(course_avgs)

            hover_course = alt.selection_point(on="pointerover", fields=["Course"], empty=False)

            bars = alt.Chart(df_course).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("Average Marks:Q", title="Average Marks", axis=c_axis),
                y=alt.Y("Course:N", sort="-x", title="", axis=c_axis),
                color=alt.value(TOK_ACCENT),
                opacity=alt.condition(hover_course, alt.value(1), alt.value(0.6)),
                tooltip=["Course", "Average Marks", "Students"],
            ).add_params(hover_course)

            class_avg_rule = alt.Chart(pd.DataFrame({"avg": [class_avg]})).mark_rule(
                strokeDash=[6, 4],
                color=TOK_DANGER,
                strokeWidth=1.5,
            ).encode(
                x="avg:Q",
                tooltip=[alt.Tooltip("avg:Q", title="Class Average", format=".1f")],
            )

            chart1 = (bars + class_avg_rule).properties(
                height=max(180, len(course_avgs) * 36)
            ).configure_view(strokeWidth=0)

            st.altair_chart(chart1, width="stretch")

        # ── Chart 2: Grade Distribution ──
        st.markdown(
            f'<div style="font-family:\'Geist\',sans-serif;font-size:1.05rem;font-weight:600;color:{TOK_INK};margin:24px 0 6px 0;">'
            f'Grade Distribution</div>',
            unsafe_allow_html=True,
        )

        grade_data = []
        for g in ["A+", "A", "B", "C", "F"]:
            cnt = sum(1 for s in all_students_list if compute_grade(s.get("marks", 0)) == g)
            grade_data.append({"Grade": g, "Count": cnt})

        df_grade = pd.DataFrame(grade_data)

        grade_bars = alt.Chart(df_grade).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Grade:N", sort=["A+", "A", "B", "C", "F"], title="Grade", axis=alt.Axis(labelAngle=0, labelColor=TOK_MUTED, titleColor=TOK_MUTED, domainColor=TOK_LINE)),
            y=alt.Y("Count:Q", title="Number of Students", axis=c_axis),
            color=alt.Color("Grade:N", scale=alt.Scale(
                domain=["A+", "A", "B", "C", "F"],
                range=[GRADE_COLORS["A+"], GRADE_COLORS["A"], GRADE_COLORS["B"], GRADE_COLORS["C"], GRADE_COLORS["F"]],
            ), legend=None),
            tooltip=["Grade", "Count"],
        )

        grade_labels = grade_bars.mark_text(dy=-10, fontSize=12, color=TOK_MUTED).encode(
            text="Count:Q",
        )

        chart2 = (grade_bars + grade_labels).properties(height=260).configure_view(strokeWidth=0)
        st.altair_chart(chart2, width="stretch")

        # ── Chart 3: Age vs Marks Scatter Plot ──
        st.markdown(
            f'<div style="font-family:\'Geist\',sans-serif;font-size:1.05rem;font-weight:600;color:{TOK_INK};margin:24px 0 6px 0;">'
            f'Age vs Marks</div>',
            unsafe_allow_html=True,
        )

        scatter_data = []
        for s in all_students_list:
            scatter_data.append({
                "Age": s.get("age", 0),
                "Marks": s.get("marks", 0),
                "Name": s.get("name", ""),
                "Course": s.get("course", ""),
                "Grade": compute_grade(s.get("marks", 0)),
            })

        df_scatter = pd.DataFrame(scatter_data)

        legend_selection = alt.selection_point(fields=["Course"], bind="legend")

        scatter = alt.Chart(df_scatter).mark_circle(size=90).encode(
            x=alt.X("Age:Q", title="Age", scale=alt.Scale(zero=False), axis=c_axis),
            y=alt.Y("Marks:Q", title="Marks", scale=alt.Scale(domain=[0, 105]), axis=c_axis),
            color=alt.Color("Course:N", scale=alt.Scale(
                domain=all_courses,
                range=COURSE_PALETTE[:len(all_courses)],
            )),
            opacity=alt.condition(legend_selection, alt.value(0.9), alt.value(0.15)),
            tooltip=["Name", "Age", "Marks", "Course", "Grade"],
        ).add_params(legend_selection).interactive()

        pass_rule = alt.Chart(pd.DataFrame({"y": [60]})).mark_rule(
            strokeDash=[6, 4],
            color=TOK_DANGER,
            strokeWidth=1.5,
        ).encode(
            y="y:Q",
            tooltip=[alt.Tooltip("y:Q", title="Pass Cutoff (60)")],
        )

        chart3 = (scatter + pass_rule).properties(height=340).configure_view(strokeWidth=0).configure_legend(
            labelColor=TOK_MUTED,
            titleColor=TOK_MUTED,
        )
        st.altair_chart(chart3, width="stretch")


# ─── 3. Activity Tab ────────────────────────────────────────────────────────────
with tab_activity:
    act_col1, act_col2 = st.columns([1, 1])
    with act_col1:
        if st.button("🗑️ Clear Log", width="stretch", key="btn_clear_log"):
            st.session_state.activity_log = []
            st.rerun()

    with act_col2:
        # Export CSV of all students with computed grade
        if all_students_list:
            csv_buf = io.StringIO()
            fieldnames = ["id", "name", "age", "course", "marks", "email", "grade"]
            writer = csv.DictWriter(csv_buf, fieldnames=fieldnames)
            writer.writeheader()
            for s in all_students_list:
                writer.writerow({
                    "id": s.get("id", ""),
                    "name": s.get("name", ""),
                    "age": s.get("age", 0),
                    "course": s.get("course", ""),
                    "marks": s.get("marks", 0),
                    "email": s.get("email", ""),
                    "grade": compute_grade(s.get("marks", 0)),
                })
            st.download_button(
                "📥 Export CSV",
                csv_buf.getvalue(),
                "students_registry.csv",
                "text/csv",
                width="stretch",
                key="btn_download_csv",
            )
        else:
            st.download_button(
                "📥 Export CSV",
                "",
                "students.csv",
                "text/csv",
                disabled=True,
                width="stretch",
            )

    log_entries = st.session_state.activity_log
    if not log_entries:
        st.markdown(
            f'<div class="empty-state">'
            f'<div class="empty-icon">📝</div>'
            f'<p>No API requests recorded yet in this session.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        log_rows = []
        for entry in log_entries:
            log_rows.append({
                "Time": entry["time"],
                "Method": entry["method"],
                "Path": entry["path"],
                # Status cast to string to avoid PyArrow type mismatch
                "Status": str(entry["status"]),
                "ms": entry["ms"],
                "OK": "✅" if entry["ok"] else "❌",
            })

        df_log = pd.DataFrame(log_rows)
        st.dataframe(df_log, hide_index=True, width="stretch")
