/* ============================================================
   Student Registry — Vanilla JS Client
   ============================================================ */

// ── State ────────────────────────────────────────────────────
const state = {
  baseUrl: 'http://127.0.0.1:8000',
  allStudents: {},
  students: [],
  course: '',
  sortBy: '',
  order: 'asc',
  search: '',
  page: 1,
  limit: 10,
  total: 0,
  connected: false,
  drawerOpen: false,
  drawerMode: null,
  editingStudent: null
};

// ── Constants ────────────────────────────────────────────────
const DOT_COLORS = ['#e07b5a','#d4a843','#7cb87a','#5b9bd5','#9b7cb8','#d47ba0','#5bbab5','#b89b5a'];
const GRADE_COLORS = { 'A+': '#2d5a4c', 'A': '#3d7a5c', 'B': '#6b7a2d', 'C': '#b8860b', 'F': '#b0412d' };

// ── Helpers ──────────────────────────────────────────────────
function esc(str) {
  if (str === null || str === undefined) return '';
  var s = String(str);
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function computeGrade(marks) {
  if (marks >= 90) return 'A+';
  if (marks >= 80) return 'A';
  if (marks >= 70) return 'B';
  if (marks >= 60) return 'C';
  return 'F';
}

function getSortedCourses() {
  var courses = [];
  var seen = {};
  for (var id in state.allStudents) {
    var c = state.allStudents[id].course;
    if (c && !seen[c]) { seen[c] = true; courses.push(c); }
  }
  courses.sort(function(a, b) { return a.localeCompare(b); });
  return courses;
}

function courseColor(course) {
  var list = getSortedCourses();
  var idx = list.indexOf(course);
  if (idx === -1) idx = 0;
  return DOT_COLORS[idx % DOT_COLORS.length];
}

function gradeChipHTML(grade) {
  var bg = GRADE_COLORS[grade] || '#666';
  return '<span class="grade-chip" style="background:' + bg + '22;color:' + bg + ';border:1px solid ' + bg + '44">' + esc(grade) + '</span>';
}

function nextId() {
  var max = 0;
  for (var id in state.allStudents) {
    var m = id.match(/^S(\d+)$/);
    if (m) { var n = parseInt(m[1], 10); if (n > max) max = n; }
  }
  var next = max + 1;
  return 'S' + String(next).padStart(3, '0');
}

// ── localStorage ─────────────────────────────────────────────
function lsGet(key) { try { return localStorage.getItem(key); } catch(e) { return null; } }
function lsSet(key, val) { try { localStorage.setItem(key, val); } catch(e) {} }

function loadPrefs() {
  var url = lsGet('sr_baseUrl');
  if (url) state.baseUrl = url;
  var lim = lsGet('sr_limit');
  if (lim) state.limit = parseInt(lim, 10) || 10;
  var theme = lsGet('sr_theme');
  if (theme) {
    document.documentElement.setAttribute('data-theme', theme);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateThemeIcon();
}

function saveBaseUrl() { lsSet('sr_baseUrl', state.baseUrl); }
function saveLimit()   { lsSet('sr_limit', String(state.limit)); }
function saveTheme()   { lsSet('sr_theme', document.documentElement.getAttribute('data-theme') || 'light'); }

// ── ApiError ─────────────────────────────────────────────────
function ApiError(status, message, fields) {
  this.status = status;
  this.message = message;
  this.fields = fields || {};
}
ApiError.prototype = Object.create(Error.prototype);
ApiError.prototype.constructor = ApiError;

// ── api() wrapper ────────────────────────────────────────────
function api(method, path, body) {
  var url = state.baseUrl + path;
  var reqLine = document.getElementById('request-line');
  var opts = { method: method, headers: {} };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  var methodColors = { GET: '#5b9bd5', POST: '#7cb87a', PUT: '#d4a843', DELETE: '#e07b5a' };
  var t0 = performance.now();

  return fetch(url, opts).then(function(resp) {
    var elapsed = Math.round(performance.now() - t0);
    if (reqLine) {
      reqLine.innerHTML = '<span style="color:' + (methodColors[method] || '#ccc') + ';font-weight:700">' + method + '</span> ' +
        esc(path) + ' <span style="opacity:.6">' + resp.status + ' · ' + elapsed + ' ms</span>';
    }
    setConnected(true);

    return resp.text().then(function(text) {
      var data;
      try { data = JSON.parse(text); } catch(e) { data = text; }

      if (!resp.ok) {
        var fields = {};
        var msg = '';
        if (resp.status === 422 && data && Array.isArray(data.detail)) {
          data.detail.forEach(function(err) {
            var field = Array.isArray(err.loc) && err.loc.length > 0 ? err.loc[err.loc.length - 1] : 'general';
            var m = (err.msg || '').replace(/^Value error, /i, '');
            fields[field] = m;
          });
          msg = 'Validation failed';
        } else if (data && typeof data.detail === 'string') {
          msg = data.detail;
        } else {
          msg = 'Request failed (' + resp.status + ')';
        }
        throw new ApiError(resp.status, msg, fields);
      }
      return data;
    });
  }).catch(function(err) {
    if (err instanceof ApiError) throw err;
    var elapsed = Math.round(performance.now() - t0);
    if (reqLine) {
      reqLine.innerHTML = '<span style="color:#e07b5a;font-weight:700">' + method + '</span> ' +
        esc(path) + ' <span style="color:#e07b5a">ERR · ' + elapsed + ' ms</span>';
    }
    setConnected(false);
    throw new ApiError(0, "Can't reach the API. Is `uvicorn main:app --reload` running?", {});
  });
}

// ── Connection ───────────────────────────────────────────────
function setConnected(val) {
  state.connected = val;
  var dot = document.getElementById('conn-dot');
  var text = document.getElementById('conn-text');
  var reconnect = document.getElementById('btn-reconnect');
  var newBtn = document.getElementById('btn-new');
  if (dot) dot.className = 'conn-dot ' + (val ? 'conn-ok' : 'conn-fail');
  if (text) text.textContent = val ? 'Connected' : 'Disconnected';
  if (reconnect) reconnect.style.display = val ? 'none' : 'inline-flex';
  if (newBtn) newBtn.disabled = !val;
}

// ── Toast ────────────────────────────────────────────────────
function toast(message, type, statusCode) {
  var container = document.getElementById('toasts');
  if (!container) return;
  var el = document.createElement('div');
  el.className = 'toast toast-' + (type || 'success');
  var prefix = '';
  if (statusCode) prefix = '<span class="toast-code">' + statusCode + '</span> ';
  el.innerHTML = prefix + esc(message);
  container.appendChild(el);
  requestAnimationFrame(function() { el.classList.add('toast-show'); });
  setTimeout(function() {
    el.classList.remove('toast-show');
    el.classList.add('toast-hide');
    setTimeout(function() { if (el.parentNode) el.parentNode.removeChild(el); }, 350);
  }, 4000);
}

// ── Theme ────────────────────────────────────────────────────
function toggleTheme() {
  var current = document.documentElement.getAttribute('data-theme');
  var next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  updateThemeIcon();
  saveTheme();
}

function updateThemeIcon() {
  var btn = document.getElementById('btn-theme');
  if (!btn) return;
  var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.textContent = isDark ? '☀' : '☽';
}

// ── Stats ────────────────────────────────────────────────────
function renderStats() {
  var container = document.getElementById('stats');
  if (!container) return;

  var ids = Object.keys(state.allStudents);
  var count = ids.length;
  var courses = getSortedCourses();
  var totalMarks = 0;
  var passing = 0;
  var topName = '';
  var topMarks = -1;
  var topCourse = '';
  var grades = { 'A+': 0, 'A': 0, 'B': 0, 'C': 0, 'F': 0 };

  ids.forEach(function(id) {
    var s = state.allStudents[id];
    totalMarks += s.marks;
    if (s.marks >= 60) passing++;
    if (s.marks > topMarks) { topMarks = s.marks; topName = s.name; topCourse = s.course; }
    var g = computeGrade(s.marks);
    grades[g] = (grades[g] || 0) + 1;
  });

  var avg = count ? (totalMarks / count).toFixed(1) : '0';

  // Grade bar segments
  var barParts = '';
  var legendParts = '';
  var gradeOrder = ['A+', 'A', 'B', 'C', 'F'];
  gradeOrder.forEach(function(g) {
    var pct = count ? (grades[g] / count * 100) : 0;
    if (pct > 0) {
      barParts += '<div class="grade-bar-seg" style="width:' + pct + '%;background:' + GRADE_COLORS[g] + '" title="' + g + ': ' + grades[g] + '"></div>';
    }
    legendParts += '<span class="grade-legend-item"><span class="grade-legend-dot" style="background:' + GRADE_COLORS[g] + '"></span>' + g + ' <span class="dim">' + grades[g] + '</span></span>';
  });

  container.innerHTML =
    '<div class="stat-card">' +
      '<div class="stat-value">' + count + '</div>' +
      '<div class="stat-label">Students <span class="dim">across ' + courses.length + ' courses</span></div>' +
    '</div>' +
    '<div class="stat-card">' +
      '<div class="stat-value">' + esc(avg) + '</div>' +
      '<div class="stat-label">Class average <span class="dim">' + passing + ' of ' + count + ' passing (≥60)</span></div>' +
    '</div>' +
    '<div class="stat-card">' +
      '<div class="stat-value">' + (count ? esc(String(topMarks)) : '—') + '</div>' +
      '<div class="stat-label">Top scorer <span class="dim">' + esc(topName) + (topCourse ? ' · ' + esc(topCourse) : '') + '</span></div>' +
    '</div>' +
    '<div class="stat-card stat-card-wide">' +
      '<div class="grade-bar">' + barParts + '</div>' +
      '<div class="grade-legend">' + legendParts + '</div>' +
    '</div>';
}

// ── Course filter dropdown ───────────────────────────────────
function renderCourseFilter() {
  var sel = document.getElementById('sel-course');
  if (!sel) return;
  var courses = getSortedCourses();
  var html = '<option value="">All courses</option>';
  courses.forEach(function(c) {
    html += '<option value="' + esc(c) + '"' + (state.course === c ? ' selected' : '') + '>' + esc(c) + '</option>';
  });
  sel.innerHTML = html;
}

// ── Datalist for course input ────────────────────────────────
function renderCourseDatalist() {
  var dl = document.getElementById('courses-list');
  if (!dl) return;
  var courses = getSortedCourses();
  dl.innerHTML = '';
  courses.forEach(function(c) {
    var opt = document.createElement('option');
    opt.value = c;
    dl.appendChild(opt);
  });
}

// ── Skeleton ─────────────────────────────────────────────────
function renderSkeleton() {
  var tbody = document.getElementById('student-tbody');
  if (!tbody) return;
  var html = '';
  for (var i = 0; i < 5; i++) {
    html += '<tr class="skeleton-row">';
    for (var j = 0; j < 8; j++) {
      html += '<td><div class="skeleton-cell"></div></td>';
    }
    html += '</tr>';
  }
  tbody.innerHTML = html;
}

// ── Table ────────────────────────────────────────────────────
function renderTable() {
  var tbody = document.getElementById('student-tbody');
  if (!tbody) return;

  if (state.students.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty-msg">No students found</td></tr>';
    return;
  }

  var html = '';
  state.students.forEach(function(s) {
    var grade = computeGrade(s.marks);
    var cc = courseColor(s.course);
    html += '<tr class="student-row" data-id="' + esc(s.id) + '" tabindex="0">' +
      '<td class="col-id mono">' + esc(s.id) + '</td>' +
      '<td class="col-name">' + esc(s.name) + '</td>' +
      '<td class="col-course"><span class="course-dot" style="background:' + cc + '"></span>' + esc(s.course) + '</td>' +
      '<td class="col-age">' + esc(String(s.age)) + '</td>' +
      '<td class="col-marks"><div class="marks-bar-wrap"><div class="marks-bar" style="width:' + s.marks + '%;background:' + GRADE_COLORS[grade] + '"></div></div><span class="marks-num">' + s.marks + '</span></td>' +
      '<td class="col-grade">' + gradeChipHTML(grade) + '</td>' +
      '<td class="col-email">' + esc(s.email) + '</td>' +
      '<td class="col-actions"><button class="btn-icon btn-edit" data-id="' + esc(s.id) + '" title="Edit">✎</button><button class="btn-icon btn-delete" data-id="' + esc(s.id) + '" title="Delete">🗑</button></td>' +
      '</tr>';
  });
  tbody.innerHTML = html;
}

// ── Pagination ───────────────────────────────────────────────
function renderPagination() {
  var wrap = document.getElementById('pagination');
  if (!wrap) return;
  var totalPages = Math.max(1, Math.ceil(state.total / state.limit));
  var start = (state.page - 1) * state.limit + 1;
  var end = Math.min(state.page * state.limit, state.total);
  if (state.total === 0) { start = 0; end = 0; }

  wrap.innerHTML =
    '<button id="btn-prev" class="btn btn-sm"' + (state.page <= 1 ? ' disabled' : '') + '>← Prev</button>' +
    '<span class="page-info">' + start + '–' + end + ' of ' + state.total + '</span>' +
    '<button id="btn-next" class="btn btn-sm"' + (state.page >= totalPages ? ' disabled' : '') + '>Next →</button>';

  document.getElementById('btn-prev').addEventListener('click', function() {
    if (state.page > 1) { state.page--; loadData(); }
  });
  document.getElementById('btn-next').addEventListener('click', function() {
    if (state.page < totalPages) { state.page++; loadData(); }
  });
}

// ── Search filter (client-side) ──────────────────────────────
function applySearch(list) {
  if (!state.search) return list;
  var q = state.search.toLowerCase();
  return list.filter(function(s) {
    return s.name.toLowerCase().indexOf(q) !== -1 ||
           s.email.toLowerCase().indexOf(q) !== -1 ||
           s.id.toLowerCase().indexOf(q) !== -1;
  });
}

// ── Local pagination ─────────────────────────────────────────
function paginateLocal(list) {
  state.total = list.length;
  var start = (state.page - 1) * state.limit;
  return list.slice(start, start + state.limit);
}

// ── Sort locally ─────────────────────────────────────────────
function sortLocal(list) {
  if (!state.sortBy) return list;
  var key = state.sortBy;
  var asc = state.order === 'asc';
  var copy = list.slice();
  copy.sort(function(a, b) {
    var va = a[key], vb = b[key];
    if (typeof va === 'string') {
      va = va.toLowerCase(); vb = vb.toLowerCase();
    }
    if (va < vb) return asc ? -1 : 1;
    if (va > vb) return asc ? 1 : -1;
    return 0;
  });
  return copy;
}

// ── Dict → list ──────────────────────────────────────────────
function dictToList(dict) {
  var list = [];
  for (var id in dict) {
    var s = Object.assign({}, dict[id], { id: id });
    list.push(s);
  }
  return list;
}

// ── Data Loading ─────────────────────────────────────────────
function loadData() {
  renderSkeleton();

  api('GET', '/student').then(function(all) {
    state.allStudents = all;
    renderStats();
    renderCourseFilter();
    renderCourseDatalist();

    // Determine source
    if (state.course) {
      return api('GET', '/filter?course=' + encodeURIComponent(state.course)).then(function(dict) {
        var list = dictToList(dict);
        if (state.sortBy) list = sortLocal(list);
        return list;
      });
    } else if (state.sortBy) {
      return api('GET', '/sort?sort_by=' + encodeURIComponent(state.sortBy) + '&order=' + encodeURIComponent(state.order)).then(function(list) {
        return list;
      });
    } else {
      return api('GET', '/paginate?page=' + state.page + '&limit=' + state.limit).then(function(data) {
        state.total = data.total_students;
        var list = applySearch(data.students);
        if (list.length !== data.students.length) {
          // when search narrows results, re-paginate locally over all
          return api('GET', '/student').then(function(allDict) {
            var fullList = dictToList(allDict);
            fullList = applySearch(fullList);
            state.students = paginateLocal(fullList);
            renderTable();
            renderPagination();
            return null;
          });
        }
        state.students = list;
        renderTable();
        renderPagination();
        return null;
      });
    }
  }).then(function(list) {
    if (list === null || list === undefined) return;
    // local pagination path (filter / sort)
    list = applySearch(list);
    state.students = paginateLocal(list);
    renderTable();
    renderPagination();
  }).catch(function(err) {
    toast(err.message, 'error', err.status || undefined);
  });
}

// ── Drawer ───────────────────────────────────────────────────
function openDrawer(mode, student) {
  state.drawerOpen = true;
  state.drawerMode = mode;
  state.editingStudent = student || null;

  var drawer = document.getElementById('drawer');
  var scrim = document.getElementById('scrim');
  if (!drawer || !scrim) return;

  drawer.classList.add('open');
  scrim.classList.add('open');

  renderDrawer();
}

function closeDrawer() {
  state.drawerOpen = false;
  state.drawerMode = null;
  state.editingStudent = null;

  var drawer = document.getElementById('drawer');
  var scrim = document.getElementById('scrim');
  if (drawer) drawer.classList.remove('open');
  if (scrim) scrim.classList.remove('open');
}

function renderDrawer() {
  var content = document.getElementById('drawer-content');
  if (!content) return;

  if (state.drawerMode === 'view') {
    renderViewDrawer(content);
  } else if (state.drawerMode === 'create') {
    renderFormDrawer(content, false);
  } else if (state.drawerMode === 'edit') {
    renderFormDrawer(content, true);
  }
}

function renderViewDrawer(container) {
  var s = state.editingStudent;
  if (!s) return;
  var grade = computeGrade(s.marks);
  var cc = courseColor(s.course);
  var pct = s.marks;
  var gradeColor = GRADE_COLORS[grade] || '#666';

  container.innerHTML =
    '<div class="drawer-header">' +
      '<h2 class="drawer-title">' + esc(s.name) + '</h2>' +
      '<span class="mono dim">' + esc(s.id) + '</span>' +
      '<button class="btn-icon drawer-close" id="drawer-close-btn" title="Close">✕</button>' +
    '</div>' +
    '<div class="drawer-body">' +
      '<div class="marks-ring-wrap">' +
        '<div class="marks-ring" style="background:conic-gradient(' + gradeColor + ' 0% ' + pct + '%, var(--line) ' + pct + '% 100%)">' +
          '<div class="marks-ring-inner">' +
            '<span class="marks-ring-value">' + s.marks + '</span>' +
            '<span class="marks-ring-label">marks</span>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="view-grade">' + gradeChipHTML(grade) + '</div>' +
      '<div class="view-details">' +
        '<div class="view-row"><span class="view-label">Course</span><span><span class="course-dot" style="background:' + cc + '"></span>' + esc(s.course) + '</span></div>' +
        '<div class="view-row"><span class="view-label">Age</span><span>' + esc(String(s.age)) + '</span></div>' +
        '<div class="view-row"><span class="view-label">Email</span><span>' + esc(s.email) + '</span></div>' +
      '</div>' +
      '<div class="drawer-actions">' +
        '<button class="btn btn-primary" id="drawer-edit-btn">✎ Edit</button>' +
        '<button class="btn btn-danger" id="drawer-delete-btn">🗑 Delete</button>' +
      '</div>' +
    '</div>';

  document.getElementById('drawer-close-btn').addEventListener('click', closeDrawer);
  document.getElementById('drawer-edit-btn').addEventListener('click', function() {
    openDrawer('edit', s);
  });
  document.getElementById('drawer-delete-btn').addEventListener('click', function() {
    openDeleteDialog(s);
  });
}

function renderFormDrawer(container, isEdit) {
  var s = isEdit ? state.editingStudent : null;
  var idVal = isEdit ? s.id : nextId();
  var nameVal = s ? s.name : '';
  var emailVal = s ? s.email : '';
  var courseVal = s ? s.course : '';
  var ageVal = s ? s.age : 18;
  var marksVal = s ? s.marks : 50;
  var grade = computeGrade(marksVal);

  container.innerHTML =
    '<div class="drawer-header">' +
      '<h2 class="drawer-title">' + (isEdit ? 'Edit Student' : 'New Student') + '</h2>' +
      '<button class="btn-icon drawer-close" id="drawer-close-btn" title="Close">✕</button>' +
    '</div>' +
    '<div class="drawer-body">' +
      '<form id="student-form" autocomplete="off">' +
        '<div class="field">' +
          '<label for="f-id">Student ID</label>' +
          '<input id="f-id" name="id" type="text" value="' + esc(idVal) + '"' + (isEdit ? ' disabled' : '') + ' />' +
          '<div class="field-error" id="err-id"></div>' +
        '</div>' +
        '<div class="field">' +
          '<label for="f-name">Name</label>' +
          '<input id="f-name" name="name" type="text" value="' + esc(nameVal) + '" />' +
          '<div class="field-error" id="err-name"></div>' +
        '</div>' +
        '<div class="field">' +
          '<label for="f-email">Email</label>' +
          '<input id="f-email" name="email" type="email" value="' + esc(emailVal) + '" />' +
          '<div class="field-error" id="err-email"></div>' +
        '</div>' +
        '<div class="field">' +
          '<label for="f-course">Course</label>' +
          '<input id="f-course" name="course" type="text" value="' + esc(courseVal) + '" list="courses-list" />' +
          '<div class="field-error" id="err-course"></div>' +
        '</div>' +
        '<div class="field">' +
          '<label for="f-age">Age</label>' +
          '<input id="f-age" name="age" type="number" value="' + ageVal + '" min="1" max="100" />' +
          '<div class="field-error" id="err-age"></div>' +
        '</div>' +
        '<div class="field">' +
          '<label for="f-marks">Marks <span id="marks-display" class="marks-display">' + marksVal + '</span> ' + gradeChipHTML(grade) + '</label>' +
          '<input id="f-marks" name="marks" type="range" min="0" max="100" value="' + marksVal + '" />' +
          '<div class="field-error" id="err-marks"></div>' +
        '</div>' +
        '<div class="drawer-actions">' +
          '<button type="submit" class="btn btn-primary" id="btn-submit">' + (isEdit ? 'Save Changes' : 'Create Student') + '</button>' +
        '</div>' +
      '</form>' +
    '</div>';

  document.getElementById('drawer-close-btn').addEventListener('click', closeDrawer);

  // Marks slider → live update
  var marksInput = document.getElementById('f-marks');
  marksInput.addEventListener('input', function() {
    var v = parseInt(this.value, 10);
    document.getElementById('marks-display').textContent = v;
    var g = computeGrade(v);
    var label = this.closest('.field').querySelector('label');
    var chip = label.querySelector('.grade-chip');
    if (chip) {
      chip.style.background = (GRADE_COLORS[g] || '#666') + '22';
      chip.style.color = GRADE_COLORS[g] || '#666';
      chip.style.borderColor = (GRADE_COLORS[g] || '#666') + '44';
      chip.textContent = g;
    }
  });

  // Live validation
  var form = document.getElementById('student-form');
  var inputs = form.querySelectorAll('input');
  inputs.forEach(function(inp) {
    inp.addEventListener('input', function() {
      var errs = validate(isEdit);
      showFieldErrors(errs);
      document.getElementById('btn-submit').disabled = Object.keys(errs).length > 0;
    });
  });

  // Initial validation
  var initialErrs = validate(isEdit);
  document.getElementById('btn-submit').disabled = Object.keys(initialErrs).length > 0;

  // Submit
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    var errs = validate(isEdit);
    if (Object.keys(errs).length > 0) { showFieldErrors(errs); return; }

    if (isEdit) {
      submitEdit();
    } else {
      submitCreate();
    }
  });
}

