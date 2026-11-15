/**
 * Student Registry — Vanilla HTML/CSS/JS Frontend
 * No frameworks, no build tools, pure vanilla JavaScript.
 */

// ── Application State ───────────────────────────────────────────
const state = {
  baseUrl: 'http://127.0.0.1:8000',
  allStudents: {},     // raw dictionary from GET /student
  students: [],        // current page list of students
  course: '',          // active course filter
  sortBy: '',          // active sort field ('marks' | 'name' | 'age' | '')
  order: 'asc',        // sort order ('asc' | 'desc')
  search: '',          // client search query
  page: 1,             // 1-based page number
  limit: 10,           // items per page (5, 10, 20, 50)
  total: 0,            // total matching items for current view
  connected: false,    // API reachability status
  drawerOpen: false,   // drawer visibility
  drawerMode: null,    // 'view' | 'create' | 'edit'
  editingStudent: null // student object for view/edit
};

// ── Color Palettes & Constants ──────────────────────────────────
const DOT_COLORS = [
  '#e07b5a', '#d4a843', '#7cb87a', '#5b9bd5',
  '#9b7cb8', '#d47ba0', '#5bbab5', '#b89b5a'
];

const GRADE_COLORS = {
  'A+': '#2d5a4c',
  'A':  '#3d7a5c',
  'B':  '#6b7a2d',
  'C':  '#b8860b',
  'F':  '#b0412d'
};

const GRADE_CLASS_MAP = {
  'A+': 'a-plus',
  'A':  'a',
  'B':  'b',
  'C':  'c',
  'F':  'f'
};

// ── Security Helper: HTML Escaping ──────────────────────────────
/**
 * Escapes unsafe characters before injecting user content into innerHTML.
 */
function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Grade Computation ───────────────────────────────────────────
function computeGrade(marks) {
  const m = Number(marks);
  if (m >= 90) return 'A+';
  if (m >= 80) return 'A';
  if (m >= 70) return 'B';
  if (m >= 60) return 'C';
  return 'F';
}

function gradeChipHTML(grade) {
  const cls = GRADE_CLASS_MAP[grade] || 'f';
  return `<span class="grade-chip ${cls}">${esc(grade)}</span>`;
}

// ── Course Palette Assignment ───────────────────────────────────
function getUniqueSortedCourses() {
  const courses = new Set();
  for (const id in state.allStudents) {
    const c = state.allStudents[id].course;
    if (c) courses.add(c);
  }
  return Array.from(courses).sort((a, b) => a.localeCompare(b));
}

function getCourseDotColor(course) {
  const sorted = getUniqueSortedCourses();
  const idx = sorted.indexOf(course);
  return DOT_COLORS[(idx >= 0 ? idx : 0) % DOT_COLORS.length];
}

// ── Next ID Suggestion ──────────────────────────────────────────
function suggestNextId() {
  let maxNum = 0;
  for (const id in state.allStudents) {
    const match = id.match(/^S(\d+)$/i);
    if (match) {
      const num = parseInt(match[1], 10);
      if (num > maxNum) maxNum = num;
    }
  }
  return `S${String(maxNum + 1).padStart(3, '0')}`;
}

// ── Class Average Calculation ───────────────────────────────────
function getClassAverage() {
  const ids = Object.keys(state.allStudents);
  if (ids.length === 0) return 0;
  const sum = ids.reduce((acc, id) => acc + (state.allStudents[id].marks || 0), 0);
  return sum / ids.length;
}

// ── localStorage Persistence ────────────────────────────────────
function lsGet(key) {
  try { return localStorage.getItem(key); } catch (e) { return null; }
}

function lsSet(key, val) {
  try { localStorage.setItem(key, val); } catch (e) { /* ignore */ }
}

