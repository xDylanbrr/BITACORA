import os

# 1. Inject the custom modal HTML into index.html before </body>
html_path = r'c:\Users\hilar\BITACORA\bitacora\templates\index.html'

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

modal_html = """
<!-- Custom Confirm Modal -->
<div id="gtgConfirmModal" style="
  display:none;
  position:fixed;inset:0;z-index:99999;
  background:rgba(10,10,20,0.65);
  backdrop-filter:blur(4px);
  align-items:center;justify-content:center;
">
  <div style="
    background:#1a1a2e;
    border:1px solid rgba(255,255,255,0.1);
    border-radius:16px;
    padding:32px 36px;
    max-width:420px;width:90%;
    box-shadow:0 24px 64px rgba(0,0,0,0.5);
    text-align:center;
    animation:gtgModalIn 0.2s ease;
  ">
    <div id="gtgConfirmIcon" style="font-size:40px;margin-bottom:12px;">⚠️</div>
    <div id="gtgConfirmTitle" style="font-family:'Outfit',sans-serif;font-weight:700;font-size:18px;color:#fff;margin-bottom:8px;"></div>
    <div id="gtgConfirmMsg" style="font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;color:rgba(255,255,255,0.65);margin-bottom:24px;line-height:1.5;"></div>
    <div style="display:flex;gap:12px;justify-content:center;">
      <button id="gtgConfirmCancel" style="
        flex:1;max-width:140px;height:42px;
        background:rgba(255,255,255,0.08);
        color:rgba(255,255,255,0.7);
        border:1.5px solid rgba(255,255,255,0.12);
        border-radius:10px;font-weight:600;font-size:14px;cursor:pointer;
        font-family:'Plus Jakarta Sans',sans-serif;
        transition:all 0.15s;
      " onmouseover="this.style.background='rgba(255,255,255,0.14)'" onmouseout="this.style.background='rgba(255,255,255,0.08)'">
        Cancelar
      </button>
      <button id="gtgConfirmOk" style="
        flex:1;max-width:140px;height:42px;
        background:linear-gradient(135deg,#c0392b,#922b21);
        color:#fff;border:none;
        border-radius:10px;font-weight:700;font-size:14px;cursor:pointer;
        font-family:'Plus Jakarta Sans',sans-serif;
        box-shadow:0 4px 16px rgba(192,57,43,0.4);
        transition:all 0.15s;
      " onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='translateY(0)'">
        Eliminar
      </button>
    </div>
  </div>
</div>
<style>
@keyframes gtgModalIn {
  from { opacity:0; transform:scale(0.9) translateY(-10px); }
  to   { opacity:1; transform:scale(1) translateY(0); }
}
#gtgConfirmModal.show { display:flex !important; }
</style>
"""

if 'gtgConfirmModal' not in html:
    html = html.replace('</body>', modal_html + '\n</body>')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Modal HTML injected into index.html OK")
else:
    print("Modal already exists in index.html")

# 2. Inject the gtgConfirm() JS function into app.js and replace confirm() call
js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

gtg_confirm_func = """
/**
 * Custom confirm dialog replacing the ugly native browser confirm().
 * Usage: gtgConfirm({ title, message, okText, onOk })
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

  document.getElementById('gtgConfirmOk').onclick = function() {
    close();
    if (typeof onOk === 'function') onOk();
  };
  document.getElementById('gtgConfirmCancel').onclick = close;
  modal.onclick = function(e) { if (e.target === modal) close(); };
}
"""

# Inject the function before the first function definition in the file
if 'function gtgConfirm' not in js:
    pos = js.find('function handleLogin')
    if pos == -1:
        pos = js.find('function getPermissions')
    js = js[:pos] + gtg_confirm_func + '\n' + js[pos:]
    print("gtgConfirm() function injected OK")
else:
    print("gtgConfirm() already exists")

# Replace the ugly confirm() call in deleteHistoryRecord
old_confirm = "  if (!confirm('Seguro que deseas eliminar este registro del historial?')) return;"
new_confirm = """  gtgConfirm({
    title: 'Eliminar registro',
    message: 'Esta acción no se puede deshacer. ¿Deseas eliminar este registro del historial?',
    okText: 'Eliminar',
    onOk: function() {
      const saves = getSaves().filter(function(s){ return s.id !== id; });
      localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));
      renderHistoryRecords();
      updateStats();
    }
  });
  return; // the actual logic runs inside onOk above"""

if old_confirm in js:
    # We also need to remove the lines after the confirm that were part of the original function
    js = js.replace(old_confirm, new_confirm)
    print("confirm() replaced with gtgConfirm() OK")
else:
    print("WARNING: confirm() call not found - may have already been replaced")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Done! app.js updated.")
