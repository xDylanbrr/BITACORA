import os

file_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the start of renderHistoryRecords
start_tag = 'function renderHistoryRecords() {'
start_idx = content.find(start_tag)

if start_idx != -1:
    # Find the matching closing brace (this is naive but should work if there are no nested functions)
    # Actually, let's find the NEXT function definition or the end of the file.
    next_func_idx = content.find('function', start_idx + len(start_tag))
    if next_func_idx == -1:
        end_idx = len(content)
    else:
        # Search backwards for the last } before the next function
        end_idx = content.rfind('}', start_idx, next_func_idx) + 1
    
    if end_idx > start_idx:
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
}
"""
        content = content[:start_idx] + new_render_func + content[end_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully replaced renderHistoryRecords from {start_idx} to {end_idx}")
    else:
        print("Could not find end of function")
else:
    print("Could not find start of function")