function getFormData() {
  return {
    id: (document.getElementById('f-id').value || '').trim(),
    name: (document.getElementById('f-name').value || '').trim(),
    email: (document.getElementById('f-email').value || '').trim(),
    course: (document.getElementById('f-course').value || '').trim(),
    age: parseInt(document.getElementById('f-age').value, 10) || 0,
    marks: parseInt(document.getElementById('f-marks').value, 10) || 0
  };
}

function validate(isEdit) {
  var d = getFormData();
  var e = {};

  if (!isEdit) {
    if (!d.id) e.id = 'ID is required';
    else if (!/^S\d+$/.test(d.id)) e.id = 'ID must be S followed by digits';
  }

  if (!d.name) e.name = 'Name is required';
  else if (!/^[A-Za-z\s]+$/.test(d.name)) e.name = 'Letters and spaces only';
  else if (isEdit) {
    if (d.name.length < 2 || d.name.length > 50) e.name = 'Must be 2–50 characters';
  } else {
    if (d.name.length < 2 || d.name.length > 100) e.name = 'Must be 2–100 characters';
  }

  if (isNaN(d.age) || d.age < 1) e.age = 'Age is required';
  else if (isEdit) {
    if (d.age < 1 || d.age > 99) e.age = 'Age must be 1–99';
  } else {
    if (d.age < 1 || d.age > 100) e.age = 'Age must be 1–100';
  }

  if (!d.course) e.course = 'Course is required';
  else if (isEdit) {
    if (d.course.length > 50) e.course = 'Max 50 characters';
  } else {
    if (d.course.length < 2 || d.course.length > 100) e.course = 'Must be 2–100 characters';
  }

  if (isNaN(d.marks) || d.marks < 0 || d.marks > 100) e.marks = 'Marks must be 0–100';

  if (!d.email) e.email = 'Email is required';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) e.email = 'Invalid email format';

  return e;
}

