import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERVIEWS_DATA = os.path.expanduser("~/interviews-log/backend/data")

# Look for deliverables.json and groups.json in local dir first, then interviews-log
DELIVERABLES_PATH = os.path.join(BASE_DIR, "deliverables.json")
if not os.path.exists(DELIVERABLES_PATH):
    DELIVERABLES_PATH = os.path.join(INTERVIEWS_DATA, "deliverables.json")

GROUPS_PATH = os.path.join(BASE_DIR, "groups.json")
if not os.path.exists(GROUPS_PATH):
    GROUPS_PATH = os.path.join(INTERVIEWS_DATA, "groups.json")

OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

with open(DELIVERABLES_PATH, "r", encoding="utf-8") as f:
    deliv_data = json.load(f)

with open(GROUPS_PATH, "r", encoding="utf-8") as f:
    groups_data = json.load(f)

deliverables_raw = deliv_data.get("deliverables", [])
groups = groups_data.get("groups", [])
updated_at_raw = deliv_data.get("updated_at", "2026-11-19T15:50:00")

# Format updated_at nicely
try:
    dt = datetime.fromisoformat(updated_at_raw.replace("Z", "+00:00"))
    formatted_date = dt.strftime("%d/%m/%Y %H:%M")
except Exception:
    formatted_date = updated_at_raw

# Sort deliverables: students with pending items (< 3) FIRST, then completed students
# Within pending: fewest completed first, then alphabetical by name
# Within completed: alphabetical by name
def student_sort_key(s):
    is_pending = 0 if s.get("completed_count", 0) < 3 else 1
    count = s.get("completed_count", 0)
    name = s.get("student_name", "")
    return (is_pending, count, name)

deliverables = sorted(deliverables_raw, key=student_sort_key)

# Dynamic stats calculations
total_students = len(deliverables)
complete_students = sum(1 for d in deliverables if d.get("completed_count", 0) == 3)
partial_students = sum(1 for d in deliverables if 0 < d.get("completed_count", 0) < 3)
missing_students = sum(1 for d in deliverables if d.get("completed_count", 0) == 0)
pending_total = partial_students + missing_students
complete_pct = round((complete_students / total_students * 100), 1) if total_students > 0 else 0
pending_pct = round((pending_total / total_students * 100), 1) if total_students > 0 else 0

needs_pdf_count = sum(1 for d in deliverables if not d.get("tasks_pdf", {}).get("submitted", False))
needs_demo_count = sum(1 for d in deliverables if not d.get("demo_video", {}).get("submitted", False))
needs_bug_count = sum(1 for d in deliverables if not d.get("bug_video", {}).get("submitted", False))

# Group mapping and stats
group_stats = []
for g in groups:
    gid = g["id"]
    gname = g["name"]
    students_in_g = [d for d in deliverables if d.get("group_id") == gid]
    tot_st = len(students_in_g)
    comp_st = sum(1 for d in students_in_g if d.get("completed_count", 0) == 3)
    exp_items = tot_st * 3
    sub_items = sum(d.get("completed_count", 0) for d in students_in_g)
    pct = round((sub_items / exp_items * 100), 1) if exp_items > 0 else 0
    has_pending = comp_st < tot_st

    # Sort students inside group with pending first
    sorted_group_students = sorted(students_in_g, key=student_sort_key)

    group_stats.append({
        "id": gid,
        "name": gname,
        "students": sorted_group_students,
        "total_students": tot_st,
        "complete_students": comp_st,
        "has_pending": has_pending,
        "expected_items": exp_items,
        "submitted_items": sub_items,
        "percentage": pct
    })

# Sort groups: groups with pending members first, then alphabetically
group_stats_sorted = sorted(group_stats, key=lambda x: (0 if x["has_pending"] else 1, x["name"]))
complete_groups_count = sum(1 for g in group_stats if not g["has_pending"])
total_groups_count = len(group_stats)

summary = {
    "total_students": total_students,
    "complete": complete_students,
    "partial": partial_students,
    "missing": missing_students,
    "pending_total": pending_total,
    "complete_percentage": complete_pct,
    "pending_percentage": pending_pct,
    "needs_pdf": needs_pdf_count,
    "needs_demo": needs_demo_count,
    "needs_bug": needs_bug_count,
    "complete_groups": complete_groups_count,
    "total_groups": total_groups_count
}

