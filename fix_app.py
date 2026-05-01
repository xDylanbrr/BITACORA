import os

file_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix saveForm
save_form_old = """  const payload = {
    id: 'REQ-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random()*1000),
    area,
    fecha: document.getElementById(area + '-fecha')?.value || '',
    horaInicio: document.getElementById(area + '-hora')?.value || '',
    horaFin: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toLowerCase(),
    maquina: document.getElementById(area + '-maquina')?.value || '',
    mo: document.getElementById(area + '-mo')?.value || '',
    item: document.getElementById(area + '-item')?.value || '',
    descripcion: document.getElementById(area + '-desc')?.value || '',
    turno: lastDetectedTurno || detectTurno(),
    auditor: getSession()?.name || 'Sistema',
    filas: document.getElementById(area + '-body')?.querySelectorAll('tr').length || 0,
    guardadoAt: Date.now()
  };"""

save_form_new = """  const payload = {
    id: 'REQ-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random()*1000),
    area,
    fecha: document.getElementById(area + '-fecha')?.value || '',
    horaInicio: document.getElementById(area + '-hora')?.value || '',
    horaFin: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toLowerCase(),
    maquina: document.getElementById(area + '-maquina')?.value || '',
    mo: document.getElementById(area + '-mo')?.value || '',
    item: document.getElementById(area + '-item')?.value || '',
    descripcion: document.getElementById(area + '-desc')?.value || '',
    turno: lastDetectedTurno || detectTurno(),
    auditor: getSession()?.name || 'Sistema',
    filas: document.getElementById(area + '-body')?.querySelectorAll('tr').length || 0,
    guardadoAt: Date.now()
  };
  console.log('Saving payload:', payload);"""

content = content.replace(save_form_old, save_form_new)

# Fix renderHistoryRecords syntax errors
# Note: I need to be careful with the exact string matches here.
# Instead of replacing specific chunks, I'll replace the whole function if possible.

import re
render_func_pattern = r'function renderHistoryRecords\(\) \{[\s\S]+?\}'
new_render_func = """function renderHistoryRecords() {
  const tbody = document.getElementById('historyBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const search = (document.getElementById('historySearch')?.value || '').toLowerCase();
  const areaFilter = document.getElementById('historyArea')?.value || '';
  const fromDate = document.getElementById('historyFrom')?.value || '';
  const toDate = document.getElementById('historyTo')?.value || '';

  const saves = getSaves().sort((a, b) => b.guardadoAt - a.guardadoAt);
  const perms = getPermissions();

  saves.forEach(s => {
    if (areaFilter && s.area !== areaFilter) return;

    if (fromDate || toDate) {
      if (fromDate && s.fecha < fromDate) return;
      if (toDate && s.fecha > toDate) return;
    }

    if (search) {
      const fullText = Object.values(s).join(' ').toLowerCase();
      if (!fullText.includes(search)) return;
    }

    const tr = document.createElement('tr');
    const gDateStr = new Date(s.guardadoAt).toLocaleDateString('es-DO');
    const areaLabels = { ext: 'Extrusión', imp: 'Impresión', con: 'Conversión' };
    const areaName = areaLabels[s.area] || s.area;

    const btnHtml = perms.canEditHistory ? `
      <div style="display:flex;gap:4px;">
        <button class="btn role-delete" onclick="deleteHistoryRecord('${s.id}')" style="background:var(--red-soft);color:var(--red-dark);padding:4px 8px;font-size:10px;border-radius:4px;border:none;cursor:pointer;">Eliminar</button>
      </div>
    ` : '<span style="font-size:10px;color:var(--text-light)">Restringido</span>';

    tr.innerHTML = `
      <td>${gDateStr}</td>
      <td><span class="badge badge-amber">${areaName}</span></td>
      <td>${s.fecha}</td>
      <td style="font-weight:600;color:var(--blue);">${(s.horaInicio||'--')} - ${(s.horaFin||'--')}</td>
      <td>${s.maquina}</td>
      <td>${s.mo}</td>
      <td>${s.item}</td>
      <td><div style="max-width:120px;overflow:hidden;text-overflow:ellipsis;" title="${s.descripcion}">${s.descripcion}</div></td>
      <td>Turno ${s.turno}</td>
      <td>${(s.auditor||'')}</td>
      <td style="text-align:center;">${(s.filas || 0)}</td>
      <td>${btnHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}"""

content = re.sub(render_func_pattern, new_render_func, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated app.js")