function showFieldErrors(errs) {
  ['id', 'name', 'email', 'course', 'age', 'marks'].forEach(function(f) {
    var el = document.getElementById('err-' + f);
    if (el) el.textContent = errs[f] || '';
  });
}

function submitCreate() {
  var d = getFormData();
  var btn = document.getElementById('btn-submit');
  btn.disabled = true;

  api('POST', '/create', d).then(function() {
    toast('Student ' + d.id + ' created', 'success');
    closeDrawer();
    loadData();
  }).catch(function(err) {
    if (err.status === 422 && Object.keys(err.fields).length > 0) {
      showFieldErrors(err.fields);
    } else if (err.status === 400) {
      showFieldErrors({ id: err.message });
    } else {
      toast(err.message, 'error', err.status || undefined);
    }
    btn.disabled = false;
  });
}

function submitEdit() {
  var d = getFormData();
  var s = state.editingStudent;
  var changed = {};
  if (d.name !== s.name) changed.name = d.name;
  if (d.email !== s.email) changed.email = d.email;
  if (d.course !== s.course) changed.course = d.course;
  if (d.age !== s.age) changed.age = d.age;
  if (d.marks !== s.marks) changed.marks = d.marks;

  if (Object.keys(changed).length === 0) {
    toast('Nothing changed', 'success');
    return;
  }

  var btn = document.getElementById('btn-submit');
  btn.disabled = true;

  api('PUT', '/update/' + s.id, changed).then(function() {
    toast('Student ' + s.id + ' updated', 'success');
    closeDrawer();
    loadData();
  }).catch(function(err) {
    if (err.status === 422 && Object.keys(err.fields).length > 0) {
      showFieldErrors(err.fields);
    } else {
      toast(err.message, 'error', err.status || undefined);
    }
    btn.disabled = false;
  });
}