function loadPreferences() {
  const savedUrl = lsGet('sr_baseUrl');
  if (savedUrl) state.baseUrl = savedUrl;

  const savedLimit = lsGet('sr_limit');
  if (savedLimit) state.limit = parseInt(savedLimit, 10) || 10;

  const savedTheme = lsGet('sr_theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateThemeButton();
}

function savePreferences() {
  lsSet('sr_baseUrl', state.baseUrl);
  lsSet('sr_limit', String(state.limit));
  lsSet('sr_theme', document.documentElement.getAttribute('data-theme') || 'light');
}

// ── Custom API Error Class ──────────────────────────────────────
class ApiError extends Error {
  constructor(status, message, fields = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.fields = fields; // { fieldName: errorMsg }
  }
}

// ── Unified HTTP API Helper ─────────────────────────────────────
async function api(method, path, body = null) {
  const cleanBase = state.baseUrl.replace(/\/+$/, '');
  const url = `${cleanBase}${path}`;
  const t0 = performance.now();

  const reqMethodEl = document.getElementById('req-method');
  const reqPathEl = document.getElementById('req-path');
  const reqStatusEl = document.getElementById('req-status');

  const headers = {};
  const options = { method, headers };

  if (body !== null && body !== undefined) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(url, options);
    const elapsed = Math.round(performance.now() - t0);

    // Update Request Line
    if (reqMethodEl) {
      reqMethodEl.textContent = method;
      reqMethodEl.className = `req-method ${method.toLowerCase()}`;
    }
    if (reqPathEl) {
      reqPathEl.textContent = path;
    }
    if (reqStatusEl) {
      reqStatusEl.textContent = `${res.status} · ${elapsed} ms`;
      reqStatusEl.className = res.ok ? 'req-status status-ok' : 'req-status status-err';
    }

    setConnectionStatus(true);

    const text = await res.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (e) {
      data = text;
    }

    if (!res.ok) {
      const fields = {};
      let msg = 'Request failed';

      if (res.status === 422 && data && Array.isArray(data.detail)) {
        // FastAPI 422 format: [{ loc: [..., "fieldName"], msg: "Value error, ..." }]
        data.detail.forEach(err => {
          const field = Array.isArray(err.loc) && err.loc.length > 0
            ? err.loc[err.loc.length - 1]
            : 'general';
          const cleanMsg = (err.msg || '').replace(/^Value error,\s*/i, '');
          fields[field] = cleanMsg;
        });
        msg = Object.values(fields).join('; ');
      } else if (data && typeof data.detail === 'string') {
        msg = data.detail;
      } else if (typeof data === 'string') {
        msg = data;
      }

      throw new ApiError(res.status, msg, fields);
    }

    return data;
  } catch (err) {
    const elapsed = Math.round(performance.now() - t0);

    if (err instanceof ApiError) {
      throw err;
    }

    // Network / timeout error
    if (reqMethodEl) {
      reqMethodEl.textContent = method;
      reqMethodEl.className = `req-method ${method.toLowerCase()}`;
    }
    if (reqPathEl) reqPathEl.textContent = path;
    if (reqStatusEl) {
      reqStatusEl.textContent = `ERR · ${elapsed} ms`;
      reqStatusEl.className = 'req-status status-err';
    }

    setConnectionStatus(false);
    throw new ApiError(
      0,
      "Can't reach the API. Is `uvicorn main:app --reload` running?"
    );
  }
}

// ── Connection Status ───────────────────────────────────────────
function setConnectionStatus(connected) {
  state.connected = connected;
  const dot = document.getElementById('connection-dot');
  const newBtn = document.getElementById('btn-new-student');

  if (dot) {
    dot.className = `connection-dot ${connected ? 'online' : 'offline'}`;
    dot.title = connected ? 'API Connected' : 'API Offline';
  }
  if (newBtn) {
    newBtn.disabled = !connected;
  }
}

