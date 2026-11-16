import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERVIEWS_DATA = os.path.expanduser("~/interviews-log/backend/data")
if not os.path.exists(INTERVIEWS_DATA):
    INTERVIEWS_DATA = r"C:\Users\Sebi\projects\interviews-log\backend\data"

DELIVERABLES_PATH = os.path.join(INTERVIEWS_DATA, "deliverables.json")
GROUPS_PATH = os.path.join(INTERVIEWS_DATA, "groups.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

with open(DELIVERABLES_PATH, "r", encoding="utf-8") as f:
    deliv_data = json.load(f)

with open(GROUPS_PATH, "r", encoding="utf-8") as f:
    groups_data = json.load(f)

deliverables = deliv_data.get("deliverables", [])
groups = groups_data.get("groups", [])
summary = deliv_data.get("summary", {})
updated_at = deliv_data.get("updated_at", "2026-11-16")

# Group mapping
group_map = {g["id"]: g["name"] for g in groups}

# Calculate group stats
group_stats = []
for g in groups:
    gid = g["id"]
    gname = g["name"]
    students_in_g = [d for d in deliverables if d["group_id"] == gid]
    total_st = len(students_in_g)
    comp_st = sum(1 for d in students_in_g if d["completed_count"] == 3)
    total_deliverables_expected = total_st * 3
    total_deliverables_submitted = sum(d["completed_count"] for d in students_in_g)
    pct = round((total_deliverables_submitted / total_deliverables_expected * 100), 1) if total_deliverables_expected > 0 else 0
    
    group_stats.append({
        "id": gid,
        "name": gname,
        "students": students_in_g,
        "total_students": total_st,
        "complete_students": comp_st,
        "expected_items": total_deliverables_expected,
        "submitted_items": total_deliverables_submitted,
        "percentage": pct
    })

# Sort group_stats by percentage ascending (those needing attention first) or alphabetically
group_stats_sorted = sorted(group_stats, key=lambda x: (x["percentage"], x["name"]))

payload_json = json.dumps({
    "updated_at": updated_at,
    "summary": summary,
    "deliverables": deliverables,
    "groups": group_stats
}, ensure_ascii=False, indent=2)

html_template = f"""<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-50">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Estado de Entregas Finales | DCP - Universidad Austral</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
          }},
          colors: {{
            austral: {{
              50: '#f0f5fa',
              100: '#e1ecf5',
              600: '#0284c7',
              700: '#0369a1',
              800: '#075985',
              900: '#0c4a6e',
              950: '#082f49',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .badge-sub {{ background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
    .badge-missing {{ background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
    .badge-neutral {{ background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}
  </style>
</head>
<body class="min-h-full flex flex-col text-slate-800 antialiased selection:bg-sky-500 selection:text-white">

  <!-- Header -->
  <header class="bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 text-white shadow-lg border-b border-sky-800/40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <span>Universidad Austral</span>
            <span>•</span>
            <span>Facultad de Ingeniería</span>
            <span>•</span>
            <span class="bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded-full border border-sky-400/30">DCP / Proyectos</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2.5">
            <span>📋</span> Estado de Entregas Finales
          </h1>
          <p class="text-sky-200/80 text-sm mt-1">
            Panel público de seguimiento de requisitos: <strong>PDF de Tareas</strong>, <strong>Video Demo</strong> y <strong>Video Bug</strong>.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <div class="bg-white/10 backdrop-blur-sm border border-white/10 rounded-xl px-4 py-2.5 text-right">
            <div class="text-[11px] uppercase tracking-wider text-sky-300 font-semibold">Última Actualización</div>
            <div class="text-sm font-bold text-white flex items-center gap-1.5 justify-end mt-0.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              {updated_at}
            </div>
          </div>
          <button onclick="copyGeneralReport()" class="inline-flex items-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold px-3.5 py-2.5 rounded-xl shadow-sm transition active:scale-95 border border-sky-400/40" title="Copiar informe para Discord/Slack">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
            <span>Copiar Resumen</span>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">

    <!-- KPI Summary Cards -->
    <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Total Alumnos</span>
          <span class="w-8 h-8 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center text-sm font-bold">👥</span>
        </div>
        <div class="text-3xl font-extrabold text-slate-900 mt-2">38</div>
        <div class="text-xs text-slate-500 mt-1">En 16 grupos de desarrollo</div>
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-slate-300"></div>
      </div>

      <div class="bg-white rounded-2xl p-5 border border-emerald-200 shadow-sm relative overflow-hidden bg-gradient-to-br from-white to-emerald-50/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-700">Completos (3/3)</span>
          <span class="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center text-sm font-bold">✅</span>
        </div>
        <div class="text-3xl font-extrabold text-emerald-700 mt-2">10</div>
        <div class="text-xs text-emerald-600 mt-1 font-medium">26.3% del total (listos)</div>
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
      </div>

      <div class="bg-white rounded-2xl p-5 border border-amber-200 shadow-sm relative overflow-hidden bg-gradient-to-br from-white to-amber-50/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-amber-700">Parciales (1 o 2)</span>
          <span class="w-8 h-8 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center text-sm font-bold">⚠️</span>
        </div>
        <div class="text-3xl font-extrabold text-amber-700 mt-2">16</div>
        <div class="text-xs text-amber-600 mt-1 font-medium">5 con 2/3 • 11 con 1/3</div>
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-amber-500"></div>
      </div>

      <div class="bg-white rounded-2xl p-5 border border-rose-200 shadow-sm relative overflow-hidden bg-gradient-to-br from-white to-rose-50/40">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-rose-700">Sin Entregar (0/3)</span>
          <span class="w-8 h-8 rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center text-sm font-bold">❌</span>
        </div>
        <div class="text-3xl font-extrabold text-rose-700 mt-2">12</div>
        <div class="text-xs text-rose-600 mt-1 font-medium">31.6% sin entregas finales</div>
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-rose-500"></div>
      </div>
    </section>

    <!-- Global Progress Bar -->
    <section class="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-600">Progreso General del Curso</span>
        <span class="text-xs font-semibold text-slate-500">
          <strong class="text-emerald-600">10 completados</strong> / 
          <strong class="text-amber-600">16 parciales</strong> / 
          <strong class="text-rose-600">12 pendientes</strong> (38 alumnos)
        </span>
      </div>
      <div class="w-full bg-slate-100 h-3.5 rounded-full overflow-hidden flex shadow-inner">
        <div style="width: 26.3%" class="bg-emerald-500 hover:opacity-90 transition" title="10 Completos (26.3%)"></div>
        <div style="width: 13.2%" class="bg-sky-500 hover:opacity-90 transition" title="5 con 2/3 (13.2%)"></div>
        <div style="width: 28.9%" class="bg-amber-400 hover:opacity-90 transition" title="11 con 1/3 (28.9%)"></div>
        <div style="width: 31.6%" class="bg-rose-500 hover:opacity-90 transition" title="12 Sin Entregas (31.6%)"></div>
      </div>
      <div class="flex flex-wrap items-center gap-4 mt-3 text-xs text-slate-500 font-medium">
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> 3/3 Completo (10)</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-500"></span> 2/3 Parcial (5)</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span> 1/3 Parcial (11)</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> 0/3 Sin Entrega (12)</span>
      </div>
    </section>

    <!-- Navigation Views & Filter Controls -->
    <section class="space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-3">
        <!-- Tab selector -->
        <div class="inline-flex bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button id="tab-btn-students" onclick="switchView('students')" class="px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-white text-slate-900 shadow-sm">
            <span>👥</span> Vista por Alumno
          </button>
          <button id="tab-btn-groups" onclick="switchView('groups')" class="px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 text-slate-600 hover:text-slate-900">
            <span>🏷️</span> Vista por Grupo (16)
          </button>
        </div>

        <!-- Search Bar -->
        <div class="relative w-full sm:w-72">
          <input 
            type="text" 
            id="search-input" 
            placeholder="Buscar alumno o grupo..." 
            oninput="applyFilters()"
            class="w-full pl-9 pr-8 py-2 text-xs rounded-xl border border-slate-300 bg-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition shadow-sm"
          />
          <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <button id="clear-search-btn" onclick="clearSearch()" class="hidden absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 text-xs">✕</button>
        </div>
      </div>

      <!-- Filter Pills -->
      <div class="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div class="flex flex-wrap items-center gap-1.5" id="filter-pills-container">
          <button onclick="setFilter('all')" class="filter-pill active px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white shadow-sm" data-filter="all">Todos (38)</button>
          <button onclick="setFilter('complete')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="complete">✅ Completos (10)</button>
          <button onclick="setFilter('partial')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="partial">⚠️ Parciales (16)</button>
          <button onclick="setFilter('missing')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="missing">❌ Sin Entregar (12)</button>
          <span class="text-slate-300 font-light mx-1">|</span>
          <button onclick="setFilter('needs-pdf')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-pdf">📄 Debe PDF (23)</button>
          <button onclick="setFilter('needs-demo')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-demo">🎥 Debe Demo (23)</button>
          <button onclick="setFilter('needs-bug')" class="filter-pill px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50" data-filter="needs-bug">🐞 Debe Bug (12)</button>
        </div>

        <div class="flex items-center gap-2">
          <!-- Group Select Dropdown -->
          <select id="group-select" onchange="applyFilters()" class="text-xs rounded-xl border border-slate-300 bg-white py-1.5 px-3 text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm font-medium">
            <option value="all">Todos los grupos (16)</option>
          </select>
          <button onclick="exportCSV()" class="inline-flex items-center gap-1 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold px-2.5 py-1.5 rounded-xl shadow-sm transition active:scale-95" title="Exportar a CSV">
            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>CSV</span>
          </button>
        </div>
      </div>
    </section>

    <!-- VIEW 1: STUDENTS TABLE -->
    <section id="view-students" class="space-y-3">
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50/80 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[11px]">
              <tr>
                <th class="py-3 px-4">Alumno</th>
                <th class="py-3 px-3">Grupo</th>
                <th class="py-3 px-3 text-center">PDF Tareas</th>
                <th class="py-3 px-3 text-center">Video Demo</th>
                <th class="py-3 px-3 text-center">Video Bug</th>
                <th class="py-3 px-3 text-center">Progreso</th>
                <th class="py-3 px-3 text-center">Feedback 5to</th>
                <th class="py-3 px-4">Detalle / Links</th>
              </tr>
            </thead>
            <tbody id="students-table-body" class="divide-y divide-slate-100 font-medium">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
        <div id="no-results-students" class="hidden py-12 text-center text-slate-400">
          <div class="text-3xl mb-1">🔍</div>
          <p class="font-semibold text-sm">No se encontraron alumnos con los filtros seleccionados.</p>
        </div>
      </div>
      <div class="text-right text-xs text-slate-400" id="filtered-count-label">Mostrando 38 de 38 alumnos</div>
    </section>

    <!-- VIEW 2: GROUPS CARDS -->
    <section id="view-groups" class="hidden space-y-4">
      <div id="groups-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Rendered via JS -->
      </div>
      <div id="no-results-groups" class="hidden py-12 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
        <div class="text-3xl mb-1">🔍</div>
        <p class="font-semibold text-sm">No se encontraron grupos con los filtros seleccionados.</p>
      </div>
    </section>

  </main>

  <!-- Modal Student Detail -->
  <div id="student-modal" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 transform transition-all animate-in fade-in zoom-in-95 duration-150">
      <div class="bg-gradient-to-r from-slate-900 to-sky-950 text-white p-5 flex items-start justify-between">
        <div>
          <span id="modal-group-name" class="text-xs font-semibold uppercase tracking-wider text-sky-300">Grupo</span>
          <h3 id="modal-student-name" class="text-lg font-bold text-white mt-0.5">Nombre del Alumno</h3>
        </div>
        <button onclick="closeModal()" class="text-sky-300 hover:text-white rounded-lg p-1 transition">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="p-6 space-y-4 text-xs">
        <div>
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">Checklist de Requisitos</div>
          <div id="modal-checklist" class="space-y-2"></div>
        </div>

        <div class="bg-slate-50 rounded-xl p-3.5 border border-slate-200">
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">Observaciones / Notas</div>
          <p id="modal-notes" class="text-slate-700 font-medium leading-relaxed"></p>
        </div>

        <div class="flex items-center justify-between pt-2">
          <button onclick="copyStudentNotice()" class="inline-flex items-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold px-4 py-2 rounded-xl transition shadow-sm active:scale-95">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
            <span>Copiar mensaje para este alumno</span>
          </button>
          <button onclick="closeModal()" class="text-slate-500 hover:text-slate-700 font-semibold px-3 py-2">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-xl border border-slate-700 text-xs font-semibold flex items-center gap-2 transform transition-all translate-y-16 opacity-0 pointer-events-none">
    <span id="toast-icon">📋</span>
    <span id="toast-msg">Mensaje copiado al portapapeles</span>
  </div>

  <!-- Footer -->
  <footer class="bg-white border-t border-slate-200 mt-auto py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-400 space-y-1">
      <p>Diseño y Construcción de Programas • Universidad Austral • Facultad de Ingeniería</p>
      <p>Datos extraídos de envíos oficiales recibidos por correo electrónico.</p>
    </div>
  </footer>

  <!-- Application Logic & Embedded Data -->
  <script>
    const APP_DATA = {payload_json};
    let currentFilter = 'all';
    let currentView = 'students';
    let activeModalStudent = null;

    // Initialize group dropdown
    const groupSelect = document.getElementById('group-select');
    APP_DATA.groups.forEach(g => {{
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = `${{g.name}} (${{g.submitted_items}}/${{g.expected_items}})`;
      groupSelect.appendChild(opt);
    }});

    function switchView(view) {{
      currentView = view;
      const tabStudents = document.getElementById('tab-btn-students');
      const tabGroups = document.getElementById('tab-btn-groups');
      const viewStudents = document.getElementById('view-students');
      const viewGroups = document.getElementById('view-groups');

      if (view === 'students') {{
        tabStudents.className = "px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-white text-slate-900 shadow-sm";
        tabGroups.className = "px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 text-slate-600 hover:text-slate-900";
        viewStudents.classList.remove('hidden');
        viewGroups.classList.add('hidden');
      }} else {{
        tabGroups.className = "px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-white text-slate-900 shadow-sm";
        tabStudents.className = "px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 text-slate-600 hover:text-slate-900";
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

    function renderStatusPill(status, count) {{
      if (count === 3) {{
        return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span> 3/3 Completo
                </span>`;
      }} else if (count > 0) {{
        return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-600"></span> ${{count}}/3 Parcial
                </span>`;
      }} else {{
        return `<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                  <span class="w-1.5 h-1.5 rounded-full bg-rose-600"></span> 0/3 Sin Entrega
                </span>`;
      }}
    }}

    function renderItemBadge(item, label) {{
      if (item && item.submitted) {{
        const isUrl = typeof item.value === 'string' && (item.value.startsWith('http://') || item.value.startsWith('https://'));
        if (isUrl) {{
          return `<a href="${{item.value}}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition" title="${{item.value}}">
                    <span>✓</span> ${{label}}
                    <svg class="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                  </a>`;
        }} else {{
          const cleanName = item.value ? item.value.split('/').pop().split('\\\\').pop() : label;
          return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200" title="${{item.value}}">
                    <span>✓</span> ${{label}}
                  </span>`;
        }}
      }} else {{
        return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200">
                  <span>✕</span> Pendiente
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
      const filtered = APP_DATA.deliverables.filter(item => {{
        // Group filter
        if (selectedGroup !== 'all' && String(item.group_id) !== String(selectedGroup)) {{
          return false;
        }}

        // Pill filter
        if (currentFilter === 'complete' && item.completed_count !== 3) return false;
        if (currentFilter === 'partial' && (item.completed_count === 0 || item.completed_count === 3)) return false;
        if (currentFilter === 'missing' && item.completed_count !== 0) return false;
        if (currentFilter === 'needs-pdf' && item.tasks_pdf.submitted) return false;
        if (currentFilter === 'needs-demo' && item.demo_video.submitted) return false;
        if (currentFilter === 'needs-bug' && item.bug_video.submitted) return false;

        // Search text
        if (searchVal) {{
          const name = (item.student_name || '').toLowerCase();
          const gname = (item.group_name || '').toLowerCase();
          const notes = (item.notes || '').toLowerCase();
          if (!name.includes(searchVal) && !gname.includes(searchVal) && !notes.includes(searchVal)) {{
            return false;
          }}
        }}

        return true;
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
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-50 transition cursor-pointer border-b border-slate-100";
        tr.onclick = (e) => {{
          if (e.target.tagName !== 'A') {{
            openModal(s);
          }}
        }};

        tr.innerHTML = `
          <td class="py-3 px-4 font-bold text-slate-900 whitespace-nowrap">
            <div class="flex items-center gap-2">
              <span>${{s.student_name}}</span>
              <button class="text-slate-400 hover:text-sky-600" title="Ver ficha">ℹ️</button>
            </div>
          </td>
          <td class="py-3 px-3 text-slate-600 whitespace-nowrap">
            <span class="inline-block px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-[11px] font-semibold">
              ${{s.group_name}}
            </span>
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.tasks_pdf, 'PDF')}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.demo_video, 'Demo')}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderItemBadge(s.bug_video, 'Bug')}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{renderStatusPill(s.status, s.completed_count)}}
          </td>
          <td class="py-3 px-3 text-center whitespace-nowrap">
            ${{s.leader_feedback && s.leader_feedback.submitted ? 
              `<span class="text-emerald-700 text-[11px] font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200" title="${{s.leader_feedback.value}}">✓ Enviado</span>` : 
              `<span class="text-slate-400 text-[11px]">-</span>`}}
          </td>
          <td class="py-3 px-4 text-slate-500 text-[11px] max-w-xs truncate" title="${{s.notes}}">
            ${{s.notes || '-'}}
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

      groups.forEach(g => {{
        const card = document.createElement('div');
        card.className = "bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between";

        let membersHtml = '';
        g.students.forEach(st => {{
          const count = st.completed_count;
          const badgeClass = count === 3 ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 
                             count > 0 ? 'bg-amber-50 border-amber-200 text-amber-800' : 
                             'bg-rose-50 border-rose-200 text-rose-800';

          membersHtml += `
            <div class="p-2.5 rounded-xl border ${{badgeClass}} text-xs space-y-1">
              <div class="flex items-center justify-between font-bold">
                <span>${{st.student_name}}</span>
                <span>${{count}}/3</span>
              </div>
              <div class="flex items-center gap-1.5 text-[10px] pt-1">
                <span class="${{st.tasks_pdf.submitted ? 'text-emerald-700 font-bold' : 'text-rose-600'}}">${{st.tasks_pdf.submitted ? '✓' : '✕'}} PDF</span>
                <span>•</span>
                <span class="${{st.demo_video.submitted ? 'text-emerald-700 font-bold' : 'text-rose-600'}}">${{st.demo_video.submitted ? '✓' : '✕'}} Demo</span>
                <span>•</span>
                <span class="${{st.bug_video.submitted ? 'text-emerald-700 font-bold' : 'text-rose-600'}}">${{st.bug_video.submitted ? '✓' : '✕'}} Bug</span>
              </div>
            </div>
          `;
        }});

        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-extrabold text-base text-slate-900">${{g.name}}</h3>
              <span class="text-xs font-bold px-2 py-0.5 rounded-full ${{g.percentage === 100 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'}}">
                ${{g.percentage}}%
              </span>
            </div>
            <div class="w-full bg-slate-100 h-2 rounded-full overflow-hidden mb-4">
              <div class="${{g.percentage === 100 ? 'bg-emerald-500' : 'bg-sky-500'}} h-full transition-all" style="width: ${{g.percentage}}%"></div>
            </div>
            <div class="space-y-2 mb-4">
              ${{membersHtml}}
            </div>
          </div>
          <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[11px] text-slate-400 font-medium">${{g.complete_students}}/${{g.total_students}} al día</span>
            <button onclick="copyGroupNotice(${{g.id}})" class="inline-flex items-center gap-1 text-[11px] font-bold text-sky-600 hover:text-sky-800 transition py-1 px-2 rounded-lg hover:bg-sky-50">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
              <span>Copiar Aviso</span>
            </button>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function openModal(student) {{
      activeModalStudent = student;
      document.getElementById('modal-group-name').textContent = student.group_name;
      document.getElementById('modal-student-name').textContent = student.student_name;
      document.getElementById('modal-notes').textContent = student.notes || 'Sin observaciones registradas.';

      const cl = document.getElementById('modal-checklist');
      cl.innerHTML = `
        <div class="flex items-center justify-between p-2.5 rounded-xl border ${{student.tasks_pdf.submitted ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}}">
          <div class="flex items-center gap-2">
            <span class="font-bold">${{student.tasks_pdf.submitted ? '✓' : '✕'}}</span>
            <span class="font-semibold">1. PDF de Tareas Realizadas</span>
          </div>
          <span class="text-[11px] font-medium">${{student.tasks_pdf.submitted ? (student.tasks_pdf.value || 'Entregado') : 'Pendiente'}}</span>
        </div>
        <div class="flex items-center justify-between p-2.5 rounded-xl border ${{student.demo_video.submitted ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}}">
          <div class="flex items-center gap-2">
            <span class="font-bold">${{student.demo_video.submitted ? '✓' : '✕'}}</span>
            <span class="font-semibold">2. Video Demo del Proyecto</span>
          </div>
          <span class="text-[11px] font-medium">${{student.demo_video.submitted ? (student.demo_video.value.substring(0, 30) + (student.demo_video.value.length > 30 ? '...' : '')) : 'Pendiente'}}</span>
        </div>
        <div class="flex items-center justify-between p-2.5 rounded-xl border ${{student.bug_video.submitted ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}}">
          <div class="flex items-center gap-2">
            <span class="font-bold">${{student.bug_video.submitted ? '✓' : '✕'}}</span>
            <span class="font-semibold">3. Video del Bug Encontrado</span>
          </div>
          <span class="text-[11px] font-medium">${{student.bug_video.submitted ? (student.bug_video.value.substring(0, 30) + (student.bug_video.value.length > 30 ? '...' : '')) : 'Pendiente'}}</span>
        </div>
      `;

      document.getElementById('student-modal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('student-modal').classList.add('hidden');
      activeModalStudent = null;
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
      }}).catch(err => {{
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast(msg || 'Copiado al portapapeles');
      }});
    }}

    function copyStudentNotice() {{
      if (!activeModalStudent) return;
      const s = activeModalStudent;
      let text = `Hola ${{s.student_name}} (Grupo: ${{s.group_name}}):\\n`;
      text += `Revisamos tus entregas finales de la materia y este es tu estado actual:\\n`;
      text += `- PDF de tareas: ${{s.tasks_pdf.submitted ? '✅ Entregado' : '❌ PENDIENTE'}}\\n`;
      text += `- Video demo del proyecto: ${{s.demo_video.submitted ? '✅ Entregado' : '❌ PENDIENTE'}}\\n`;
      text += `- Video del bug: ${{s.bug_video.submitted ? '✅ Entregado' : '❌ PENDIENTE'}}\\n`;
      if (s.completed_count === 3) {{
        text += `\\n¡Excelente! Ya tenés todas las entregas completadas.`;
      }} else {{
        text += `\\nPor favor enviá lo antes posible lo que tengas pendiente para poder cerrar tu evaluación.`;
      }}
      copyToClipboard(text, `Aviso para ${{s.student_name}} copiado`);
    }}

    function copyGroupNotice(groupId) {{
      const g = APP_DATA.groups.find(x => x.id === groupId);
      if (!g) return;

      let text = `📢 **Grupo ${{g.name}} — Estado de Entregas Finales**\\n\\n`;
      g.students.forEach(st => {{
        const missing = [];
        if (!st.tasks_pdf.submitted) missing.push('PDF de Tareas');
        if (!st.demo_video.submitted) missing.push('Video Demo');
        if (!st.bug_video.submitted) missing.push('Video Bug');

        if (missing.length === 0) {{
          text += `• **${{st.student_name}}**: ✅ 3/3 Completo\\n`;
        }} else {{
          text += `• **${{st.student_name}}**: ⚠️ Debe: ${{missing.join(', ')}}\\n`;
        }}
      }});

      copyToClipboard(text, `Aviso de ${{g.name}} copiado`);
    }}

    function copyGeneralReport() {{
      let text = `📋 **Reporte de Entregas Finales — DCP (${{APP_DATA.updated_at}})**\\n\\n`;
      text += `• Alumnos Totales: 38\\n`;
      text += `• ✅ Completos (3/3): ${{APP_DATA.summary.complete_3_of_3}}\\n`;
      text += `• ⚠️ Parciales: ${{APP_DATA.summary.partial_2_of_3 + APP_DATA.summary.partial_1_of_3}}\\n`;
      text += `• ❌ Sin Entregar (0/3): ${{APP_DATA.summary.missing_0_of_3}}\\n\\n`;
      text += `**Alumnos que deben entregas:**\\n`;

      APP_DATA.deliverables.filter(d => d.completed_count < 3).forEach(d => {{
        const missing = [];
        if (!d.tasks_pdf.submitted) missing.push('PDF');
        if (!d.demo_video.submitted) missing.push('Demo');
        if (!d.bug_video.submitted) missing.push('Bug');
        text += `- ${{d.student_name}} (${{d.group_name}}): Debe ${{missing.join(' + ')}}\\n`;
      }});

      copyToClipboard(text, 'Reporte general copiado');
    }}

    function exportCSV() {{
      const headers = ['Alumno', 'Grupo', 'PDF Tareas', 'Video Demo', 'Video Bug', 'Feedback Lideres', 'Completados', 'Estado', 'Notas'];
      const rows = APP_DATA.deliverables.map(d => [
        `"${{d.student_name}}"`,
        `"${{d.group_name}}"`,
        d.tasks_pdf.submitted ? `"${{d.tasks_pdf.value.replace(/"/g, '""')}}"` : 'Pendiente',
        d.demo_video.submitted ? `"${{d.demo_video.value.replace(/"/g, '""')}}"` : 'Pendiente',
        d.bug_video.submitted ? `"${{d.bug_video.value.replace(/"/g, '""')}}"` : 'Pendiente',
        d.leader_feedback && d.leader_feedback.submitted ? 'Enviado' : 'No',
        d.completed_count,
        d.status,
        `"${{(d.notes || '').replace(/"/g, '""')}}"`
      ]);

      const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `entregas_finales_dcp_${{APP_DATA.updated_at}}.csv`);
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