// ── Delete Dialog ────────────────────────────────────────────
function openDeleteDialog(student) {
  var dialog = document.getElementById('delete-dialog');
  if (!dialog) return;

  document.getElementById('del-student-name').textContent = student.name;
  document.getElementById('del-confirm-input').value = '';
  document.getElementById('btn-del-confirm').disabled = true;

  dialog.dataset.studentId = student.id;
  dialog.showModal();

  var input = document.getElementById('del-confirm-input');
  input.focus();
  input.oninput = function() {
    document.getElementById('btn-del-confirm').disabled = input.value.trim() !== student.id;
  };
}

function confirmDelete() {
  var dialog = document.getElementById('delete-dialog');
  var sid = dialog.dataset.studentId;
  var btn = document.getElementById('btn-del-confirm');
  btn.disabled = true;

  api('DELETE', '/delete/' + sid).then(function() {
    toast('Student ' + sid + ' deleted', 'success');
    dialog.close();
    closeDrawer();

    // Check if page will be empty after delete
    var totalAfter = state.total - 1;
    var maxPage = Math.max(1, Math.ceil(totalAfter / state.limit));
    if (state.page > maxPage) state.page = maxPage;

    loadData();
  }).catch(function(err) {
    toast(err.message, 'error', err.status || undefined);
    btn.disabled = false;
  });
}