// ── Toast Notifications ─────────────────────────────────────────
function showToast(message, type = 'success', statusCode = null) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'error' ? 'error' : ''}`;

  const codePrefix = statusCode ? `<strong>[${statusCode}]</strong> ` : '';
  toast.innerHTML = `${codePrefix}${esc(message)}`;

  container.appendChild(toast);

  // Auto-dismiss after 4 seconds
  setTimeout(() => {
    toast.classList.add('toast-hide');
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 250);
  }, 4000);
}

// ── Theme Management ────────────────────────────────────────────
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  updateThemeButton();
  savePreferences();
}

function updateThemeButton() {
  const btn = document.getElementById('btn-theme');
  if (!btn) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.textContent = isDark ? '☀' : '☽';
  btn.title = isDark ? 'Switch to light theme' : 'Switch to dark theme';
}

// ── Stat Cards Rendering ────────────────────────────────────────
function renderStats() {
  const ids = Object.keys(state.allStudents);
  const total = ids.length;
  const courses = getUniqueSortedCourses();

  // 1. Students count
  const countEl = document.getElementById('stat-students-count');
  const countSubEl = document.getElementById('stat-students-sub');
  if (countEl) countEl.textContent = total;
  if (countSubEl) countSubEl.textContent = `across ${courses.length} course${courses.length !== 1 ? 's' : ''}`;

  if (total === 0) {
    document.getElementById('stat-avg-marks').textContent = '—';
    document.getElementById('stat-avg-sub').textContent = '0 of 0 passing (60+)';
    document.getElementById('stat-top-marks').textContent = '—';
    document.getElementById('stat-top-sub').textContent = '—';
    document.getElementById('stat-grade-bar').innerHTML = '';
    document.getElementById('stat-grade-legend').innerHTML = '';
    return;
  }

  // 2. Class Average
  let sumMarks = 0;
  let passing = 0;
  let topStudent = null;
  const gradeCounts = { 'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'F': 0 };

  ids.forEach(id => {
    const s = state.allStudents[id];
    const m = s.marks || 0;
    sumMarks += m;
    if (m >= 60) passing++;

    if (!topStudent || m > topStudent.marks) {
      topStudent = { id, ...s };
    }

    const g = computeGrade(m);
    gradeCounts[g] = (gradeCounts[g] || 0) + 1;
  });

  const avg = (sumMarks / total).toFixed(1);
  const avgEl = document.getElementById('stat-avg-marks');
  const avgSubEl = document.getElementById('stat-avg-sub');
  if (avgEl) avgEl.textContent = avg;
  if (avgSubEl) avgSubEl.textContent = `${passing} of ${total} passing (60+)`;

  // 3. Top Scorer
  const topMarksEl = document.getElementById('stat-top-marks');
  const topSubEl = document.getElementById('stat-top-sub');
  if (topMarksEl && topStudent) topMarksEl.textContent = topStudent.marks;
  if (topSubEl && topStudent) {
    topSubEl.textContent = `${topStudent.name} · ${topStudent.course}`;
  }

  // 4. Grade Spread Bar & Legend
  const barEl = document.getElementById('stat-grade-bar');
  const legendEl = document.getElementById('stat-grade-legend');
  if (barEl && legendEl) {
    let barHTML = '';
    let legendHTML = '';

    ['A+', 'A', 'B', 'C', 'F'].forEach(grade => {
      const cnt = gradeCounts[grade] || 0;
      const pct = (cnt / total) * 100;
      const color = GRADE_COLORS[grade];

      if (cnt > 0) {
        barHTML += `<div class="grade-bar-segment" style="width:${pct}%;background:${color};" title="${grade}: ${cnt}"></div>`;
      }
      legendHTML += `
        <span class="grade-legend-item">
          <span class="grade-legend-dot" style="background:${color};"></span>
          ${grade} <span class="mono">${cnt}</span>
        </span>
      `;
    });

    barEl.innerHTML = barHTML;
    legendEl.innerHTML = legendHTML;
  }
}

// ── Course Dropdown & Datalist ──────────────────────────────────
function renderCourseOptions() {
  const select = document.getElementById('filter-course');
  const datalist = document.getElementById('course-datalist');
  const courses = getUniqueSortedCourses();

  if (select) {
    const curVal = state.course;
    let html = '<option value="">All Courses</option>';
    courses.forEach(c => {
      const sel = c === curVal ? 'selected' : '';
      html += `<option value="${esc(c)}" ${sel}>${esc(c)}</option>`;
    });
    select.innerHTML = html;
  }

  if (datalist) {
    let dlHtml = '';
    courses.forEach(c => {
      dlHtml += `<option value="${esc(c)}"></option>`;
    });
    datalist.innerHTML = dlHtml;
  }
}

// ── Skeleton Loading ────────────────────────────────────────────
function renderSkeletonTable() {
  const tbody = document.getElementById('students-tbody');
  if (!tbody) return;

  let html = '';
  for (let i = 0; i < 5; i++) {
    html += `
      <tr>
        <td><div class="skeleton-cell" style="width: 45px;"></div></td>
        <td><div class="skeleton-cell" style="width: 140px;"></div></td>
        <td><div class="skeleton-cell" style="width: 90px;"></div></td>
        <td><div class="skeleton-cell" style="width: 30px;"></div></td>
        <td><div class="skeleton-cell" style="width: 110px;"></div></td>
        <td><div class="skeleton-cell" style="width: 45px;"></div></td>
        <td><div class="skeleton-cell" style="width: 160px;"></div></td>
        <td><div class="skeleton-cell" style="width: 40px;"></div></td>
      </tr>
    `;
  }
  tbody.innerHTML = html;
}

// ── Render Students Table ───────────────────────────────────────
function renderTable() {
  const tbody = document.getElementById('students-tbody');
  if (!tbody) return;

  if (state.students.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 40px 20px; color: var(--muted);">
          No students found matching your criteria.
        </td>
      </tr>
    `;
    renderPager();
    return;
  }

  let html = '';
  state.students.forEach(s => {
    const grade = computeGrade(s.marks);
    const dotColor = getCourseDotColor(s.course);
    const marksPct = Math.min(Math.max(s.marks || 0, 0), 100);

    html += `
      <tr class="student-row" data-id="${esc(s.id)}" tabindex="0" role="button" aria-label="View student ${esc(s.name)}">
        <td class="td-id">${esc(s.id)}</td>
        <td class="td-name">${esc(s.name)}</td>
        <td class="td-course">
          <span class="course-dot" style="background-color: ${dotColor};"></span>${esc(s.course)}
        </td>
        <td class="td-age">${esc(s.age)}</td>
        <td class="td-marks">
          <div class="marks-cell">
            <div class="marks-mini-bar">
              <div class="marks-mini-fill" style="width: ${marksPct}%;"></div>
            </div>
            <span class="marks-mini-val">${esc(s.marks)}</span>
          </div>
        </td>
        <td class="td-grade">${gradeChipHTML(grade)}</td>
        <td class="td-email">${esc(s.email)}</td>
        <td class="td-actions">
          <div class="row-actions">
            <button
              type="button"
              class="btn-action action-edit"
              data-id="${esc(s.id)}"
              title="Edit student"
              aria-label="Edit student ${esc(s.name)}"
            >
              ✎
            </button>
            <button
              type="button"
              class="btn-action action-del"
              data-id="${esc(s.id)}"
              title="Delete student"
              aria-label="Delete student ${esc(s.name)}"
            >
              🗑
            </button>
          </div>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
  renderPager();
}

// ── Pager Controls ──────────────────────────────────────────────
function renderPager() {
  const pagerInfo = document.getElementById('pager-info');
  const prevBtn = document.getElementById('btn-prev-page');
  const nextBtn = document.getElementById('btn-next-page');

  const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
  const start = state.total === 0 ? 0 : (state.page - 1) * state.limit + 1;
  const end = Math.min(state.page * state.limit, state.total);

  if (pagerInfo) {
    pagerInfo.textContent = `${start}–${end} of ${state.total} · page ${state.page} of ${totalPages}`;
  }

  if (prevBtn) prevBtn.disabled = state.page <= 1;
  if (nextBtn) nextBtn.disabled = state.page >= totalPages;
}

// ── Local Search & Sort Helpers ─────────────────────────────────
function applyLocalSearch(list) {
  if (!state.search.trim()) return list;
  const q = state.search.trim().toLowerCase();
  return list.filter(s =>
    (s.name && s.name.toLowerCase().includes(q)) ||
    (s.email && s.email.toLowerCase().includes(q)) ||
    (s.id && s.id.toLowerCase().includes(q))
  );
}

function applyLocalSort(list, field, order) {
  if (!field) return list;
  const isDesc = order === 'desc';
  return [...list].sort((a, b) => {
    let va = a[field];
    let vb = b[field];

    if (typeof va === 'string') va = va.toLowerCase();
    if (typeof vb === 'string') vb = vb.toLowerCase();

    if (va < vb) return isDesc ? 1 : -1;
    if (va > vb) return isDesc ? -1 : 1;
    return 0;
  });
}

function dictToList(dict) {
  const res = [];
  for (const id in dict) {
    res.push({ ...dict[id], id });
  }
  return res;
}

// ── Data-Loading Logic ──────────────────────────────────────────
/**
 * 1. Course selected → GET /filter?course=X (dict → list; sort locally if chosen), paginate locally.
 * 2. Sort field chosen (no course) → GET /sort?sort_by=X&order=Y, paginate locally.
 * 3. Neither → GET /paginate (server-side).
 * Always load GET /student for stats, course list, and next-ID suggestions.
 */
async function loadData() {
  renderSkeletonTable();

  try {
    // 1. Fetch complete records for stats, course list, next-ID
    const all = await api('GET', '/student');
    state.allStudents = all;
    renderStats();
    renderCourseOptions();

    let list = [];

    if (state.course) {
      // 1. Course selected -> GET /filter
      const filteredDict = await api('GET', `/filter?course=${encodeURIComponent(state.course)}`);
      list = dictToList(filteredDict);

      // Local sort if sort chosen
      if (state.sortBy) {
        list = applyLocalSort(list, state.sortBy, state.order);
      }

      // Local search
      list = applyLocalSearch(list);
      state.total = list.length;

      // Local pagination
      const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
      if (state.page > totalPages) state.page = totalPages;
      const start = (state.page - 1) * state.limit;
      state.students = list.slice(start, start + state.limit);

    } else if (state.sortBy) {
      // 2. Sort field chosen (no course) -> GET /sort
      list = await api('GET', `/sort?sort_by=${encodeURIComponent(state.sortBy)}&order=${encodeURIComponent(state.order)}`);

      // Local search
      list = applyLocalSearch(list);
      state.total = list.length;

      // Local pagination
      const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
      if (state.page > totalPages) state.page = totalPages;
      const start = (state.page - 1) * state.limit;
      state.students = list.slice(start, start + state.limit);

    } else {
      // 3. Neither -> Server-side pagination via GET /paginate
      if (state.search.trim()) {
        // When client searches without course/sort, filter over allStudents
        let fullList = dictToList(state.allStudents);
        fullList = applyLocalSearch(fullList);
        state.total = fullList.length;

        const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
        if (state.page > totalPages) state.page = totalPages;
        const start = (state.page - 1) * state.limit;
        state.students = fullList.slice(start, start + state.limit);
      } else {
        const pagData = await api('GET', `/paginate?page=${state.page}&limit=${state.limit}`);
        state.total = pagData.total_students || 0;
        state.students = pagData.students || [];
      }
    }

    renderTable();
  } catch (err) {
    showToast(err.message, 'error', err.status || null);
    renderTable();
  }
}

// ── Drawer Management ───────────────────────────────────────────
function openDrawer(mode, student = null) {
  state.drawerOpen = true;
  state.drawerMode = mode;
  state.editingStudent = student ? { ...student } : null;

  const drawer = document.getElementById('drawer');
  const scrim = document.getElementById('drawer-scrim');
  const viewSection = document.getElementById('drawer-view');
  const formSection = document.getElementById('student-form');
  const title = document.getElementById('drawer-title');

  if (drawer) {
    drawer.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
  }
  if (scrim) scrim.classList.add('open');

  if (mode === 'view' && student) {
    if (title) title.textContent = 'Student Profile';
    if (viewSection) viewSection.hidden = false;
    if (formSection) formSection.hidden = true;
    populateViewDrawer(student);
  } else {
    const isEdit = mode === 'edit';
    if (title) title.textContent = isEdit ? 'Edit Student' : 'New Student';
    if (viewSection) viewSection.hidden = true;
    if (formSection) formSection.hidden = false;
    setupFormDrawer(isEdit, student);
  }
}

function closeDrawer() {
  state.drawerOpen = false;
  state.drawerMode = null;
  state.editingStudent = null;

  const drawer = document.getElementById('drawer');
  const scrim = document.getElementById('drawer-scrim');
  if (drawer) {
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
  }
  if (scrim) scrim.classList.remove('open');
}

// ── View Mode: Populate Student Profile ─────────────────────────
function populateViewDrawer(student) {
  const nameEl = document.getElementById('profile-name');
  const idEl = document.getElementById('profile-id');
  const marksValEl = document.getElementById('profile-marks-val');
  const marksRingEl = document.getElementById('profile-marks-ring');
  const gradeChipWrap = document.getElementById('profile-grade-chip');
  const rankEl = document.getElementById('profile-rank');
  const courseEl = document.getElementById('profile-course');
  const ageEl = document.getElementById('profile-age');
  const emailEl = document.getElementById('profile-email');

  const grade = computeGrade(student.marks);
  const ringColor = GRADE_COLORS[grade] || 'var(--accent)';
  const marksDeg = ((student.marks || 0) / 100) * 360;

  if (nameEl) nameEl.textContent = student.name;
  if (idEl) idEl.textContent = student.id;
  if (marksValEl) marksValEl.textContent = student.marks;

  if (marksRingEl) {
    marksRingEl.style.background = `conic-gradient(${ringColor} ${marksDeg}deg, var(--line) ${marksDeg}deg)`;
  }

  if (gradeChipWrap) {
    gradeChipWrap.innerHTML = gradeChipHTML(grade);
  }

  // Calculate ranks
  const allList = dictToList(state.allStudents);
  allList.sort((a, b) => (b.marks || 0) - (a.marks || 0));
  const rankOverall = allList.findIndex(s => s.id === student.id) + 1;

  const courseMates = allList.filter(s => s.course === student.course);
  const rankCourse = courseMates.findIndex(s => s.id === student.id) + 1;

  if (rankEl) {
    rankEl.textContent = `Rank #${rankOverall || 1} overall · #${rankCourse || 1} in ${student.course}`;
  }

  if (courseEl) {
    const dotColor = getCourseDotColor(student.course);
    courseEl.innerHTML = `<span class="course-dot" style="background-color:${dotColor};"></span>${esc(student.course)}`;
  }
  if (ageEl) ageEl.textContent = `${student.age} years old`;
  if (emailEl) emailEl.textContent = student.email;

  // vs Class Average bar
  const classAvg = getClassAverage();
  const delta = (student.marks || 0) - classAvg;
  const deltaFormatted = (delta >= 0 ? '+' : '') + delta.toFixed(1);

  const fillEl = document.getElementById('profile-avg-bar-fill');
  const markerEl = document.getElementById('profile-avg-marker');
  const deltaEl = document.getElementById('profile-avg-delta');

  if (fillEl) fillEl.style.width = `${Math.min(student.marks || 0, 100)}%`;
  if (markerEl) markerEl.style.left = `${Math.min(classAvg, 100)}%`;
  if (deltaEl) {
    deltaEl.textContent = deltaFormatted;
    deltaEl.className = `vs-avg-delta ${delta >= 0 ? 'positive' : 'negative'}`;
  }
}

