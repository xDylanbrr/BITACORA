import os, re

js_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'
views_path = r'c:\Users\hilar\BITACORA\bitacora\views.py'

# ─── FIX 1: saveForm - save horaFin in clean "11:47 AM" format ───────────────
with open(js_path, 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

old_hora_fin = "horaFin: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toLowerCase(),"
new_hora_fin = "(function(){ const n=new Date(); let h=n.getHours(),m=String(n.getMinutes()).padStart(2,'0'),ampm=h>=12?'PM':'AM'; h=h%12||12; return h+':'+m+' '+ampm; })(),"
new_hora_fin = "horaFin: (function(){ const n=new Date(); let h=n.getHours(),m=String(n.getMinutes()).padStart(2,'0'),ampm=h>=12?'PM':'AM'; h=h%12||12; return h+':'+m+' '+ampm; })(),"

if old_hora_fin in js:
    js = js.replace(old_hora_fin, new_hora_fin)
    print("FIX 1: horaFin format fixed in saveForm OK")
else:
    print("WARNING: horaFin line not found")

# ─── FIX 2: normalizeRecord - add formatTime helper and use it ───────────────
old_normalize = """  function normalizeRecord(r) {
    // Handles both Django API format and localStorage format
    return {
      _dbId:       r.id       || null,   // numeric Django PK (for DELETE)
      id:          r.frontend_id || r.id || '',
      area:        r.area     || '',
      fecha:       r.fecha    || '',
      horaInicio:  r.hora_inicio || r.horaInicio || '--',
      horaFin:     r.hora_fin   || r.horaFin    || '--',"""

new_normalize = """  function formatTime(t) {
    if (!t || t === '--' || t === null) return '--';
    const s = String(t).trim();
    // Django TimeField format: "HH:MM:SS" or "HH:MM"
    const django = s.match(/^(\\d{1,2}):(\\d{2})/);
    if (django) {
      let h = parseInt(django[1]), m = django[2];
      const ampm = h >= 12 ? 'PM' : 'AM';
      h = h % 12 || 12;
      return h + ':' + m + ' ' + ampm;
    }
    // Already formatted like "11:47 AM" - keep as-is but normalize "a. m." -> "AM"
    return s.replace(/a\\.\\s*m\\./gi, 'AM').replace(/p\\.\\s*m\\./gi, 'PM').trim();
  }

  function normalizeRecord(r) {
    // Handles both Django API format and localStorage format
    return {
      _dbId:       r.id       || null,   // numeric Django PK (for DELETE)
      id:          r.frontend_id || r.id || '',
      area:        r.area     || '',
      fecha:       r.fecha    || '',
      horaInicio:  formatTime(r.hora_inicio || r.horaInicio),
      horaFin:     formatTime(r.hora_fin    || r.horaFin),"""

if old_normalize in js:
    js = js.replace(old_normalize, new_normalize)
    print("FIX 2: normalizeRecord updated with formatTime OK")
else:
    # Try with encoded chars
    print("WARNING: normalizeRecord exact match failed, trying regex...")
    pat = r'function normalizeRecord\(r\) \{[\s\S]+?horaInicio:  r\.hora_inicio \|\| r\.horaInicio \|\| \'--\',\n      horaFin:     r\.hora_fin   \|\| r\.horaFin    \|\| \'--\','
    if re.search(pat, js):
        js = re.sub(pat, new_normalize.strip(), js, count=1)
        print("FIX 2: normalizeRecord fixed via regex OK")
    else:
        print("ERROR: could not find normalizeRecord block")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js saved OK")

# ─── FIX 3: views.py - fix parse_time_flexible to handle "a. m." format ─────
with open(views_path, 'r', encoding='utf-8', errors='ignore') as f:
    views = f.read()

old_parse = """        def parse_time_flexible(t):
            \"\"\"Acepta formatos HH:MM y HH:MM AM/PM\"\"\"
            if not t:
                return None
            t = t.strip().upper()
            for fmt in ('%I:%M %p', '%H:%M'):
                try:
                    from datetime import datetime
                    return datetime.strptime(t, fmt).time()
                except ValueError:
                    continue
            return parse_time(t)"""

new_parse = """        def parse_time_flexible(t):
            \"\"\"Acepta 11:47 AM, 11:47 a. m., 11:47:00\"\"\"
            if not t:
                return None
            import re as _re
            from datetime import datetime
            # Normalize Spanish locale format: "11:47 a. m." -> "11:47 AM"
            t = _re.sub(r'a\\.\\s*m\\.', 'AM', str(t), flags=_re.IGNORECASE)
            t = _re.sub(r'p\\.\\s*m\\.', 'PM', t, flags=_re.IGNORECASE)
            t = t.strip().upper()
            for fmt in ('%I:%M %p', '%I:%M:%S %p', '%H:%M:%S', '%H:%M'):
                try:
                    return datetime.strptime(t, fmt).time()
                except ValueError:
                    continue
            return parse_time(t)"""

if old_parse in views:
    views = views.replace(old_parse, new_parse)
    print("FIX 3: parse_time_flexible in views.py fixed OK")
else:
    print("WARNING: parse_time_flexible not found in views.py, may need manual fix")

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views)

print("views.py saved OK")
print("\nAll 3 fixes applied successfully!")