// ── Event delegation on table ────────────────────────────────
function onTableClick(e) {
  var btn = e.target.closest('.btn-edit');
  if (btn) {
    e.stopPropagation();
    var id = btn.dataset.id;
    var s = Object.assign({}, state.allStudents[id], { id: id });
    openDrawer('edit', s);
    return;
  }

  btn = e.target.closest('.btn-delete');
  if (btn) {
    e.stopPropagation();
    var id2 = btn.dataset.id;
    var s2 = Object.assign({}, state.allStudents[id2], { id: id2 });
    openDeleteDialog(s2);
    return;
  }

  var row = e.target.closest('.student-row');
  if (row) {
    var id3 = row.dataset.id;
    var s3 = Object.assign({}, state.allStudents[id3], { id: id3 });
    openDrawer('view', s3);
  }
}

function onTableKeydown(e) {
  if (e.key === 'Enter') {
    var row = e.target.closest('.student-row');
    if (row) {
      var id = row.dataset.id;
      var s = Object.assign({}, state.allStudents[id], { id: id });
      openDrawer('view', s);
    }
  }
}

// ── Initialisation ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  loadPrefs();

  // Base URL input
  var urlInput = document.getElementById('input-url');
  if (urlInput) {
    urlInput.value = state.baseUrl;
    urlInput.addEventListener('change', function() {
      state.baseUrl = this.value.replace(/\/+$/, '');
      saveBaseUrl();
      loadData();
    });
  }

  // Theme toggle
  var themeBtn = document.getElementById('btn-theme');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // New student
  var newBtn = document.getElementById('btn-new');
  if (newBtn) newBtn.addEventListener('click', function() { openDrawer('create', null); });

  // Course filter
  var selCourse = document.getElementById('sel-course');
  if (selCourse) selCourse.addEventListener('change', function() {
    state.course = this.value;
    state.page = 1;
    loadData();
  });

  // Sort
  var selSort = document.getElementById('sel-sort');
  if (selSort) selSort.addEventListener('change', function() {
    state.sortBy = this.value;
    state.page = 1;
    loadData();
  });

  // Order
  var selOrder = document.getElementById('sel-order');
  if (selOrder) selOrder.addEventListener('change', function() {
    state.order = this.value;
    state.page = 1;
    loadData();
  });

  // Search
  var searchInput = document.getElementById('input-search');
  if (searchInput) searchInput.addEventListener('input', function() {
    state.search = this.value.trim();
    state.page = 1;
    loadData();
  });

  // Limit
  var selLimit = document.getElementById('sel-limit');
  if (selLimit) {
    selLimit.value = String(state.limit);
    selLimit.addEventListener('change', function() {
      state.limit = parseInt(this.value, 10) || 10;
      state.page = 1;
      saveLimit();
      loadData();
    });
  }

  // Table events
  var tbody = document.getElementById('student-tbody');
  if (tbody) {
    tbody.addEventListener('click', onTableClick);
    tbody.addEventListener('keydown', onTableKeydown);
  }

  // Scrim
  var scrim = document.getElementById('scrim');
  if (scrim) scrim.addEventListener('click', closeDrawer);

  // Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && state.drawerOpen) closeDrawer();
  });

  // Reconnect
  var reconnBtn = document.getElementById('btn-reconnect');
  if (reconnBtn) reconnBtn.addEventListener('click', function() { loadData(); });

  // Delete dialog buttons
  var delConfirm = document.getElementById('btn-del-confirm');
  if (delConfirm) delConfirm.addEventListener('click', confirmDelete);
  var delCancel = document.getElementById('btn-del-cancel');
  if (delCancel) delCancel.addEventListener('click', function() {
    document.getElementById('delete-dialog').close();
  });

  // Initial load
  loadData();
});
