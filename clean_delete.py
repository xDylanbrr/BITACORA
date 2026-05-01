import os

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

# Replace the whole deleteHistoryRecord function with a clean version
old_func = """function deleteHistoryRecord(id) {
  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta acci\u00f3n no se puede deshacer. \u00bfDeseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      const saves = getSaves().filter(function(s){ return s.id !== id; });
      localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
      renderHistoryRecords();
      updateStats();
    }
  });
  return; // the actual logic runs inside onOk above
  const saves = getSaves().filter(s => s.id !== id);
  localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
  renderHistoryRecords();
  updateStats(); if (typeof renderHistoryRecords === 'function') renderHistoryRecords();
}"""

new_func = """function deleteHistoryRecord(id) {
  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta accion no se puede deshacer. Deseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      const saves = getSaves().filter(function(s){ return s.id !== id; });
      localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
      renderHistoryRecords();
      updateStats();
    }
  });
}"""

# Use a looser find since encoding mangled accented chars
import re
pattern = r'function deleteHistoryRecord\(id\) \{[\s\S]+?\n\}'
match = re.search(pattern, js)
if match:
    js = js[:match.start()] + new_func + js[match.end():]
    print("deleteHistoryRecord cleaned OK")
else:
    print("WARNING: function not found by regex")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated")
