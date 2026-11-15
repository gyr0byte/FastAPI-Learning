import streamlit as st
import requests
import time
import html
import math
import csv
import io
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Student Registry", page_icon="📘", layout="wide")

# ─── Theme Detection ────────────────────────────────────────────────────────────
try:
    _theme_type = st.context.theme.type
except Exception:
    _theme_type = "dark"

IS_DARK = _theme_type == "dark"

# ─── Design Tokens ───────────────────────────────────────────────────────────────
if IS_DARK:
    TOK_BG = "#111110"
    TOK_SURFACE = "#1a1916"
    TOK_INK = "#ecebe5"
    TOK_MUTED = "#7a766c"
    TOK_LINE = "#2a2822"
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
    "A+": "#1b7a44" if not IS_DARK else "#4caf6a",
    "A": "#2e8b57" if not IS_DARK else "#66bb6a",
    "B": "#6b8e23" if not IS_DARK else "#9e9d24",
    "C": "#d4a017" if not IS_DARK else "#ffb300",
    "F": "#c0392b" if not IS_DARK else "#ef5350",
}

COURSE_PALETTE = ["#e07b5a", "#5a9fd4", "#8bc34a", "#ab47bc", "#26a69a", "#ff7043", "#5c6bc0", "#78909c"]

METHOD_COLORS = {
    "GET": TOK_ACCENT,
    "POST": "#4a90d9",
    "PUT": "#d4a017",
    "DELETE": TOK_DANGER,
}

# ─── CSS Injection ───────────────────────────────────────────────────────────────
_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap');

:root {{
    --tok-bg: {TOK_BG};
    --tok-surface: {TOK_SURFACE};
    --tok-ink: {TOK_INK};
    --tok-muted: {TOK_MUTED};
    --tok-line: {TOK_LINE};
    --tok-accent: {TOK_ACCENT};
    --tok-danger: {TOK_DANGER};
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
[data-testid="stStatusWidget"] {{visibility: hidden;}}
header [data-testid="stDeployButton"] {{display: none;}}

.title-font {{
    font-family: 'Instrument Serif', serif;
}}
.ui-font {{
    font-family: 'Geist', sans-serif;
}}
.mono-font {{
    font-family: 'Geist Mono', monospace;
}}

.stat-card {{
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 12px;
    padding: 20px 22px;
    height: 100%%;
}}
.stat-card .stat-label {{
    font-family: 'Geist', sans-serif;
    font-size: 0.78rem;
    color: var(--tok-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}}
.stat-card .stat-value {{
    font-family: 'Instrument Serif', serif;
    font-size: 2.2rem;
    color: var(--tok-ink);
    line-height: 1.1;
}}
.stat-card .stat-sub {{
    font-family: 'Geist', sans-serif;
    font-size: 0.8rem;
    color: var(--tok-muted);
    margin-top: 4px;
}}

.grade-chip {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-family: 'Geist', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
}}

.course-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%%;
    margin-right: 6px;
    vertical-align: middle;
}}

.request-line {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.82rem;
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 8px;
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0 12px 0;
}}
.request-line .method {{
    font-weight: 700;
    margin-right: 8px;
}}
.request-line .status-ok {{
    color: var(--tok-accent);
}}
.request-line .status-err {{
    color: var(--tok-danger);
}}

.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Geist', sans-serif;
    font-size: 0.82rem;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--tok-line);
    background: var(--tok-surface);
}}
.status-pill .dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%%;
}}
.status-pill .dot.online {{
    background: #4caf50;
    animation: pulse 2s infinite;
}}
.status-pill .dot.offline {{
    background: var(--tok-danger);
}}
@keyframes pulse {{
    0%%, 100%% {{ opacity: 1; }}
    50%% {{ opacity: 0.4; }}
}}