// ── Form Mode: Setup Create / Edit ──────────────────────────────
function setupFormDrawer(isEdit, student = null) {
  const form = document.getElementById('student-form');
  if (!form) return;

  const idInput = document.getElementById('field-id');
  const nameInput = document.getElementById('field-name');
  const emailInput = document.getElementById('field-email');
  const courseInput = document.getElementById('field-course');
  const ageInput = document.getElementById('field-age');
  const marksInput = document.getElementById('field-marks');
  const submitBtn = document.getElementById('btn-form-submit');

  clearFormErrors();

  if (isEdit && student) {
    idInput.value = student.id;
    idInput.disabled = true;
    nameInput.value = student.name;
    emailInput.value = student.email;
    courseInput.value = student.course;
    ageInput.value = student.age;
    marksInput.value = student.marks;
    submitBtn.textContent = 'Save Changes';
  } else {
    idInput.value = suggestNextId();
    idInput.disabled = false;
    nameInput.value = '';
    emailInput.value = '';
    courseInput.value = '';
    ageInput.value = 20;
    marksInput.value = 50;
    submitBtn.textContent = 'Create Student';
  }

  updateMarksSliderUI();
  validateForm(isEdit);
}

function updateMarksSliderUI() {
  const marksInput = document.getElementById('field-marks');
  const valEl = document.getElementById('field-marks-val');
  const chipEl = document.getElementById('grade-preview-chip');
  const deltaEl = document.getElementById('grade-delta-preview');

  if (!marksInput) return;
  const marks = parseInt(marksInput.value, 10) || 0;

  if (valEl) valEl.textContent = marks;

  const grade = computeGrade(marks);
  if (chipEl) {
    chipEl.className = `grade-chip ${GRADE_CLASS_MAP[grade] || 'f'}`;
    chipEl.textContent = grade;
  }

  if (deltaEl) {
    const avg = getClassAverage();
    if (avg > 0) {
      const delta = marks - avg;
      const str = (delta >= 0 ? '+' : '') + delta.toFixed(1);
      deltaEl.textContent = `(${str} vs avg)`;
    } else {
      deltaEl.textContent = '';
    }
  }
}

