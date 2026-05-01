import os, re

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# 1. Fix normalizeRecord so it only assigns _dbId if it's a numeric ID (server record)
old_norm = "_dbId:       r.id       || null,"
new_norm = "_dbId:       (typeof r.id === 'number') ? r.id : null,"

if old_norm in js:
    js = js.replace(old_norm, new_norm)
    print("normalizeRecord fixed OK")
else:
    print("WARNING: normalizeRecord line not found exactly")

# 2. Fix deleteHistoryRecord to ALWAYS clean localStorage even if deleting from server
# This ensures the record doesn't "reappear" because it was still in the browser's backup.
old_delete = """function deleteHistoryRecord(id) {
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
}"""

# Improved delete logic that passes both IDs to ensure full cleanup
new_delete = """function deleteHistoryRecord(id) {
  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta accion no se puede deshacer. Deseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      // Parse the ID which might be "db:NUM|FRONTEND_ID" or just "FRONTEND_ID"
      let dbId = null;
      let frontendId = id;

      if (String(id).startsWith('db:')) {
        const parts = String(id).replace('db:', '').split('|');
        dbId = parts[0];
        frontendId = parts[1] || null;
      }

      // 1. Clean localStorage (always do this so it doesn't reappear)
      if (frontendId) {
        const saves = getSaves().filter(function(s) { return s.id !== frontendId; });
        localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
      }

      // 2. Clean Server if needed
      if (dbId) {
        const csrf = document.cookie.split(';').map(function(c){ return c.trim(); })
          .find(function(c){ return c.startsWith('csrftoken='); });
        const csrfVal = csrf ? csrf.split('=')[1] : '';
        fetch('/api/registro/' + dbId + '/', {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrfVal }
        }).then(function() {
          console.log('Registro eliminado del servidor');
        }).catch(function() {
          console.warn('No se pudo eliminar del servidor, pero se quito del local.');
        });
      }

      // Update UI immediately
      renderHistoryRecords();
      updateStats();
    }
  });
}"""

if old_delete in js:
    js = js.replace(old_delete, new_delete)
    print("deleteHistoryRecord fixed OK")
else:
    print("WARNING: deleteHistoryRecord exact match failed, using regex fallback")
    # Looser regex match for deleteHistoryRecord
    pat = r'function deleteHistoryRecord\(id\) \{[\s\S]+?\}\n  \}\);\n\}'
    if re.search(pat, js):
        js = re.sub(pat, new_delete, js, count=1)
        print("deleteHistoryRecord fixed via regex OK")
    else:
        print("ERROR: could not find deleteHistoryRecord block")

# 3. Update deleteArg construction in renderHistoryRecords
old_arg = "const deleteArg = s._dbId ? 'db:' + s._dbId : s.id;"
new_arg = "const deleteArg = s._dbId ? 'db:' + s._dbId + '|' + s.id : s.id;"

if old_arg in js:
    js = js.replace(old_arg, new_arg)
    print("deleteArg updated OK")
else:
    print("WARNING: deleteArg construction line not found")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js saved OK")
