import os, re

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# NEW renderHistoryRecords: reads from Django API, falls back to localStorage
# ─────────────────────────────────────────────────────────────────────────────
new_render = r"""function renderHistoryRecords() {
  const tbody = document.getElementById('historyBody');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;padding:24px;color:var(--text-light);font-size:13px;">Cargando historial...</td></tr>';

  const search    = (document.getElementById('historySearch')?.value || '').toLowerCase();
  const areaFilter = document.getElementById('historyArea')?.value || '';
  const fromDate  = document.getElementById('historyFrom')?.value || '';
  const toDate    = document.getElementById('historyTo')?.value || '';
  const perms     = getPermissions();

  function normalizeRecord(r) {
    // Handles both Django API format and localStorage format
    return {
      _dbId:       r.id       || null,   // numeric Django PK (for DELETE)
      id:          r.frontend_id || r.id || '',
      area:        r.area     || '',
      fecha:       r.fecha    || '',
      horaInicio:  r.hora_inicio || r.horaInicio || '--',
      horaFin:     r.hora_fin   || r.horaFin    || '--',
      maquina:     r.maquina    || '',
      mo:          r.mo         || '',
      item:        r.item       || '',
      descripcion: r.descripcion || '',
      turno:       r.turno      || '',
      auditor:     r.auditor    || '',
      filas:       r.filas      || 0,
      guardadoAt:  r.guardado_at ? new Date(r.guardado_at).getTime() : (r.guardadoAt || 0),
    };
  }

  function renderRows(records) {
    tbody.innerHTML = '';
    const areaLabels = { ext: 'Extrusión', imp: 'Impresión', con: 'Conversión' };
    const sorted = records
      .map(normalizeRecord)
      .sort((a, b) => b.guardadoAt - a.guardadoAt);

    const filtered = sorted.filter(s => {
      if (areaFilter && s.area !== areaFilter) return false;
      if (fromDate && s.fecha < fromDate) return false;
      if (toDate   && s.fecha > toDate)   return false;
      if (search) {
        const txt = Object.values(s).join(' ').toLowerCase();
        if (!txt.includes(search)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;padding:32px;color:var(--text-light);font-size:13px;">No hay registros guardados todavía.</td></tr>';
      return;
    }

    filtered.forEach(s => {
      const tr = document.createElement('tr');
      const gDateStr = s.guardadoAt ? new Date(s.guardadoAt).toLocaleDateString('es-DO') : '--';
      const areaName = areaLabels[s.area] || s.area;

      // Delete uses _dbId if available (server record), otherwise frontend id (localStorage only)
      const deleteArg = s._dbId ? 'db:' + s._dbId : s.id;

      const btnHtml = perms.canEditHistory
        ? `<div style="display:flex;gap:4px;">
            <button onclick="deleteHistoryRecord('${deleteArg}')"
              style="background:var(--red-soft);color:var(--red-dark);padding:4px 10px;font-size:11px;border-radius:6px;border:none;cursor:pointer;font-weight:600;">
              Eliminar
            </button>
          </div>`
        : '<span style="font-size:11px;color:var(--text-light)">Restringido</span>';

      const horaDisplay = (s.horaInicio && s.horaInicio !== '--') 
        ? s.horaInicio + ' → ' + (s.horaFin || '--')
        : '--';

      tr.innerHTML = `
        <td>${gDateStr}</td>
        <td><span class="badge badge-amber">${areaName}</span></td>
        <td>${s.fecha || '--'}</td>
        <td style="font-weight:600;color:var(--blue);white-space:nowrap;">${horaDisplay}</td>
        <td>${s.maquina || '--'}</td>
        <td>${s.mo || '--'}</td>
        <td>${s.item || '--'}</td>
        <td><div style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${s.descripcion}">${s.descripcion || '--'}</div></td>
        <td>Turno ${s.turno || '--'}</td>
        <td>${s.auditor || '--'}</td>
        <td style="text-align:center;">${s.filas || 0}</td>
        <td>${btnHtml}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Try to load from Django API first
  fetch('/api/registro/')
    .then(function(res) { return res.ok ? res.json() : Promise.reject(res.status); })
    .then(function(data) {
      const serverRecords = (data.registros || []);
      // Also merge any localStorage records not yet on server (offline saves)
      const localRecords = getSaves().filter(function(ls) {
        return !serverRecords.some(function(sr) { return sr.frontend_id === ls.id; });
      });
      renderRows([...serverRecords, ...localRecords]);
    })
    .catch(function(err) {
      console.warn('API no disponible, usando localStorage:', err);
      renderRows(getSaves());
    });
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# NEW deleteHistoryRecord: calls Django DELETE API + removes from localStorage
# ─────────────────────────────────────────────────────────────────────────────
new_delete = r"""function deleteHistoryRecord(id) {
  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta accion no se puede deshacer. Deseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      // If the id starts with "db:" it is a Django DB record
      if (String(id).startsWith('db:')) {
        const dbId = String(id).replace('db:', '');
        const csrf = document.cookie.split(';').map(function(c){ return c.trim(); })
          .find(function(c){ return c.startsWith('csrftoken='); });
        const csrfVal = csrf ? csrf.split('=')[1] : '';
        fetch('/api/registro/' + dbId + '/', {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrfVal }
        }).then(function() {
          renderHistoryRecords();
          updateStats();
        }).catch(function() {
          alert('Error al eliminar del servidor. Intenta de nuevo.');
        });
      } else {
        // localStorage-only record
        const saves = getSaves().filter(function(s) { return s.id !== id; });
        localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
        renderHistoryRecords();
        updateStats();
      }
    }
  });
}
"""

# Replace renderHistoryRecords function
pattern_render = r'function renderHistoryRecords\(\) \{[\s\S]+?\n\}'
if re.search(pattern_render, content):
    content = re.sub(pattern_render, new_render.strip(), content, count=1)
    print("renderHistoryRecords replaced OK")
else:
    content += '\n' + new_render
    print("renderHistoryRecords appended (not found)")

# Replace deleteHistoryRecord function
pattern_delete = r'function deleteHistoryRecord\(id\) \{[\s\S]+?\n\}'
if re.search(pattern_delete, content):
    content = re.sub(pattern_delete, new_delete.strip(), content, count=1)
    print("deleteHistoryRecord replaced OK")
else:
    content += '\n' + new_delete
    print("deleteHistoryRecord appended (not found)")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("app.js saved OK")
