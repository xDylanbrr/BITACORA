import os, re

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# 1. Ensure constants are correct
if "const STORAGE_SAVES_KEY = 'gtg_quality_saves';" not in js:
    js = js.replace("const STORAGE_SAVES_KEY = 'gtg_saves';", "const STORAGE_SAVES_KEY = 'gtg_quality_saves';")

# 2. Add Missing Functions at the top (after pad/initials)
missing_funcs = """
/** 
 * Permisos por Rol
 */
function getPermissions() {
  const sess = getSession();
  const role = (sess?.role || '').toLowerCase();
  const isAdmin = role === 'administrador';
  const isSup = role === 'supervisor';
  const isAuditor = role === 'auditor';
  return {
    canEditHistory: isAdmin || isSup,
    canDeleteHistory: isAdmin,
    canManageUsers: isAdmin,
    canViewAllForms: true,
    role: sess?.role || 'Visitante',
    isAdmin, isSup, isAuditor
  };
}

/**
 * Custom confirm dialog
 */
function gtgConfirm({ title = 'Confirmar', message = '', okText = 'Aceptar', icon = '', onOk }) {
  const modal = document.getElementById('gtgConfirmModal');
  const titleEl = document.getElementById('gtgConfirmTitle');
  const msgEl = document.getElementById('gtgConfirmMsg');
  const iconEl = document.getElementById('gtgConfirmIcon');
  const okBtn = document.getElementById('gtgConfirmOk');
  const cancelBtn = document.getElementById('gtgConfirmCancel');
  if (!modal) { if (confirm(message)) onOk(); return; }
  titleEl.textContent = title;
  msgEl.textContent = message;
  iconEl.textContent = icon || '';
  iconEl.style.display = icon ? 'block' : 'none';
  okBtn.textContent = okText;
  modal.classList.add('show');
  function close() {
    modal.classList.remove('show');
    okBtn.replaceWith(okBtn.cloneNode(true));
    cancelBtn.replaceWith(cancelBtn.cloneNode(true));
  }
  document.getElementById('gtgConfirmOk').onclick = function() { close(); if (typeof onOk === 'function') onOk(); };
  document.getElementById('gtgConfirmCancel').onclick = close;
  modal.onclick = function(e) { if (e.target === modal) close(); };
}

/** Precarga los usuarios reales de Calidad */
function ensureSeedUsers() {
  try {
    const users = JSON.parse(localStorage.getItem('gtg_quality_users')) || [];
    const seedData = [
      { employeeId: "0001", name: "Administrador GTG", role: "Administrador", email: "admin@gtg.local", dept: "Calidad", position: "Administrador de Sistema", company: "GLOBAL", gender: "N/A", password: "Admin1234", active: true },
      { employeeId: "0814", name: "Reily Nalda Santos Guzmán", role: "Supervisor", email: "rsantos@gtg.com.do", dept: "Calidad", position: "Coordinador de calidad e ingeniería", company: "GLOBAL", gender: "Femenino", password: "1234", active: true },
      { employeeId: "0852", name: "Eloy José Delgado Álvarez", role: "Supervisor", email: "edelgado@gtg.com.do", dept: "Calidad", position: "Supervisor de calidad e ingeniería", company: "GLOBAL", gender: "Masculino", password: "1234", active: true },
      { employeeId: "0906", name: "Esther Noemí Taveras Hernández", role: "Auditor", email: "esthertaveras1829@gmail.com", dept: "Calidad", position: "Auditor de Calidad", company: "GLOBAL", gender: "Femenino", password: "1234", active: true },
      { employeeId: "1063", name: "Randy Eduardo Vargas Marmolejos", role: "Auditor", email: "randyvargassem04@gmail.com", dept: "Calidad", position: "Auditor de Calidad", company: "GLOBAL", gender: "Masculino", password: "1234", active: true },
      { employeeId: "1087", name: "Yulian Jose Victoriano Martinez", role: "Auditor", email: "Yulianm23@gmail.com", dept: "Calidad", position: "Auditor de Calidad", company: "GLOBAL", gender: "Masculino", password: "1234", active: true }
    ];
    let modified = false;
    seedData.forEach(seed => {
      if (!users.find(u => String(u.employeeId) === String(seed.employeeId))) {
        users.push({ ...seed, joined: new Date().toLocaleDateString('es-DO') });
        modified = true;
      }
    });
    if (modified) localStorage.setItem('gtg_quality_users', JSON.stringify(users));
  } catch(e) {}
}

function getRecords() {
  try { return JSON.parse(localStorage.getItem('gtg_quality_saves')) || []; } catch(e) { return []; }
}
function saveRecords(recs) {
  localStorage.setItem('gtg_quality_saves', JSON.stringify(recs));
}
"""