function clearFormErrors() {
  ['id', 'name', 'email', 'course', 'age', 'marks'].forEach(f => {
    const el = document.getElementById(`error-${f}`);
    if (el) el.textContent = '';
  });
}

function showFieldErrors(errors) {
  clearFormErrors();
  for (const field in errors) {
    const el = document.getElementById(`error-${field}`);
    if (el) el.textContent = errors[field];
  }
}

// ── Client-side Validation ──────────────────────────────────────
/**
 * Mirrors server rules:
 * Create:
 *   - id: required, S### format
 *   - name: letters & spaces, 2–100 chars
 *   - age: 1–100
 *   - course: 2–100 chars
 *   - marks: 0–100 integer
 *   - email: valid email
 * Edit:
 *   - name: letters & spaces, 2–50 chars
 *   - age: 1–99 (lt=100)
 *   - course: max 50 chars
 *   - marks: 0–100
 *   - email: valid email
 */
function validateForm(isEdit) {
  const id = (document.getElementById('field-id').value || '').trim();
  const name = (document.getElementById('field-name').value || '').trim();
  const email = (document.getElementById('field-email').value || '').trim();
  const course = (document.getElementById('field-course').value || '').trim();
  const age = parseInt(document.getElementById('field-age').value, 10);
  const marks = parseInt(document.getElementById('field-marks').value, 10);

  const errors = {};

  // ID validation (only on create)
  if (!isEdit) {
    if (!id) {
      errors.id = 'ID is required';
    } else if (!/^S\d+$/i.test(id)) {
      errors.id = 'ID must start with S followed by numbers (e.g. S001)';
    } else if (state.allStudents[id]) {
      errors.id = 'Student with this ID already exists';
    }
  }

  // Name validation
  if (!name) {
    errors.name = 'Name is required';
  } else if (!/^[A-Za-z\s]+$/.test(name)) {
    errors.name = 'Name must contain only alphabets and spaces';
  } else if (isEdit) {
    if (name.length < 2 || name.length > 50) errors.name = 'Name must be 2–50 characters';
  } else {
    if (name.length < 2 || name.length > 100) errors.name = 'Name must be 2–100 characters';
  }

  // Age validation
  if (isNaN(age)) {
    errors.age = 'Age is required';
  } else if (isEdit) {
    if (age <= 0 || age >= 100) errors.age = 'Age must be between 1 and 99';
  } else {
    if (age <= 0 || age > 100) errors.age = 'Age must be between 1 and 100';
  }

  // Course validation
  if (!course) {
    errors.course = 'Course is required';
  } else if (isEdit) {
    if (course.length > 50) errors.course = 'Course cannot exceed 50 characters';
  } else {
    if (course.length < 2 || course.length > 100) errors.course = 'Course must be 2–100 characters';
  }

  // Marks validation
  if (isNaN(marks) || marks < 0 || marks > 100) {
    errors.marks = 'Marks must be an integer between 0 and 100';
  }

  // Email validation
  if (!email) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = 'Please enter a valid email address';
  }

  showFieldErrors(errors);

  const submitBtn = document.getElementById('btn-form-submit');
  if (submitBtn) {
    submitBtn.disabled = Object.keys(errors).length > 0;
  }

  return errors;
}