payload_json = json.dumps({
    "updated_at": formatted_date,
    "summary": summary,
    "deliverables": deliverables,
    "groups": group_stats_sorted
}, ensure_ascii=False)

html_template = f"""<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-50">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Control de Entregas Finales | DCP — Universidad Austral</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
  </style>
</head>
<body class="min-h-full flex flex-col text-slate-800 bg-slate-50 antialiased selection:bg-slate-800 selection:text-white">

  <!-- Header -->
  <header class="bg-slate-900 text-white border-b border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <span>Universidad Austral</span>
            <span>•</span>
            <span>Facultad de Ingeniería</span>
            <span>•</span>
            <span class="text-slate-300">DCP / Laboratorio II</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Panel de Entregas Finales
          </h1>
          <p class="text-slate-400 text-xs sm:text-sm mt-1 max-w-2xl">
            Seguimiento de requisitos obligatorios de cursada: PDF de tareas individuales, video de demostración y video de bug.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <div class="bg-slate-800/80 border border-slate-700/80 rounded-xl px-4 py-2 text-right">
            <div class="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Última sincronización</div>
            <div class="text-xs sm:text-sm font-semibold text-slate-200 mt-0.5">
              {formatted_date}
            </div>
          </div>
          <button onclick="copyGeneralReport()" class="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-semibold px-3.5 py-2.5 rounded-xl border border-slate-700 transition active:scale-95 shadow-sm" title="Copiar informe de pendientes">
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
            <span>Copiar Resumen</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">

    <!-- KPI Summary Cards -->
    <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-5 border border-slate-200/90 shadow-sm">
        <div class="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Alumnos</div>
        <div class="text-3xl font-bold text-slate-900 mt-2">{total_students}</div>
        <div class="text-xs text-slate-500 mt-1">16 grupos de desarrollo</div>
      </div>

      <div class="bg-white rounded-xl p-5 border border-slate-200/90 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Completos (3/3)</span>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">{complete_pct}%</span>
        </div>
        <div class="text-3xl font-bold text-emerald-700 mt-2">{complete_students}</div>
        <div class="text-xs text-slate-500 mt-1">Entregas 100% regulares</div>
      </div>

      <div class="bg-white rounded-xl p-5 border border-slate-200/90 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Con Pendientes</span>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">{pending_pct}%</span>
        </div>
        <div class="text-3xl font-bold text-amber-700 mt-2">{pending_total}</div>
        <div class="text-xs text-slate-500 mt-1">{partial_students} parcial(es) • {missing_students} sin entrega</div>
      </div>

      <div class="bg-white rounded-xl p-5 border border-slate-200/90 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Equipos al Día</span>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">{complete_groups_count}/{total_groups_count}</span>
        </div>
        <div class="text-3xl font-bold text-slate-900 mt-2">{complete_groups_count}</div>
        <div class="text-xs text-slate-500 mt-1">Equipos con 100% aprobado</div>
      </div>
    </section>

    <!-- Global Progress Bar -->
    <section class="bg-white rounded-xl p-4 sm:p-5 border border-slate-200/90 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 mb-2.5">
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-600">Progreso General del Curso</span>
        <span class="text-xs font-semibold text-slate-600">
          <strong class="text-emerald-700">{complete_students} al día ({complete_pct}%)</strong> • 
          <strong class="text-amber-700">{pending_total} con pendientes ({pending_pct}%)</strong>
        </span>
      </div>
      <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
        <div style="width: {complete_pct}%" class="bg-emerald-500 transition-all duration-300" title="{complete_students} alumnos al día"></div>
        <div style="width: {pending_pct}%" class="bg-amber-400 transition-all duration-300" title="{pending_total} con entregas pendientes"></div>
      </div>
    </section>

    <!-- Controls, Filter Tabs & Search -->
    <section class="space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-3">
        <!-- View tabs -->
        <div class="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
          <button id="tab-btn-students" onclick="switchView('students')" class="px-3.5 py-1.5 rounded-lg transition bg-white text-slate-900 shadow-sm">
            Vista por Alumno
          </button>
          <button id="tab-btn-groups" onclick="switchView('groups')" class="px-3.5 py-1.5 rounded-lg transition text-slate-600 hover:text-slate-900">
            Vista por Equipo ({total_groups_count})
          </button>
        </div>

        <!-- Search Bar -->
        <div class="relative w-full sm:w-80">
          <input 
            type="text" 
            id="search-input" 
            placeholder="Buscar alumno o grupo..." 
            oninput="applyFilters()"
            class="w-full pl-9 pr-8 py-2 text-xs rounded-xl border border-slate-300 bg-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-800 focus:border-slate-800 transition shadow-sm font-medium"
          />
          <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <button id="clear-search-btn" onclick="clearSearch()" class="hidden absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 text-xs">✕</button>
        </div>
      </div>

      <!-- Filters & Selects -->
      <div class="flex flex-wrap items-center justify-between gap-2 pt-0.5">
        <div class="flex flex-wrap items-center gap-1.5" id="filter-pills-container">
          <button onclick="setFilter('all')" class="filter-pill active px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white shadow-sm" data-filter="all">
            Todos ({total_students})
          </button>
          <button onclick="setFilter('pending')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-amber-800 hover:bg-slate-50" data-filter="pending">
            Con Pendientes ({pending_total})
          </button>
          <button onclick="setFilter('complete')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="complete">
            Completos ({complete_students})
          </button>
          <span class="text-slate-300 font-light mx-1">|</span>
          <button onclick="setFilter('needs-pdf')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-pdf">
            Debe PDF ({needs_pdf_count})
          </button>
          <button onclick="setFilter('needs-demo')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-demo">
            Debe Demo ({needs_demo_count})
          </button>
          <button onclick="setFilter('needs-bug')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-bug">
            Debe Bug ({needs_bug_count})
          </button>
        </div>

        <div class="flex items-center gap-2">
          <select id="group-select" onchange="applyFilters()" class="text-xs rounded-xl border border-slate-300 bg-white py-1.5 px-3 text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-800 shadow-sm font-medium">
            <option value="all">Todos los grupos ({total_groups_count})</option>
          </select>
          <button onclick="exportCSV()" class="inline-flex items-center gap-1.5 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold px-3 py-1.5 rounded-xl shadow-sm transition active:scale-95" title="Descargar CSV">
            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>Exportar CSV</span>
          </button>
        </div>
      </div>
    </section>

    <!-- VIEW 1: STUDENTS TABLE -->
    <section id="view-students" class="space-y-3">
      <div class="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider text-[11px]">
              <tr>
                <th class="py-3 px-4">Alumno</th>
                <th class="py-3 px-3">Grupo</th>
                <th class="py-3 px-3 text-center">PDF Tareas</th>
                <th class="py-3 px-3 text-center">Video Demo</th>
                <th class="py-3 px-3 text-center">Video Bug</th>
                <th class="py-3 px-3 text-center">Feedback Líderes</th>
                <th class="py-3 px-4 text-center">Estado</th>
              </tr>
            </thead>
            <tbody id="students-table-body" class="divide-y divide-slate-100 font-medium">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
        <div id="no-results-students" class="hidden py-12 text-center text-slate-400">
          <p class="font-semibold text-sm">No se encontraron alumnos con los criterios seleccionados.</p>
        </div>
      </div>
      <div class="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Los alumnos con entregas pendientes se muestran al principio de la tabla.</span>
        <span id="filtered-count-label">Mostrando {total_students} de {total_students} alumnos</span>
      </div>
    </section>

    <!-- VIEW 2: GROUPS CARDS -->
    <section id="view-groups" class="hidden space-y-4">
      <div id="groups-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Rendered via JS -->
      </div>
      <div id="no-results-groups" class="hidden py-12 text-center text-slate-400 bg-white rounded-xl border border-slate-200">
        <p class="font-semibold text-sm">No se encontraron grupos con los criterios seleccionados.</p>
      </div>
    </section>

  </main>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-xl border border-slate-700 text-xs font-semibold flex items-center gap-2 transform transition-all translate-y-16 opacity-0 pointer-events-none">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span id="toast-msg">Mensaje copiado al portapapeles</span>
  </div>

  <!-- Footer -->
  <footer class="bg-white border-t border-slate-200 mt-auto py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-400 space-y-1">
      <p>Diseño y Construcción de Software • Cátedra de Laboratorio II • Facultad de Ingeniería • Universidad Austral</p>
      <p>Panel informativo actualizado a partir de las entregas formales remitidas al equipo docente.</p>
    </div>
  </footer>

  <!-- Application Logic & Data -->
  <script>
    const APP_DATA = {payload_json};
    let currentFilter = 'all';
    let currentView = 'students';

    // Initialize group dropdown
    const groupSelect = document.getElementById('group-select');
    APP_DATA.groups.forEach(g => {{
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = `${{g.name}} (${{g.complete_students}}/${{g.total_students}} al día)`;
      groupSelect.appendChild(opt);
    }});

    function switchView(view) {{
      currentView = view;
      const tabStudents = document.getElementById('tab-btn-students');
      const tabGroups = document.getElementById('tab-btn-groups');
      const viewStudents = document.getElementById('view-students');
      const viewGroups = document.getElementById('view-groups');

      if (view === 'students') {{
        tabStudents.className = "px-3.5 py-1.5 rounded-lg transition bg-white text-slate-900 shadow-sm";
        tabGroups.className = "px-3.5 py-1.5 rounded-lg transition text-slate-600 hover:text-slate-900";
        viewStudents.classList.remove('hidden');
        viewGroups.classList.add('hidden');
      }} else {{
        tabGroups.className = "px-3.5 py-1.5 rounded-lg transition bg-white text-slate-900 shadow-sm";
        tabStudents.className = "px-3.5 py-1.5 rounded-lg transition text-slate-600 hover:text-slate-900";
        viewStudents.classList.add('hidden');
        viewGroups.classList.remove('hidden');
      }}
      applyFilters();
    }}

    function setFilter(filter) {{
      currentFilter = filter;
      document.querySelectorAll('.filter-pill').forEach(btn => {{
        if (btn.dataset.filter === filter) {{
          btn.className = "filter-pill active px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white shadow-sm";
        }} else {{
          btn.className = "filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50";
        }}
      }});
      applyFilters();
    }}

    function clearSearch() {{
      const input = document.getElementById('search-input');
      input.value = '';
      document.getElementById('clear-search-btn').classList.add('hidden');
      applyFilters();
    }}

    function renderStatusPill(count) {{
      if (count === 3) {{
        return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span> 3/3 Completo
                </span>`;
      }} else if (count > 0) {{
        return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-600"></span> ${{count}}/3 Parcial
                </span>`;
      }} else {{
        return `<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-100 text-rose-800">
                  <span class="w-1.5 h-1.5 rounded-full bg-rose-600"></span> 0/3 Sin Entrega
                </span>`;
      }}
    }}

    function renderItemBadge(item) {{
      if (item && item.submitted) {{
        return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                  <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                  <span>Entregado</span>
                </span>`;
      }} else {{
        return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200/60">
                  <svg class="w-3.5 h-3.5 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  <span>Pendiente</span>
                </span>`;
      }}
    }}

    function applyFilters() {{
      const searchVal = document.getElementById('search-input').value.trim().toLowerCase();
      const clearBtn = document.getElementById('clear-search-btn');
      if (searchVal) {{
        clearBtn.classList.remove('hidden');
      }} else {{
        clearBtn.classList.add('hidden');
      }}

      const selectedGroup = document.getElementById('group-select').value;

      // Filter deliverables
      let filtered = APP_DATA.deliverables.filter(item => {{
        // Group filter
        if (selectedGroup !== 'all' && String(item.group_id) !== String(selectedGroup)) {{
          return false;
        }}

        // Pill filter
        if (currentFilter === 'pending' && item.completed_count === 3) return false;
        if (currentFilter === 'complete' && item.completed_count !== 3) return false;
        if (currentFilter === 'needs-pdf' && item.tasks_pdf.submitted) return false;
        if (currentFilter === 'needs-demo' && item.demo_video.submitted) return false;
        if (currentFilter === 'needs-bug' && item.bug_video.submitted) return false;

        // Search text
        if (searchVal) {{
          const name = (item.student_name || '').toLowerCase();
          const gname = (item.group_name || '').toLowerCase();
          if (!name.includes(searchVal) && !gname.includes(searchVal)) {{
            return false;
          }}
        }}

        return true;
      }});

      // Always sort filtered list: students with pending items (< 3) FIRST
      filtered.sort((a, b) => {{
        const aPending = a.completed_count < 3 ? 0 : 1;
        const bPending = b.completed_count < 3 ? 0 : 1;
        if (aPending !== bPending) return aPending - bPending;
        if (aPending === 0) {{
          if (a.completed_count !== b.completed_count) {{
            return a.completed_count - b.completed_count;
          }}
        }}
        return a.student_name.localeCompare(b.student_name);
      }});

      renderStudentsTable(filtered);
      renderGroupsCards(searchVal, selectedGroup);

      document.getElementById('filtered-count-label').textContent = `Mostrando ${{filtered.length}} de ${{APP_DATA.deliverables.length}} alumnos`;
    }}

    function renderStudentsTable(list) {{
      const tbody = document.getElementById('students-table-body');
      const noResults = document.getElementById('no-results-students');
      tbody.innerHTML = '';

      if (list.length === 0) {{
        noResults.classList.remove('hidden');
        return;
      }}
      noResults.classList.add('hidden');

      list.forEach(s => {{
        const isPending = s.completed_count < 3;
        const tr = document.createElement('tr');
        
        // Highlight pending students cleanly
        if (isPending) {{
          tr.className = "bg-amber-50/40 hover:bg-amber-50/70 border-b border-amber-200/60 transition";
        }} else {{
          tr.className = "hover:bg-slate-50 transition border-b border-slate-100";
        }}

        tr.innerHTML = `
          <td class="py-3 px-4 font-semibold text-slate-900 whitespace-nowrap">
            ${{s.student_name}}
          </td>
          <td class="py-3 px-3 text-slate-600 whitespace-nowrap">
            <span class="inline-block px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-medium">
              ${{s.group_name}}
            </span>
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.tasks_pdf)}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.demo_video)}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.bug_video)}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{s.leader_feedback && s.leader_feedback.submitted ? 
              `<span class="inline-flex items-center gap-1 text-slate-700 text-xs font-medium bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                 <svg class="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                 <span>Recibido</span>
               </span>` : 
              `<span class="text-slate-400 text-xs">—</span>`}}
          </td>
          <td class="py-3 px-4 text-center whitespace-nowrap">
            ${{renderStatusPill(s.completed_count)}}
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function renderGroupsCards(searchVal, selectedGroup) {{
      const container = document.getElementById('groups-grid');
      const noResults = document.getElementById('no-results-groups');
      container.innerHTML = '';

      let groups = APP_DATA.groups;
      if (selectedGroup !== 'all') {{
        groups = groups.filter(g => String(g.id) === String(selectedGroup));
      }}

      if (searchVal) {{
        groups = groups.filter(g => {{
          const matchName = g.name.toLowerCase().includes(searchVal);
          const matchStudent = g.students.some(s => s.student_name.toLowerCase().includes(searchVal));
          return matchName || matchStudent;
        }});
      }}

      if (groups.length === 0) {{
        noResults.classList.remove('hidden');
        return;
      }}
      noResults.classList.add('hidden');

      // Sort groups with pending first
      groups.sort((a, b) => {{
        const aPending = a.has_pending ? 0 : 1;
        const bPending = b.has_pending ? 0 : 1;
        if (aPending !== bPending) return aPending - bPending;
        return a.name.localeCompare(b.name);
      }});

      groups.forEach(g => {{
        const card = document.createElement('div');
        const cardBorder = g.has_pending ? 'border-amber-300/80 bg-amber-50/10' : 'border-slate-200/90 bg-white';
        card.className = `rounded-xl p-5 border ${{cardBorder}} shadow-sm flex flex-col justify-between`;

        let membersHtml = '';
        g.students.forEach(st => {{
          const count = st.completed_count;
          const isPending = count < 3;
          const badgeClass = isPending ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-slate-50 border-slate-200 text-slate-800';

          membersHtml += `
            <div class="p-2.5 rounded-lg border ${{badgeClass}} text-xs space-y-1">
              <div class="flex items-center justify-between font-semibold">
                <span>${{st.student_name}}</span>
                <span class="text-[11px] font-bold ${{isPending ? 'text-amber-700' : 'text-emerald-700'}}">${{count}}/3</span>
              </div>
              <div class="flex items-center gap-2 text-[10px] pt-0.5 text-slate-500 font-medium">
                <span class="${{st.tasks_pdf.submitted ? 'text-emerald-700 font-semibold' : 'text-rose-600 font-semibold'}}">${{st.tasks_pdf.submitted ? '✓' : '✕'}} PDF</span>
                <span>•</span>
                <span class="${{st.demo_video.submitted ? 'text-emerald-700 font-semibold' : 'text-rose-600 font-semibold'}}">${{st.demo_video.submitted ? '✓' : '✕'}} Demo</span>
                <span>•</span>
                <span class="${{st.bug_video.submitted ? 'text-emerald-700 font-semibold' : 'text-rose-600 font-semibold'}}">${{st.bug_video.submitted ? '✓' : '✕'}} Bug</span>
              </div>
            </div>
          `;
        }});

        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-bold text-sm text-slate-900">${{g.name}}</h3>
              <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${{g.percentage === 100 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}}">
                ${{g.percentage}}%
              </span>
            </div>
            <div class="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden mb-3.5">
              <div class="${{g.percentage === 100 ? 'bg-emerald-500' : 'bg-amber-500'}} h-full transition-all" style="width: ${{g.percentage}}%"></div>
            </div>
            <div class="space-y-1.5 mb-3.5">
              ${{membersHtml}}
            </div>
          </div>
          <div class="pt-2.5 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[11px] text-slate-500 font-medium">${{g.complete_students}}/${{g.total_students}} al día</span>
            <button onclick="copyGroupNotice(${{g.id}})" class="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 hover:text-slate-900 transition py-1 px-2 rounded-lg hover:bg-slate-100">
              <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
              <span>Copiar Aviso</span>
            </button>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function showToast(msg) {{
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      toast.classList.remove('translate-y-16', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {{
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-16', 'opacity-0');
      }}, 3000);
    }}

    function copyToClipboard(text, msg) {{
      navigator.clipboard.writeText(text).then(() => {{
        showToast(msg || 'Copiado al portapapeles');
      }}).catch(() => {{
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast(msg || 'Copiado al portapapeles');
      }});
    }}

    function copyGroupNotice(groupId) {{
      const g = APP_DATA.groups.find(x => x.id === groupId);
      if (!g) return;

      let text = `Grupo ${{g.name}} — Estado de Entregas Finales:\\n\\n`;
      g.students.forEach(st => {{
        const missing = [];
        if (!st.tasks_pdf.submitted) missing.push('PDF de Tareas');
        if (!st.demo_video.submitted) missing.push('Video Demo');
        if (!st.bug_video.submitted) missing.push('Video Bug');

        if (missing.length === 0) {{
          text += `• ${{st.student_name}}: 3/3 Completo\\n`;
        }} else {{
          text += `• ${{st.student_name}}: Debe ${{missing.join(', ')}}\\n`;
        }}
      }});

      copyToClipboard(text, `Aviso de ${{g.name}} copiado`);
    }}

    function copyGeneralReport() {{
      let text = `Reporte de Entregas Finales — DCP (${{APP_DATA.updated_at}})\\n\\n`;
      text += `• Alumnos Totales: ${{APP_DATA.summary.total_students}}\\n`;
      text += `• Completos (3/3): ${{APP_DATA.summary.complete}} (${{APP_DATA.summary.complete_percentage}}%)\\n`;
      text += `• Con Pendientes: ${{APP_DATA.summary.pending_total}} (${{APP_DATA.summary.pending_percentage}}%)\\n\\n`;
      text += `Alumnos con entregas pendientes:\\n`;

      APP_DATA.deliverables.filter(d => d.completed_count < 3).forEach(d => {{
        const missing = [];
        if (!d.tasks_pdf.submitted) missing.push('PDF');
        if (!d.demo_video.submitted) missing.push('Demo');
        if (!d.bug_video.submitted) missing.push('Bug');
        text += `- ${{d.student_name}} (${{d.group_name}}): Debe ${{missing.join(' + ')}}\\n`;
      }});

      copyToClipboard(text, 'Reporte copiado al portapapeles');
    }}

    function exportCSV() {{
      const headers = ['Alumno', 'Grupo', 'PDF Tareas', 'Video Demo', 'Video Bug', 'Feedback Lideres', 'Completados', 'Estado'];
      const rows = APP_DATA.deliverables.map(d => [
        `"${{d.student_name}}"`,
        `"${{d.group_name}}"`,
        d.tasks_pdf.submitted ? 'Entregado' : 'Pendiente',
        d.demo_video.submitted ? 'Entregado' : 'Pendiente',
        d.bug_video.submitted ? 'Entregado' : 'Pendiente',
        d.leader_feedback && d.leader_feedback.submitted ? 'Recibido' : 'No',
        d.completed_count,
        d.completed_count === 3 ? 'Completo' : 'Parcial'
      ]);

      const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `entregas_finales_dcp.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast('Descargando archivo CSV...');
    }}

    // Initial render
    applyFilters();
  </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_template)

print("Build complete! Output at:", OUTPUT_HTML)