if "function getPermissions()" not in js:
    pos = js.find('function pad(n)')
    if pos != -1:
        js = js[:pos] + missing_funcs + "\n" + js[pos:]

# 3. Fix handleLogin for employeeId
login_old = """function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value.trim().toLowerCase();
  const password = document.getElementById('loginPassword').value;"""

login_new = """function handleLogin(e) {
  e.preventDefault();
  const inputVal = (document.getElementById('loginEmployeeId') || document.getElementById('loginEmail'))?.value.trim() || '';
  const password = document.getElementById('loginPassword').value;
  const users = getStoredUsers();
  const user = users.find(u => (String(u.employeeId) === String(inputVal) || u.email.toLowerCase() === inputVal.toLowerCase()) && u.password === password);
  if (!user) { document.getElementById('loginError').classList.add('show'); return; }"""

if login_old in js:
    js = js.replace(login_old, login_new)
    # Remove the old find logic if it's there
    js = re.sub(r'const user = getStoredUsers\(\)\.find\(u => u\.email === email && u\.password === password\);', '', js)

# 4. Add Historial Render and Delete at the end
history_logic = """
function renderHistoryRecords() {
  const tbody = document.getElementById('historyBody');
  if (!tbody) return;
  const search = (document.getElementById('historySearch')?.value || '').toLowerCase();
  const areaFilter = document.getElementById('historyArea')?.value || '';
  const fromDate = document.getElementById('historyFrom')?.value || '';
  const toDate = document.getElementById('historyTo')?.value || '';
  const perms = getPermissions();
  const records = getRecords().sort((a, b) => b.guardadoAt - a.guardadoAt);
  tbody.innerHTML = '';
  records.forEach(s => {
    if (areaFilter && s.area !== areaFilter) return;
    if (fromDate && s.fecha < fromDate) return;
    if (toDate && s.fecha > toDate) return;
    if (search) {
       const txt = `${s.mo} ${s.item} ${s.maquina} ${s.auditor} ${s.descripcion}`.toLowerCase();
       if (!txt.includes(search)) return;
    }
    const tr = document.createElement('tr');
    const areaLabels = { ext: 'Extrusión', imp: 'Impresión', con: 'Conversión' };
    const btnHtml = perms.isAdmin ? `<button class="btn" style="background:var(--red-soft);color:var(--red-dark);padding:4px 8px;font-size:10px;border:none;cursor:pointer;" onclick="deleteHistoryRecord('${s.id}')">Eliminar</button>` : '';
    tr.innerHTML = `
      <td>${new Date(s.guardadoAt).toLocaleDateString('es-DO')}</td>
      <td><span class="badge badge-amber">${areaLabels[s.area]||s.area}</span></td>
      <td>${s.fecha}</td>
      <td style="font-weight:600;color:var(--blue);">${s.horaInicio} - ${s.horaFin}</td>
      <td>${s.maquina}</td><td>${s.mo}</td><td>${s.item}</td>
      <td><div style="max-width:120px;overflow:hidden;text-overflow:ellipsis;" title="${s.descripcion}">${s.descripcion}</div></td>
      <td>Turno ${s.turno}</td><td>${s.auditor}</td><td style="text-align:center;">${s.filas}</td>
      <td>${btnHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

function deleteHistoryRecord(id) {
  const perms = getPermissions();
  if (!perms.isAdmin) { alert("Solo el administrador puede eliminar."); return; }
  gtgConfirm({
    title: 'Eliminar registro',
    message: '¿Seguro que deseas eliminar este registro?',
    okText: 'Eliminar',
    onOk: function() {
      const recs = getRecords().filter(r => String(r.id) !== String(id));
      saveRecords(recs);
      renderHistoryRecords();
      if (typeof updateStats === 'function') updateStats();
    }
  });
}
"""

if "function renderHistoryRecords" not in js:
    js += history_logic

# 5. Fix saveForm to include ID and use localStorage
# I'll replace the payload part
payload_old = r'const payload = \{\s+area,\s+fecha: document\.getElementById\(area \+ \'-fecha\'\)\?.value \|\| \'\',\s+horaInicio: document\.getElementById\(area \+ \'-hora\'\)\?.value \|\| \'\',\s+horaFin: new Date\(\)\.toLocaleTimeString\(\)\.toLowerCase\(\),'
payload_new = """const payload = {
      id: 'REG-' + Date.now() + '-' + Math.random().toString(36).slice(2,7),
      area,
      fecha: document.getElementById(area + '-fecha')?.value || '',
      horaInicio: document.getElementById(area + '-hora')?.value || '',
      horaFin: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }),"""

js = re.sub(payload_old, payload_new, js)

# 6. Update initApp to call ensureSeedUsers
if "ensureSeedUsers();" not in js:
    js = js.replace("function initApp() {", "function initApp() {\n  ensureSeedUsers();")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Restoration and Fix complete.")
