import os

file_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

getperm_func = """
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
    canViewAllForms: isAdmin || isSup || isAuditor,
    role,
    isAdmin,
    isSup,
    isAuditor
  };
}
"""

if 'function getPermissions()' not in content:
    pos = content.find('function handleLogin')
    if pos != -1:
        content = content[:pos] + getperm_func + '\n' + content[pos:]
        print("getPermissions injected OK")
    else:
        print("ERROR: could not find injection point")
else:
    print("getPermissions already exists")

old_save_block = "    localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));\n    \n    updateStats();"
new_save_block = """    localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
    (function(p) {
      const csrf = document.cookie.split(';').map(function(c){return c.trim();}).find(function(c){return c.startsWith('csrftoken=');});
      const csrfVal = csrf ? csrf.split('=')[1] : '';
      fetch('/api/registro/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfVal},
        body: JSON.stringify(p)
      }).then(function(r){ if(!r.ok) console.warn('Backend no disponible'); else console.log('Registro enviado al servidor'); })
        .catch(function(){ console.warn('Backend offline, solo localStorage'); });
    })(payload);
    updateStats();"""

if old_save_block in content:
    content = content.replace(old_save_block, new_save_block)
    print("Django API call added OK")
else:
    print("WARNING: save block not found, API call not added")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("app.js updated OK")