// ── Submit Create ───────────────────────────────────────────────
async function handleCreateSubmit() {
  const btn = document.getElementById('btn-form-submit');
  btn.disabled = true;

  const id = document.getElementById('field-id').value.trim();
  const name = document.getElementById('field-name').value.trim();
  const email = document.getElementById('field-email').value.trim();
  const course = document.getElementById('field-course').value.trim();
  const age = parseInt(document.getElementById('field-age').value, 10);
  const marks = parseInt(document.getElementById('field-marks').value, 10);

  const payload = { id, name, email, course, age, marks };

  try {
    const res = await api('POST', '/create', payload);
    showToast(`Student ${id} created successfully!`, 'success');
    closeDrawer();
    await loadData();
  } catch (err) {
    if (err.status === 422 && Object.keys(err.fields).length > 0) {
      showFieldErrors(err.fields);
    } else if (err.status === 400) {
      showFieldErrors({ id: err.message });
    } else {
      showToast(err.message, 'error', err.status || null);
    }
    btn.disabled = false;
  }
}

// ── Submit Edit (Partial Update) ────────────────────────────────
async function handleEditSubmit() {
  const btn = document.getElementById('btn-form-submit');
  const orig = state.editingStudent;
  if (!orig) return;

  const name = document.getElementById('field-name').value.trim();
  const email = document.getElementById('field-email').value.trim();
  const course = document.getElementById('field-course').value.trim();
  const age = parseInt(document.getElementById('field-age').value, 10);
  const marks = parseInt(document.getElementById('field-marks').value, 10);

  // Send only changed fields
  const changed = {};
  if (name !== orig.name) changed.name = name;
  if (email !== orig.email) changed.email = email;
  if (course !== orig.course) changed.course = course;
  if (age !== orig.age) changed.age = age;
  if (marks !== orig.marks) changed.marks = marks;

  if (Object.keys(changed).length === 0) {
    showToast('Nothing changed', 'success');
    return;
  }

  btn.disabled = true;

  try {
    await api('PUT', `/update/${orig.id}`, changed);
    showToast(`Student ${orig.id} updated successfully!`, 'success');
    closeDrawer();
    await loadData();
  } catch (err) {
    if (err.status === 422 && Object.keys(err.fields).length > 0) {
      showFieldErrors(err.fields);
    } else {
      showToast(err.message, 'error', err.status || null);
    }
    btn.disabled = false;
  }
}

