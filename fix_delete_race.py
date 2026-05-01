import os, re

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# Fix deleteHistoryRecord to wait for server confirmation before refreshing the list
new_delete_logic = """function deleteHistoryRecord(id) {
  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta accion no se puede deshacer. Deseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      let dbId = null;
      let frontendId = id;

      if (String(id).startsWith('db:')) {
        const parts = String(id).replace('db:', '').split('|');
        dbId = parts[0];
        frontendId = parts[1] || null;
      }

      // 1. Clean localStorage immediately
      if (frontendId) {
        const saves = getSaves().filter(function(s) { return s.id !== frontendId; });
        localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
      }

      // 2. Define the refresh UI function
      const refreshUI = function() {
        renderHistoryRecords();
        updateStats();
      };

      // 3. Delete from server if it exists there
      if (dbId) {
        const csrf = document.cookie.split(';').map(function(c){ return c.trim(); })
          .find(function(c){ return c.startsWith('csrftoken='); });
        const csrfVal = csrf ? csrf.split('=')[1] : '';
        
        fetch('/api/registro/' + dbId + '/', {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrfVal }
        })
        .then(function(res) {
          if (!res.ok) throw new Error('Server error');
          console.log('Registro eliminado del servidor OK');
          refreshUI(); // Refresh ONLY after server confirms
        })
        .catch(function(err) {
          console.warn('Error servidor, pero se quito del local:', err);
          refreshUI();
        });
      } else {
        // Just local, refresh immediately
        refreshUI();
      }
    }
  });
}"""

# Replace the whole function block
pat = r'function deleteHistoryRecord\(id\) \{[\s\S]+?\}\n  \}\);\n\}'
if re.search(pat, js):
    js = re.sub(pat, new_delete_logic, js, count=1)
    print("deleteHistoryRecord logic updated to prevent race condition OK")
else:
    print("ERROR: could not find deleteHistoryRecord block for replacement")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js saved OK")