.profile-panel {{
    background: var(--tok-surface);
    border: 1px solid var(--tok-line);
    border-radius: 14px;
    padding: 24px;
}}
.profile-panel .profile-name {{
    font-family: 'Instrument Serif', serif;
    font-size: 1.6rem;
    color: var(--tok-ink);
}}
.profile-panel .profile-id {{
    font-family: 'Geist Mono', monospace;
    font-size: 0.82rem;
    color: var(--tok-muted);
}}
.profile-panel .profile-field {{
    font-family: 'Geist', sans-serif;
    font-size: 0.88rem;
    color: var(--tok-ink);
    margin: 4px 0;
}}
.profile-panel .profile-field-label {{
    color: var(--tok-muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}

.marks-ring {{
    width: 100px;
    height: 100px;
    border-radius: 50%%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 12px auto;
}}
.marks-ring .marks-value {{
    font-family: 'Instrument Serif', serif;
    font-size: 1.8rem;
    color: var(--tok-ink);
}}

.grade-bar {{
    display: flex;
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
    margin: 6px 0;
}}
.grade-bar-segment {{
    height: 100%%;
}}

.empty-state {{
    text-align: center;
    padding: 40px 20px;
    color: var(--tok-muted);
    font-family: 'Geist', sans-serif;
}}
.empty-state .empty-icon {{
    font-size: 2.4rem;
    margin-bottom: 8px;
}}

.diff-old {{
    text-decoration: line-through;
    color: var(--tok-danger);
    margin-right: 6px;
}}
.diff-new {{
    color: var(--tok-accent);
    font-weight: 600;
}}

.delete-container {{
    border: 2px solid var(--tok-danger);
    border-radius: 10px;
    padding: 16px;
}}
</style>
"""
st.markdown(_css, unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────────────────────────
def _init_state():
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


_init_state()

# Show pending toast
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="✅")
    st.session_state.toast_msg = None


# ─── API Helper ──────────────────────────────────────────────────────────────────
@dataclass
class ApiError(Exception):
    status: int
    detail: Any
    fields: dict = field(default_factory=dict)
    message: str = ""

    def __post_init__(self):
        if self.status == 422 and isinstance(self.detail, list):
            for err in self.detail:
                loc = err.get("loc", [])
                field_name = loc[-1] if loc else "unknown"
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
    base = st.session_state.api_base.rstrip("/")
    url = f"{base}{path}"
    start = time.time()
    status = 0
    try:
        resp = requests.request(method, url, json=body, timeout=8)
        elapsed_ms = int((time.time() - start) * 1000)
        status = resp.status_code
        # Record to log
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status": status,
            "ms": elapsed_ms,
            "ok": 200 <= status < 300,
        }
        log = list(st.session_state.activity_log)
        log.insert(0, log_entry)
        st.session_state.activity_log = log[:100]
        st.session_state.last_request = log_entry
        st.session_state.connected = True

        if 200 <= status < 300:
            return resp.json()
        else:
            detail = resp.json().get("detail", resp.text)
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
        log = list(st.session_state.activity_log)
        log.insert(0, log_entry)
        st.session_state.activity_log = log[:100]
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
        log = list(st.session_state.activity_log)
        log.insert(0, log_entry)
        st.session_state.activity_log = log[:100]
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
        log = list(st.session_state.activity_log)
        log.insert(0, log_entry)
        st.session_state.activity_log = log[:100]
        st.session_state.last_request = log_entry
        raise ApiError(status=0, detail=str(e))


# ─── Utility Functions ───────────────────────────────────────────────────────────
def compute_grade(marks: int) -> str:
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    else:
        return "F"


def grade_chip_html(grade: str) -> str:
    color = GRADE_COLORS.get(grade, TOK_MUTED)
    bg = color + "22"
    return f'<span class="grade-chip" style="background:{bg};color:{color};">{html.escape(grade)}</span>'


def course_dot_html(course: str, courses_sorted: list) -> str:
    idx = 0
    if course in courses_sorted:
        idx = courses_sorted.index(course)
    color = COURSE_PALETTE[idx % len(COURSE_PALETTE)]
    return f'<span class="course-dot" style="background:{color};"></span>'


def get_next_id(all_students: dict) -> str:
    max_num = 0
    for sid in all_students.keys():
        try:
            num = int(sid[1:])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            pass
    return f"S{max_num + 1:03d}"


def dict_to_list(d: dict) -> list:
    result = []
    for sid, sdata in d.items():
        row = dict(sdata)
        row["id"] = sid
        result.append(row)
    return result


def render_request_line():
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


# ─── Data Loading ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_all_students(_base_url: str) -> dict:
    """Load all students via GET /student. Returns raw dict keyed by ID."""
    try:
        return api("GET", "/student")
    except ApiError:
        return {}


def load_data():
    """Load all students and compute derived data."""
    all_students = {}
    try:
        all_students = api("GET", "/student")
        st.session_state.connected = True
    except ApiError:
        st.session_state.connected = False
        return {}, [], [], 0.0

    students_list = dict_to_list(all_students)
    courses = sorted(set(s.get("course", "") for s in students_list))
    avg_marks = 0.0
    if students_list:
        avg_marks = sum(s.get("marks", 0) for s in students_list) / len(students_list)
    return all_students, students_list, courses, avg_marks


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-family:\'Instrument Serif\',serif;font-size:1.5rem;color:{TOK_INK};">📘 Student <i style="color:{TOK_ACCENT};">Registry</i></div>',
        unsafe_allow_html=True,
    )

    st.session_state.api_base = st.text_input(
        "API Base URL",
        value=st.session_state.api_base,
        placeholder="http://127.0.0.1:8000",
    )

    # Status pill
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

    if st.button("🔄 Refresh", width="stretch"):
        load_all_students.clear()
        st.rerun()

    st.divider()

    # Quick find
    st.markdown(f'<p style="font-family:\'Geist\',sans-serif;font-size:0.88rem;color:{TOK_INK};font-weight:500;">Quick find</p>', unsafe_allow_html=True)
    with st.form("quick_find_form", clear_on_submit=False):
        qf_id = st.text_input("Student ID", placeholder="e.g. S001", label_visibility="collapsed")
        qf_submit = st.form_submit_button("Find", width="stretch")

    if qf_submit and qf_id.strip():
        try:
            result = api("GET", f"/student/{qf_id.strip()}")
            st.session_state.quick_find_result = {"id": qf_id.strip(), **result}
        except ApiError as e:
            st.error(e.message)
            st.session_state.quick_find_result = None

    if st.session_state.quick_find_result:
        s = st.session_state.quick_find_result
        grade = compute_grade(s.get("marks", 0))
        st.markdown(
            f'<div class="profile-panel">'
            f'<div class="profile-name">{html.escape(s.get("name", ""))}</div>'
            f'<div class="profile-id">{html.escape(s.get("id", ""))}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Course</span><br>{html.escape(s.get("course", ""))}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Marks</span><br>{s.get("marks", 0)} {grade_chip_html(grade)}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Age</span><br>{s.get("age", 0)}</div>'
            f'<div class="profile-field"><span class="profile-field-label">Email</span><br>{html.escape(s.get("email", ""))}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("✕ Clear", key="clear_qf"):
            st.session_state.quick_find_result = None
            st.rerun()

    st.divider()

    # Endpoints expander
    with st.expander("📡 API Endpoints"):
        endpoints = [
            ("GET", "/student"),
            ("GET", "/student/{id}"),
            ("GET", "/filter?course=X"),
            ("GET", "/sort?sort_by=...&order=..."),
            ("GET", "/paginate?page=N&limit=N"),
            ("POST", "/create"),
            ("PUT", "/update/{id}"),
            ("DELETE", "/delete/{id}"),
        ]
        for m, p in endpoints:
            mc = METHOD_COLORS.get(m, TOK_MUTED)
            st.markdown(
                f'<span class="mono-font" style="font-size:0.78rem;"><span style="color:{mc};font-weight:700;">{m}</span> {html.escape(p)}</span>',
                unsafe_allow_html=True,
            )


# ─── Main Data Load ──────────────────────────────────────────────────────────────
all_students_dict, all_students_list, all_courses, class_avg = load_data()


# ─── Dialogs ─────────────────────────────────────────────────────────────────────
@st.dialog("Add Student", width="large")
def add_student_dialog():
    next_id = get_next_id(all_students_dict)
    existing_ids = set(all_students_dict.keys())

    c1, c2 = st.columns(2)
    with c1:
        new_id = st.text_input("Student ID", value=next_id)
    with c2:
        new_name = st.text_input("Full Name", placeholder="John Doe")

    c3, c4 = st.columns(2)
    with c3:
        new_email = st.text_input("Email", placeholder="john@example.com")
    with c4:
        course_options = list(all_courses) if all_courses else []
        new_course = st.selectbox("Course", options=course_options, index=None, placeholder="Select or type a course", accept_new_options=True)

    c5, c6 = st.columns(2)
    with c5:
        new_age = st.number_input("Age", min_value=1, max_value=100, value=20)
    with c6:
        new_marks = st.slider("Marks", 0, 100, 50)

    # Live grade preview
    grade = compute_grade(new_marks)
    delta = new_marks - class_avg if class_avg > 0 else 0
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
    st.markdown(
        f'<div style="font-family:\'Geist\',sans-serif;font-size:0.9rem;margin:8px 0;">'
        f'Grade preview: {grade_chip_html(grade)} '
        f'<span style="color:{TOK_MUTED};font-size:0.82rem;">({delta_str} vs class avg)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Validation
    errors = {}
    id_taken = False
    if new_id.strip() in existing_ids:
        id_taken = True
        errors["id"] = "ID already taken"

    if not new_id.strip():
        errors["id"] = "ID is required"
    if not new_name.strip():
        errors["name"] = "Name is required"
    if not new_email.strip():
        errors["email"] = "Email is required"
    if not new_course:
        errors["course"] = "Course is required"

    # Show inline errors
    for fld, msg in errors.items():
        st.caption(f"⚠️ **{fld}**: {msg}")

    can_submit = len(errors) == 0

    if st.button("Create Student", type="primary", disabled=not can_submit, width="stretch"):
        body = {
            "id": new_id.strip(),
            "name": new_name.strip(),
            "age": new_age,
            "course": new_course.strip() if new_course else "",
            "marks": new_marks,
            "email": new_email.strip(),
        }
        try:
            result = api("POST", "/create", body)
            st.session_state.toast_msg = f"✅ Student {new_id.strip()} created!"
            load_all_students.clear()
            st.rerun()
        except ApiError as e:
            if e.fields:
                for fld, msg in e.fields.items():
                    st.error(f"**{fld}**: {msg}")
            else:
                st.error(e.message)


@st.dialog("Edit Student", width="large")
def edit_student_dialog(student: dict):
    sid = student["id"]
    original = {k: v for k, v in student.items() if k != "id"}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<span class="mono-font" style="color:{TOK_MUTED};font-size:0.82rem;">Editing {html.escape(sid)}</span>', unsafe_allow_html=True)
    with c2:
        pass

    e_name = st.text_input("Name", value=original.get("name", ""))
    e_email = st.text_input("Email", value=original.get("email", ""))

    course_options = list(all_courses) if all_courses else []
    current_course = original.get("course", "")
    if current_course and current_course not in course_options:
        course_options.insert(0, current_course)
    course_idx = course_options.index(current_course) if current_course in course_options else None
    e_course = st.selectbox("Course", options=course_options, index=course_idx, accept_new_options=True)

    c3, c4 = st.columns(2)
    with c3:
        e_age = st.number_input("Age", min_value=1, max_value=99, value=original.get("age", 20))
    with c4:
        e_marks = st.slider("Marks", 0, 100, original.get("marks", 0))

    # Compute changes
    changes = {}
    if e_name.strip() != original.get("name", ""):
        changes["name"] = e_name.strip()
    if e_email.strip() != original.get("email", ""):
        changes["email"] = e_email.strip()
    if e_course and e_course.strip() != original.get("course", ""):
        changes["course"] = e_course.strip()
    if e_age != original.get("age", 0):
        changes["age"] = e_age
    if e_marks != original.get("marks", 0):
        changes["marks"] = e_marks

    # Show diff
    if changes:
        st.markdown(f'<p style="font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};margin-top:12px;">Changes:</p>', unsafe_allow_html=True)
        for field_name, new_val in changes.items():
            old_val = original.get(field_name, "")
            st.markdown(
                f'<div style="font-family:\'Geist\',sans-serif;font-size:0.88rem;margin:2px 0;">'
                f'<strong>{html.escape(field_name)}</strong>: '
                f'<span class="diff-old">{html.escape(str(old_val))}</span> → '
                f'<span class="diff-new">{html.escape(str(new_val))}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No changes made.")

    if st.button("Save Changes", type="primary", disabled=len(changes) == 0, width="stretch"):
        try:
            result = api("PUT", f"/update/{sid}", changes)
            st.session_state.toast_msg = f"✅ Student {sid} updated!"
            load_all_students.clear()
            st.rerun()
        except ApiError as e:
            if e.fields:
                for fld, msg in e.fields.items():
                    st.error(f"**{fld}**: {msg}")
            else:
                st.error(e.message)


@st.dialog("Delete Student")
def delete_student_dialog(student: dict):
    sid = student["id"]
    name = student.get("name", "Unknown")

    st.markdown(
        f'<p style="font-family:\'Geist\',sans-serif;color:{TOK_INK};">'
        f'Are you sure you want to delete <strong>{html.escape(name)}</strong> ({html.escape(sid)})?</p>',
        unsafe_allow_html=True,
    )
    st.warning("This action cannot be undone.")

    confirm_id = st.text_input("Type the student ID to confirm", placeholder=sid)

    with st.container(key="delete_confirm_container"):
        if st.button(
            "🗑️ Delete Student",
            type="primary",
            disabled=confirm_id.strip() != sid,
            width="stretch",
            key="delete_confirm_btn",
        ):
            try:
                api("DELETE", f"/delete/{sid}")
                st.session_state.toast_msg = f"🗑️ Student {sid} deleted."
                load_all_students.clear()
                st.rerun()
            except ApiError as e:
                st.error(e.message)

    # Style the delete button red
    st.markdown(
        f"""<style>
        [data-testid="stVerticalBlock"]:has(> div[data-testid="element-container"] > div[data-testid="stButton"] > button[kind="primary"][key="delete_confirm_btn"]) button[kind="primary"] {{
            background-color: {TOK_DANGER};
            border-color: {TOK_DANGER};
        }}
        div[key="delete_confirm_container"] button[kind="primary"] {{
            background-color: {TOK_DANGER} !important;
            border-color: {TOK_DANGER} !important;
        }}
        </style>""",
        unsafe_allow_html=True,
    )


# ─── Header ──────────────────────────────────────────────────────────────────────
header_l, header_r = st.columns([4, 1])
with header_l:
    st.markdown(
        f'<div style="font-family:\'Instrument Serif\',serif;font-size:2.8rem;color:{TOK_INK};line-height:1.1;">'
        f'Student <i style="color:{TOK_ACCENT};">Registry</i></div>'
        f'<div style="font-family:\'Geist\',sans-serif;font-size:0.92rem;color:{TOK_MUTED};margin-top:2px;">'
        f'A front desk for your FastAPI student records.</div>',
        unsafe_allow_html=True,
    )
with header_r:
    if st.button("＋ New student", type="primary", disabled=not st.session_state.connected, width="stretch"):
        add_student_dialog()


# ─── Connection Error Banner ─────────────────────────────────────────────────────
if not st.session_state.connected and not all_students_dict:
    st.error("🔌 Can't reach the API. Is `uvicorn main:app --reload` running?")

# ─── Stat Cards ──────────────────────────────────────────────────────────────────
if all_students_list:
    total = len(all_students_list)
    n_courses = len(all_courses)
    avg_m = class_avg
    passing = sum(1 for s in all_students_list if s.get("marks", 0) >= 60)

    # Top scorer
    top = max(all_students_list, key=lambda s: s.get("marks", 0))
    top_name = top.get("name", "N/A")
    top_marks = top.get("marks", 0)
    top_course = top.get("course", "")

    # Grade spread
    grade_counts = {"A+": 0, "A": 0, "B": 0, "C": 0, "F": 0}
    for s in all_students_list:
        g = compute_grade(s.get("marks", 0))
        grade_counts[g] = grade_counts.get(g, 0) + 1

    sc1, sc2, sc3, sc4 = st.columns(4)

    with sc1:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Students</div>'
            f'<div class="stat-value">{total}</div>'
            f'<div class="stat-sub">across {n_courses} course{"s" if n_courses != 1 else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc2:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Class Average</div>'
            f'<div class="stat-value">{avg_m:.1f}</div>'
            f'<div class="stat-sub">{passing} of {total} passing (60+)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc3:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Top Scorer</div>'
            f'<div class="stat-value">{top_marks}</div>'
            f'<div class="stat-sub">{html.escape(top_name)} · {html.escape(top_course)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with sc4:
        # Grade bar
        bar_segments = ""
        legend_parts = []
        for g in ["A+", "A", "B", "C", "F"]:
            cnt = grade_counts[g]
            if cnt > 0:
                pct = (cnt / total) * 100
                bar_segments += f'<div class="grade-bar-segment" style="width:{pct}%%;background:{GRADE_COLORS[g]};"></div>'
            legend_parts.append(f'{grade_chip_html(g)} <span style="font-size:0.78rem;color:{TOK_MUTED};">{cnt}</span>')

        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Grade Spread</div>'
            f'<div class="grade-bar">{bar_segments}</div>'
            f'<div style="margin-top:8px;font-family:\'Geist\',sans-serif;font-size:0.82rem;">'
            f'{" ".join(legend_parts)}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─── Request Line ────────────────────────────────────────────────────────────────
render_request_line()


# ─── Tabs ─────────────────────────────────────────────────────────────────────────
tab_roster, tab_insights, tab_activity = st.tabs(["📋 Roster", "📊 Insights", "📝 Activity"])


# ─── Roster Tab ──────────────────────────────────────────────────────────────────
with tab_roster:
    if not all_students_dict:
        st.markdown(
            f'<div class="empty-state"><div class="empty-icon">📭</div>No students found. Add one to get started!</div>',
            unsafe_allow_html=True,
        )
    else:
        # Controls row
        ctrl1, ctrl2 = st.columns([3, 1])
        with ctrl1:
            search_q = st.text_input("🔍 Search", placeholder="Search by name, email, or ID...", label_visibility="collapsed", key="search_input")
            st.session_state.search_query = search_q
        with ctrl2:
            page_size = st.selectbox("Rows per page", [5, 10, 20, 50], index=[5, 10, 20, 50].index(st.session_state.page_size), label_visibility="collapsed")
            st.session_state.page_size = page_size

        # Course filter
        course_filter = st.pills("Course", options=["All"] + all_courses, default="All", key="course_pills")
        if course_filter == "All":
            st.session_state.course_filter = None
        else:
            st.session_state.course_filter = course_filter

        # Sort controls
        sort_c1, sort_c2, sort_c3 = st.columns([2, 2, 3])
        with sort_c1:
            sort_field = st.segmented_control("Sort by", options=["Marks", "Name", "Age"], default=st.session_state.sort_field, key="sort_field_ctrl")
            st.session_state.sort_field = sort_field
        with sort_c2:
            sort_order = st.segmented_control("Order", options=["↑ Asc", "↓ Desc"], default=st.session_state.sort_order, key="sort_order_ctrl")
            st.session_state.sort_order = sort_order
        with sort_c3:
            marks_range = st.slider("Marks range", 0, 100, st.session_state.marks_range, key="marks_range_slider")
            st.session_state.marks_range = marks_range

        # Reset page on filter changes
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

        # ── Data loading logic ──
        course_sel = st.session_state.course_filter
        sort_sel = st.session_state.sort_field
        order_sel = st.session_state.sort_order
        order_api = "asc" if order_sel == "↑ Asc" else "desc"
        sort_map = {"Marks": "marks", "Name": "name", "Age": "age"}
        page = st.session_state.page
        psize = st.session_state.page_size
        mr = st.session_state.marks_range

        table_data = []
        total_for_pagination = 0
        api_error_msg = None

        try:
            if course_sel:
                # Use GET /filter
                filtered_dict = api("GET", f"/filter?course={requests.utils.quote(course_sel)}")
                table_data = dict_to_list(filtered_dict)

                # Apply local sort if sort field chosen
                if sort_sel:
                    sort_key = sort_map.get(sort_sel, "marks")
                    reverse = order_api == "desc"
                    table_data.sort(key=lambda s: s.get(sort_key, ""), reverse=reverse)

            elif sort_sel:
                # Use GET /sort
                sort_key = sort_map.get(sort_sel, "marks")
                table_data = api("GET", f"/sort?sort_by={sort_key}&order={order_api}")

            else:
                # Use GET /paginate (server-side)
                pass  # handled below
        except ApiError as e:
            api_error_msg = e.message

        # Apply marks range filter
        if course_sel or sort_sel:
            table_data = [s for s in table_data if mr[0] <= s.get("marks", 0) <= mr[1]]

            # Apply search filter (client-side)
            if search_q.strip():
                sq = search_q.strip().lower()
                table_data = [
                    s for s in table_data
                    if sq in s.get("name", "").lower()
                    or sq in s.get("email", "").lower()
                    or sq in s.get("id", "").lower()
                ]

            total_for_pagination = len(table_data)
            total_pages = max(1, math.ceil(total_for_pagination / psize))

            # Adjust page if needed
            if page > total_pages:
                page = total_pages
                st.session_state.page = page

            start_idx = (page - 1) * psize
            end_idx = start_idx + psize
            page_data = table_data[start_idx:end_idx]

        else:
            # Server-side pagination
            try:
                pag_result = api("GET", f"/paginate?page={page}&limit={psize}")
                page_data = pag_result.get("students", [])
                total_for_pagination = pag_result.get("total_students", 0)
                total_pages = max(1, math.ceil(total_for_pagination / psize))

                # Apply marks range filter client-side
                if mr != (0, 100):
                    # Need full data for marks filter, fall back
                    table_data_full = dict_to_list(all_students_dict)
                    table_data_full = [s for s in table_data_full if mr[0] <= s.get("marks", 0) <= mr[1]]
                    if search_q.strip():
                        sq = search_q.strip().lower()
                        table_data_full = [
                            s for s in table_data_full
                            if sq in s.get("name", "").lower()
                            or sq in s.get("email", "").lower()
                            or sq in s.get("id", "").lower()
                        ]
                    total_for_pagination = len(table_data_full)
                    total_pages = max(1, math.ceil(total_for_pagination / psize))
                    if page > total_pages:
                        page = total_pages
                        st.session_state.page = page
                    start_idx = (page - 1) * psize
                    end_idx = start_idx + psize
                    page_data = table_data_full[start_idx:end_idx]
                elif search_q.strip():
                    # Need full data for search, fall back
                    sq = search_q.strip().lower()
                    table_data_full = dict_to_list(all_students_dict)
                    table_data_full = [
                        s for s in table_data_full
                        if sq in s.get("name", "").lower()
                        or sq in s.get("email", "").lower()
                        or sq in s.get("id", "").lower()
                    ]
                    total_for_pagination = len(table_data_full)
                    total_pages = max(1, math.ceil(total_for_pagination / psize))
                    if page > total_pages:
                        page = total_pages
                        st.session_state.page = page
                    start_idx = (page - 1) * psize
                    end_idx = start_idx + psize
                    page_data = table_data_full[start_idx:end_idx]
                else:
                    if page > total_pages:
                        page = total_pages
                        st.session_state.page = page
                        pag_result = api("GET", f"/paginate?page={page}&limit={psize}")
                        page_data = pag_result.get("students", [])

            except ApiError as e:
                api_error_msg = e.message
                page_data = []
                total_pages = 1

        if api_error_msg:
            st.error(api_error_msg)

        # ── Table and Profile Panel ──
        table_col, profile_col = st.columns([3, 2])

        with table_col:
            if page_data:
                import pandas as pd

                # Build dataframe
                df_rows = []
                for s in page_data:
                    grade = compute_grade(s.get("marks", 0))
                    df_rows.append({
                        "ID": s.get("id", ""),
                        "Name": s.get("name", ""),
                        "Course": s.get("course", ""),
                        "Age": s.get("age", 0),
                        "Marks": s.get("marks", 0),
                        "Grade": grade,
                        "Email": s.get("email", ""),
                    })

                df = pd.DataFrame(df_rows)

                # Unique key based on view params to reset selection
                view_key = f"roster_{course_sel}_{sort_sel}_{order_sel}_{page}_{psize}_{search_q}_{mr}"

                column_config = {
                    "Marks": st.column_config.ProgressColumn(
                        "Marks",
                        min_value=0,
                        max_value=100,
                        format="%d",
                    ),
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

                # Pagination controls
                pg_c1, pg_c2, pg_c3 = st.columns([1, 3, 1])
                with pg_c1:
                    if st.button("← Prev", disabled=page <= 1, width="stretch"):
                        st.session_state.page = page - 1
                        st.rerun()
                with pg_c2:
                    start_row = (page - 1) * psize + 1
                    end_row = min(page * psize, total_for_pagination)
                    st.markdown(
                        f'<div style="text-align:center;font-family:\'Geist\',sans-serif;font-size:0.85rem;color:{TOK_MUTED};padding:8px 0;">'
                        f'{start_row}–{end_row} of {total_for_pagination} · page {page} of {total_pages}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with pg_c3:
                    if st.button("Next →", disabled=page >= total_pages, width="stretch"):
                        st.session_state.page = page + 1
                        st.rerun()

                # Selected student
                selected_rows = event.selection.rows if event and event.selection else []
                selected_student = None
                if selected_rows:
                    idx = selected_rows[0]
                    if idx < len(page_data):
                        selected_student = page_data[idx]

            else:
                st.markdown(
                    f'<div class="empty-state"><div class="empty-icon">🔍</div>No students match your filters.</div>',
                    unsafe_allow_html=True,
                )
                selected_student = None

        with profile_col:
            if page_data and selected_student:
                s = selected_student
                s_name = html.escape(s.get("name", ""))
                s_id = html.escape(s.get("id", ""))
                s_marks = s.get("marks", 0)
                s_grade = compute_grade(s_marks)
                s_course = html.escape(s.get("course", ""))
                s_age = s.get("age", 0)
                s_email = html.escape(s.get("email", ""))

                # Rank overall
                sorted_all = sorted(all_students_list, key=lambda x: x.get("marks", 0), reverse=True)
                rank_overall = 1
                for i, stu in enumerate(sorted_all):
                    if stu.get("id") == s.get("id"):
                        rank_overall = i + 1
                        break

                # Rank in course
                course_mates = [x for x in all_students_list if x.get("course") == s.get("course")]
                course_mates_sorted = sorted(course_mates, key=lambda x: x.get("marks", 0), reverse=True)
                rank_course = 1
                for i, stu in enumerate(course_mates_sorted):
                    if stu.get("id") == s.get("id"):
                        rank_course = i + 1
                        break

                # Course avg
                course_avg = 0
                if course_mates:
                    course_avg = sum(x.get("marks", 0) for x in course_mates) / len(course_mates)

                # Marks ring
                pct = s_marks / 100
                deg = pct * 360
                ring_color = GRADE_COLORS.get(s_grade, TOK_ACCENT)

                # vs class average bar
                delta_val = s_marks - class_avg
                delta_str = f"+{delta_val:.1f}" if delta_val >= 0 else f"{delta_val:.1f}"
                delta_color = TOK_ACCENT if delta_val >= 0 else TOK_DANGER

                st.markdown(
                    f'<div class="profile-panel">'
                    f'<div class="profile-name">{s_name}</div>'
                    f'<div class="profile-id">{s_id}</div>'
                    f'<div class="marks-ring" style="background:conic-gradient({ring_color} {deg}deg, {TOK_LINE} {deg}deg);">'
                    f'<div style="width:76px;height:76px;border-radius:50%%;background:{TOK_SURFACE};display:flex;align-items:center;justify-content:center;">'
                    f'<span class="marks-value">{s_marks}</span></div></div>'
                    f'<div style="text-align:center;margin:6px 0;">{grade_chip_html(s_grade)}</div>'
                    f'<div style="text-align:center;font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};">'
                    f'Rank #{rank_overall} overall · #{rank_course} in {s_course}</div>'
                    f'<hr style="border-color:{TOK_LINE};margin:14px 0;">'
                    f'<div class="profile-field"><span class="profile-field-label">Course</span><br>'
                    f'{course_dot_html(s.get("course", ""), all_courses)}{s_course}</div>'
                    f'<div class="profile-field"><span class="profile-field-label">Age</span><br>{s_age}</div>'
                    f'<div class="profile-field"><span class="profile-field-label">Email</span><br>{s_email}</div>'
                    f'<hr style="border-color:{TOK_LINE};margin:14px 0;">'
                    f'<div style="font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};margin-bottom:4px;">vs Class Average</div>'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'<div style="flex:1;height:8px;background:{TOK_LINE};border-radius:4px;position:relative;">'
                    f'<div style="height:100%%;width:{min(s_marks, 100)}%%;background:{ring_color};border-radius:4px;"></div>'
                    f'<div style="position:absolute;top:-4px;left:{min(class_avg, 100)}%%;width:2px;height:16px;background:{TOK_MUTED};"></div>'
                    f'</div>'
                    f'<span style="font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{delta_color};font-weight:600;">{delta_str}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("✏️ Edit", width="stretch", key="edit_btn"):
                        edit_student_dialog(s)
                with btn_c2:
                    if st.button("🗑️ Delete", width="stretch", key="delete_btn"):
                        delete_student_dialog(s)
            else:
                st.markdown(
                    f'<div class="empty-state" style="margin-top:40px;">'
                    f'<div class="empty-icon">👈</div>'
                    f'<div style="font-family:\'Geist\',sans-serif;color:{TOK_MUTED};">No one selected</div>'
                    f'<div style="font-family:\'Geist\',sans-serif;font-size:0.82rem;color:{TOK_MUTED};margin-top:4px;">'
                    f'Click a row in the table to view their profile.</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ─── Insights Tab ────────────────────────────────────────────────────────────────
with tab_insights:
    if not all_students_list:
        st.info("No student data available for insights.")
    else:
        import altair as alt
        import pandas as pd

        alt_ink = TOK_INK
        alt_muted = TOK_MUTED
        alt_accent = TOK_ACCENT
        alt_bg = "transparent"

        base_config = alt.Chart.configure_view(strokeWidth=0).configure_axis(
            labelColor=alt_muted,
            titleColor=alt_muted,
            gridColor=TOK_LINE,
            domainColor=TOK_LINE,
            tickColor=TOK_LINE,
        ).configure_legend(
            labelColor=alt_muted,
            titleColor=alt_muted,
        ).configure_title(
            color=alt_ink,
        )

        # ── Average Marks by Course ──
        st.markdown(f'<p style="font-family:\'Geist\',sans-serif;font-weight:600;color:{TOK_INK};margin-top:16px;">Average Marks by Course</p>', unsafe_allow_html=True)

        course_avgs = []
        for c in all_courses:
            mates = [s for s in all_students_list if s.get("course") == c]
            if mates:
                cavg = sum(s.get("marks", 0) for s in mates) / len(mates)
                course_avgs.append({"Course": c, "Average Marks": round(cavg, 1)})

        if course_avgs:
            df_course = pd.DataFrame(course_avgs)

            bars = alt.Chart(df_course).mark_bar(
                cornerRadiusEnd=4,
                color=alt_accent,
            ).encode(
                x=alt.X("Average Marks:Q", title="Average Marks"),
                y=alt.Y("Course:N", sort="-x", title=""),
                tooltip=["Course", "Average Marks"],
                opacity=alt.condition(
                    alt.selection_point(on="pointerover", fields=["Course"]),
                    alt.value(1),
                    alt.value(0.7),
                ),
            ).add_params(
                alt.selection_point(on="pointerover", fields=["Course"])
            )

            rule = alt.Chart(pd.DataFrame({"avg": [class_avg]})).mark_rule(
                strokeDash=[6, 4],
                color=TOK_DANGER,
                strokeWidth=1.5,
            ).encode(
                x="avg:Q",
                tooltip=[alt.Tooltip("avg:Q", title="Class Average", format=".1f")],
            )

            chart = (bars + rule).properties(height=max(200, len(course_avgs) * 40)).configure_view(strokeWidth=0).configure_axis(
                labelColor=alt_muted, titleColor=alt_muted, gridColor=TOK_LINE, domainColor=TOK_LINE, tickColor=TOK_LINE,
            )
            st.altair_chart(chart, use_container_width=True)

        # ── Grade Distribution ──
        st.markdown(f'<p style="font-family:\'Geist\',sans-serif;font-weight:600;color:{TOK_INK};margin-top:24px;">Grade Distribution</p>', unsafe_allow_html=True)

        grade_data = []
        for g in ["A+", "A", "B", "C", "F"]:
            cnt = sum(1 for s in all_students_list if compute_grade(s.get("marks", 0)) == g)
            grade_data.append({"Grade": g, "Count": cnt, "Color": GRADE_COLORS[g]})

        df_grade = pd.DataFrame(grade_data)

        grade_bars = alt.Chart(df_grade).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Grade:N", sort=["A+", "A", "B", "C", "F"], title="Grade", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Count:Q", title="Count"),
            color=alt.Color("Grade:N", scale=alt.Scale(
                domain=["A+", "A", "B", "C", "F"],
                range=[GRADE_COLORS["A+"], GRADE_COLORS["A"], GRADE_COLORS["B"], GRADE_COLORS["C"], GRADE_COLORS["F"]],
            ), legend=None),
            tooltip=["Grade", "Count"],
        )

        grade_text = grade_bars.mark_text(dy=-10, fontSize=12, color=alt_muted).encode(
            text="Count:Q",
        )

        chart2 = (grade_bars + grade_text).properties(height=280).configure_view(strokeWidth=0).configure_axis(
            labelColor=alt_muted, titleColor=alt_muted, gridColor=TOK_LINE, domainColor=TOK_LINE, tickColor=TOK_LINE,
        )
        st.altair_chart(chart2, use_container_width=True)

        # ── Age vs Marks Scatter ──
        st.markdown(f'<p style="font-family:\'Geist\',sans-serif;font-weight:600;color:{TOK_INK};margin-top:24px;">Age vs Marks</p>', unsafe_allow_html=True)

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

        legend_sel = alt.selection_point(fields=["Course"], bind="legend")

        scatter = alt.Chart(df_scatter).mark_circle(size=80).encode(
            x=alt.X("Age:Q", title="Age", scale=alt.Scale(zero=False)),
            y=alt.Y("Marks:Q", title="Marks", scale=alt.Scale(domain=[0, 105])),
            color=alt.Color("Course:N", scale=alt.Scale(
                domain=all_courses,
                range=COURSE_PALETTE[:len(all_courses)],
            )),
            tooltip=["Name", "Age", "Marks", "Course", "Grade"],
            opacity=alt.condition(legend_sel, alt.value(0.85), alt.value(0.15)),
        ).add_params(legend_sel).interactive()

        pass_line = alt.Chart(pd.DataFrame({"y": [60]})).mark_rule(
            strokeDash=[6, 4],
            color=TOK_DANGER,
            strokeWidth=1.5,
        ).encode(
            y="y:Q",
            tooltip=[alt.Tooltip("y:Q", title="Pass line")],
        )

        chart3 = (scatter + pass_line).properties(height=360).configure_view(strokeWidth=0).configure_axis(
            labelColor=alt_muted, titleColor=alt_muted, gridColor=TOK_LINE, domainColor=TOK_LINE, tickColor=TOK_LINE,
        ).configure_legend(
            labelColor=alt_muted, titleColor=alt_muted,
        )
        st.altair_chart(chart3, use_container_width=True)


# ─── Activity Tab ────────────────────────────────────────────────────────────────
with tab_activity:
    act_c1, act_c2 = st.columns([1, 1])
    with act_c1:
        if st.button("🗑️ Clear log", width="stretch"):
            st.session_state.activity_log = []
            st.rerun()
    with act_c2:
        # Export CSV
        if all_students_list:
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=["id", "name", "age", "course", "marks", "email", "grade"])
            writer.writeheader()
            for s in all_students_list:
                row = {
                    "id": s.get("id", ""),
                    "name": s.get("name", ""),
                    "age": s.get("age", 0),
                    "course": s.get("course", ""),
                    "marks": s.get("marks", 0),
                    "email": s.get("email", ""),
                    "grade": compute_grade(s.get("marks", 0)),
                }
                writer.writerow(row)
            st.download_button("📥 Export CSV", csv_buffer.getvalue(), "students.csv", "text/csv", width="stretch")
        else:
            st.download_button("📥 Export CSV", "", "students.csv", "text/csv", disabled=True, width="stretch")

    log = st.session_state.activity_log
    if not log:
        st.markdown(
            f'<div class="empty-state"><div class="empty-icon">📝</div>No API requests logged yet.</div>',
            unsafe_allow_html=True,
        )
    else:
        import pandas as pd

        log_rows = []
        for entry in log:
            log_rows.append({
                "Time": entry["time"],
                "Method": entry["method"],
                "Path": entry["path"],
                "Status": str(entry["status"]),
                "ms": entry["ms"],
                "OK": "✅" if entry["ok"] else "❌",
            })

        df_log = pd.DataFrame(log_rows)
        st.dataframe(df_log, hide_index=True, width="stretch")