// ── Delete Confirmation Modal Flow ──────────────────────────────
function openDeleteModal(student) {
  const dialog = document.getElementById('delete-dialog');
  if (!dialog) return;

  const nameEl = document.getElementById('delete-student-name');
  const expectedIdEl = document.getElementById('delete-expected-id');
  const confirmInput = document.getElementById('delete-confirm-input');
  const confirmBtn = document.getElementById('btn-delete-confirm');

  if (nameEl) nameEl.textContent = student.name;
  if (expectedIdEl) expectedIdEl.textContent = student.id;
  if (confirmInput) {
    confirmInput.value = '';
    confirmInput.placeholder = student.id;
  }
  if (confirmBtn) confirmBtn.disabled = true;

  dialog.dataset.studentId = student.id;
  dialog.showModal();

  if (confirmInput) {
    confirmInput.focus();
    confirmInput.oninput = () => {
      confirmBtn.disabled = confirmInput.value.trim() !== student.id;
    };
  }
}

async function handleConfirmDelete() {
  const dialog = document.getElementById('delete-dialog');
  const sid = dialog ? dialog.dataset.studentId : null;
  const btn = document.getElementById('btn-delete-confirm');

  if (!sid) return;
  btn.disabled = true;

  try {
    await api('DELETE', `/delete/${sid}`);
    showToast(`Student ${sid} deleted successfully!`, 'success');
    dialog.close();
    closeDrawer();

    // Adjust page if current page becomes empty
    const totalAfter = state.total - 1;
    const maxPage = Math.max(1, Math.ceil(totalAfter / state.limit));
    if (state.page > maxPage) state.page = maxPage;

    await loadData();
  } catch (err) {
    showToast(err.message, 'error', err.status || null);
    btn.disabled = false;
  }
}

// ── Quick Find / Lookup ─────────────────────────────────────────
async function lookupStudentById(id) {
  try {
    // SINGULAR PATH: /student/{id}
    const data = await api('GET', `/student/${encodeURIComponent(id)}`);
    const student = { id, ...data };
    openDrawer('view', student);
  } catch (err) {
    showToast(err.message, 'error', err.status || null);
  }
}

// ── Event Listeners Setup ───────────────────────────────────────
function setupEventListeners() {
  // API URL change
  const urlInput = document.getElementById('api-url-input');
  if (urlInput) {
    urlInput.value = state.baseUrl;
    urlInput.addEventListener('change', () => {
      state.baseUrl = urlInput.value.trim().replace(/\/+$/, '');
      savePreferences();
      state.page = 1;
      loadData();
    });
  }

  // Reconnect button
  const reconnBtn = document.getElementById('btn-reconnect');
  if (reconnBtn) {
    reconnBtn.addEventListener('click', () => loadData());
  }

  // Theme toggle
  const themeBtn = document.getElementById('btn-theme');
  if (themeBtn) {
    themeBtn.addEventListener('click', toggleTheme);
  }

  // New Student button
  const newBtn = document.getElementById('btn-new-student');
  if (newBtn) {
    newBtn.addEventListener('click', () => openDrawer('create'));
  }

  // Course Filter
  const courseSel = document.getElementById('filter-course');
  if (courseSel) {
    courseSel.addEventListener('change', () => {
      state.course = courseSel.value;
      state.page = 1;
      loadData();
    });
  }

  // Sort By
  const sortSel = document.getElementById('sort-by');
  if (sortSel) {
    sortSel.addEventListener('change', () => {
      state.sortBy = sortSel.value;
      state.page = 1;
      loadData();
    });
  }

  // Asc / Desc Segmented Buttons
  const ascBtn = document.getElementById('sort-asc');
  const descBtn = document.getElementById('sort-desc');

  if (ascBtn && descBtn) {
    ascBtn.addEventListener('click', () => {
      if (state.order !== 'asc') {
        state.order = 'asc';
        ascBtn.classList.add('active');
        descBtn.classList.remove('active');
        ascBtn.setAttribute('aria-checked', 'true');
        descBtn.setAttribute('aria-checked', 'false');
        state.page = 1;
        loadData();
      }
    });

    descBtn.addEventListener('click', () => {
      if (state.order !== 'desc') {
        state.order = 'desc';
        descBtn.classList.add('active');
        ascBtn.classList.remove('active');
        descBtn.setAttribute('aria-checked', 'true');
        ascBtn.setAttribute('aria-checked', 'false');
        state.page = 1;
        loadData();
      }
    });
  }

  // Search input with debounce
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    let debounceTimer = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.search = searchInput.value;
        state.page = 1;
        loadData();
      }, 250);
    });

    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = searchInput.value.trim();
        // If it looks like an exact ID (e.g. S001), open it directly
        if (/^S\d+$/i.test(q)) {
          lookupStudentById(q);
        }
      }
    });
  }

  // Page size selector
  const limitSel = document.getElementById('page-size-select');
  if (limitSel) {
    limitSel.value = String(state.limit);
    limitSel.addEventListener('change', () => {
      state.limit = parseInt(limitSel.value, 10) || 10;
      state.page = 1;
      savePreferences();
      loadData();
    });
  }

  // Pager buttons
  const prevBtn = document.getElementById('btn-prev-page');
  const nextBtn = document.getElementById('btn-next-page');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.page > 1) {
        state.page--;
        loadData();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      const totalPages = Math.max(1, Math.ceil(state.total / state.limit));
      if (state.page < totalPages) {
        state.page++;
        loadData();
      }
    });
  }

  // Table row click & keyboard delegation
  const tbody = document.getElementById('students-tbody');
  if (tbody) {
    tbody.addEventListener('click', (e) => {
      // Edit button clicked
      const editBtn = e.target.closest('.action-edit');
      if (editBtn) {
        e.stopPropagation();
        const sid = editBtn.dataset.id;
        const student = state.allStudents[sid]
          ? { ...state.allStudents[sid], id: sid }
          : state.students.find(s => s.id === sid);
        if (student) openDrawer('edit', student);
        return;
      }

      // Delete button clicked
      const delBtn = e.target.closest('.action-del');
      if (delBtn) {
        e.stopPropagation();
        const sid = delBtn.dataset.id;
        const student = state.allStudents[sid]
          ? { ...state.allStudents[sid], id: sid }
          : state.students.find(s => s.id === sid);
        if (student) openDeleteModal(student);
        return;
      }

      // Row clicked -> open profile view
      const row = e.target.closest('.student-row');
      if (row) {
        const sid = row.dataset.id;
        const student = state.allStudents[sid]
          ? { ...state.allStudents[sid], id: sid }
          : state.students.find(s => s.id === sid);
        if (student) openDrawer('view', student);
      }
    });

    tbody.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const row = e.target.closest('.student-row');
        if (row) {
          const sid = row.dataset.id;
          const student = state.allStudents[sid]
            ? { ...state.allStudents[sid], id: sid }
            : state.students.find(s => s.id === sid);
          if (student) openDrawer('view', student);
        }
      }
    });
  }

  // Drawer Profile Actions
  const drawerEditBtn = document.getElementById('btn-profile-edit');
  const drawerDelBtn = document.getElementById('btn-profile-delete');
  const drawerCloseBtn = document.getElementById('btn-drawer-close');
  const drawerScrim = document.getElementById('drawer-scrim');

  if (drawerEditBtn) {
    drawerEditBtn.addEventListener('click', () => {
      if (state.editingStudent) {
        openDrawer('edit', state.editingStudent);
      }
    });
  }

  if (drawerDelBtn) {
    drawerDelBtn.addEventListener('click', () => {
      if (state.editingStudent) {
        openDeleteModal(state.editingStudent);
      }
    });
  }

  if (drawerCloseBtn) drawerCloseBtn.addEventListener('click', closeDrawer);
  if (drawerScrim) drawerScrim.addEventListener('click', closeDrawer);

  // Global Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state.drawerOpen) {
      closeDrawer();
    }
  });

  // Drawer Form Events
  const form = document.getElementById('student-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const isEdit = state.drawerMode === 'edit';
      const errors = validateForm(isEdit);
      if (Object.keys(errors).length > 0) return;

      if (isEdit) {
        handleEditSubmit();
      } else {
        handleCreateSubmit();
      }
    });

    // Real-time live validation on input
    form.querySelectorAll('input').forEach(inp => {
      inp.addEventListener('input', () => {
        validateForm(state.drawerMode === 'edit');
      });
    });

    // Range slider live UI update
    const marksSlider = document.getElementById('field-marks');
    if (marksSlider) {
      marksSlider.addEventListener('input', updateMarksSliderUI);
    }

    const cancelBtn = document.getElementById('btn-form-cancel');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        if (state.drawerMode === 'edit' && state.editingStudent) {
          openDrawer('view', state.editingStudent);
        } else {
          closeDrawer();
        }
      });
    }
  }

  // Delete Dialog buttons
  const delConfirmBtn = document.getElementById('btn-delete-confirm');
  const delCancelBtn = document.getElementById('btn-delete-cancel');

  if (delConfirmBtn) delConfirmBtn.addEventListener('click', handleConfirmDelete);
  if (delCancelBtn) {
    delCancelBtn.addEventListener('click', () => {
      document.getElementById('delete-dialog').close();
    });
  }
}

// ── Application Initialization ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadPreferences();
  setupEventListeners();
  loadData();
});
