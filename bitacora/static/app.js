// GTG — Auditoría de Calidad
// app.js: reloj, menú, draft MO/Ítem, estado de procesos.

const DRAFT_KEY = 'gtg_orden_draft';
const PROC_KEY  = 'gtg_procesos';

// ── Reloj ─────────────────────────────────────────────────────────────────────
function updateClock() {
  const now     = new Date();
  const timeStr = now.toLocaleTimeString('es-DO', { hour12: false });
  const dateStr = now.toLocaleDateString('es-DO', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
  const el = document.getElementById('clock');
  const dt = document.getElementById('clock-date');
  const tb = document.getElementById('topbarDate');
  if (el) el.textContent = timeStr;
  if (dt) dt.textContent = dateStr;
  if (tb) tb.textContent = dateStr;
}

// ── Menú de usuario ───────────────────────────────────────────────────────────
function toggleUserMenu() {
  const menu = document.getElementById('userMenu');
  if (!menu) return;
  menu.classList.toggle('show', !menu.classList.contains('show'));
}
document.addEventListener('click', function(e) {
  const menu = document.getElementById('userMenu');
  const btn  = document.getElementById('userChipBtn');
  if (menu && btn && !btn.contains(e.target)) menu.classList.remove('show');
});

// ── Draft: guardar / cargar MO · Ítem · Descripción ──────────────────────────
function saveDraftOrden() {
  const mo   = document.getElementById('draft-mo');   // hidden input
  const item = document.getElementById('draft-item'); // hidden input
  const desc = document.getElementById('draft-desc');
  if (!mo) return;
  localStorage.setItem(DRAFT_KEY, JSON.stringify({
    mo:   mo.value   || '',
    item: item ? item.value : '',
    desc: desc ? desc.value : '',
  }));
}

function loadDraftOrden() {
  try {
    const d = JSON.parse(localStorage.getItem(DRAFT_KEY));
    if (!d) return;
    const mo   = document.getElementById('draft-mo');
    const item = document.getElementById('draft-item');
    const desc = document.getElementById('draft-desc');
    if (mo   && !mo.value)   mo.value   = d.mo   || '';
    if (item && !item.value) item.value = d.item || '';
    if (desc && !desc.value) desc.value = d.desc || '';
  } catch(e) {}
}

// ── Actualizar inputs visibles del MO / Ítem desde los hidden ────────────────
function updateMoDisplay() {
  const hidden = document.getElementById('draft-mo');
  const vis    = document.getElementById('mo-middle');
  if (!hidden || !vis) return;
  const pre = vis.dataset.pre || '';
  const suf = vis.dataset.suf || '';
  const v   = (hidden.value || '').toUpperCase();
  if (v.startsWith(pre)) {
    const inner = v.slice(pre.length);
    const sufRe = suf ? new RegExp(suf.replace('-', '\\-')) : /$/;
    vis.value = inner.replace(sufRe, '').replace(/\D/g, '').slice(0, 4);
  }
}

function updateItemDisplay() {
  const hidden = document.getElementById('draft-item');
  const vis    = document.getElementById('item-middle');
  if (!hidden || !vis) return;
  const pre = vis.dataset.pre || 'PTC';
  const len = parseInt(vis.dataset.len || '5', 10);
  const v   = (hidden.value || '').toUpperCase();
  vis.value = v.startsWith(pre)
    ? v.slice(pre.length).replace(/[^A-Z0-9]/g, '').slice(0, len)
    : '';
}

// ── Handlers del campo MO (split-input) ──────────────────────────────────────
let _moTimer = null;
function handleMoInput(input) {
  clearTimeout(_moTimer);
  const pre = input.dataset.pre || '';
  const suf = input.dataset.suf || '';
  _moTimer = setTimeout(() => {
    let v = input.value.toUpperCase();
    if (v.startsWith(pre)) {
      const sufRe = suf ? new RegExp(suf.replace('-', '\\-') + '.*') : /$/;
      v = v.slice(pre.length).replace(sufRe, '').replace(/\D/g, '').slice(0, 4);
    } else {
      v = v.replace(/\D/g, '').slice(0, 4);
    }
    input.value = v;
    document.getElementById('draft-mo').value = v ? `${pre}${v}${suf}` : '';
    saveDraftOrden();
  }, 80);
}

function handleMoPaste(event) {
  event.preventDefault();
  const input = event.target;
  const pre   = input.dataset.pre || '';
  const suf   = input.dataset.suf || '';
  let v = (event.clipboardData || window.clipboardData).getData('text').toUpperCase().trim();
  if (v.startsWith(pre)) v = v.slice(pre.length);
  if (suf) {
    const sufRe = new RegExp(suf.replace('-', '\\-'));
    v = v.replace(sufRe, '');
  }
  v = v.replace(/\D/g, '').slice(0, 4);
  input.value = v;
  document.getElementById('draft-mo').value = v ? `${pre}${v}${suf}` : '';
  saveDraftOrden();
}

// ── Handlers del campo Ítem (split-input) ────────────────────────────────────
let _itemTimer = null;
function handleItemInput(input) {
  clearTimeout(_itemTimer);
  const pre = input.dataset.pre || 'PTC';
  const len = parseInt(input.dataset.len || '5', 10);
  _itemTimer = setTimeout(() => {
    let v = input.value.toUpperCase();
    if (v.startsWith(pre)) v = v.slice(pre.length);
    v = v.replace(/[^A-Z0-9]/g, '').slice(0, len);
    input.value = v;
    document.getElementById('draft-item').value = v ? `${pre}${v}` : '';
    saveDraftOrden();
  }, 80);
}

function handleItemPaste(event) {
  event.preventDefault();
  const input = event.target;
  const pre = input.dataset.pre || 'PTC';
  const len = parseInt(input.dataset.len || '5', 10);
  let v = (event.clipboardData || window.clipboardData).getData('text').toUpperCase().trim();
  if (v.startsWith(pre)) v = v.slice(pre.length);
  v = v.replace(/[^A-Z0-9]/g, '').slice(0, len);
  input.value = v;
  document.getElementById('draft-item').value = v ? `${pre}${v}` : '';
  saveDraftOrden();
}

// ── Escáner de código de barras ───────────────────────────────────────────────
let _bcStream   = null;
let _bcTarget   = null;
let _bcDetector = null;
let _bcFrameId  = null;
let _bcZXing    = null;   // lector ZXing (fallback)
let _bcDone     = false;  // evita doble disparo

// Carga ZXing-js desde CDN de forma diferida (solo si BarcodeDetector no está)
function _loadZXing() {
  if (window.ZXing) return Promise.resolve(true);
  return new Promise(resolve => {
    const s   = document.createElement('script');
    s.src     = 'https://unpkg.com/@zxing/library@0.21.3/umd/index.min.js';
    s.onload  = () => resolve(true);
    s.onerror = () => resolve(false);
    document.head.appendChild(s);
  });
}

function _bcErrMsg(err) {
  if (!err) return '⚠ Error desconocido.';
  if (err.name === 'NotAllowedError') return '⚠ Permiso de cámara denegado. Habilítalo en la configuración del navegador.';
  if (err.name === 'NotFoundError')   return '⚠ No se encontró ninguna cámara en este dispositivo.';
  return `⚠ ${err.message || err}`;
}

async function openBarcodeScanner(visId) {
  const vis = document.getElementById(visId);
  if (!vis) return;

  _bcTarget = {
    visId,
    hiddenId: vis.dataset.hidden || 'draft-mo',
    pre: vis.dataset.pre || '',
    suf: vis.dataset.suf || '',
    len: parseInt(vis.dataset.len || '4', 10),
  };
  _bcDone = false;

  const modal  = document.getElementById('barcodeModal');
  const status = document.getElementById('bc-status');
  const label  = document.getElementById('bc-label');
  const video  = document.getElementById('barcodeVideo');

  modal.style.display = 'flex';
  status.style.color  = 'rgba(255,255,255,.65)';
  status.textContent  = 'Iniciando cámara…';
  label.textContent   = `${_bcTarget.pre}${'_'.repeat(_bcTarget.len)}${_bcTarget.suf}`;

  if (location.protocol !== 'https:' && !['localhost','127.0.0.1'].includes(location.hostname)) {
    status.textContent = '⚠ Se requiere HTTPS para acceder a la cámara.';
    return;
  }

  if ('BarcodeDetector' in window) {
    // ── Ruta nativa ─────────────────────────────────────────────────
    try {
      let formats = ['code_128'];
      try {
        const sup  = await BarcodeDetector.getSupportedFormats();
        const want = ['code_128','code_39','code_93','ean_13','ean_8','qr_code','data_matrix'];
        const ok   = want.filter(f => sup.includes(f));
        if (ok.length) formats = ok;
      } catch(_) {}

      _bcDetector    = new BarcodeDetector({ formats });
      _bcStream      = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      video.srcObject = _bcStream;
      await video.play();
      status.textContent = 'Apunta la cámara al código de barras…';

      (function scan() {
        if (!_bcStream) return;
        _bcDetector.detect(video)
          .then(codes => { codes.length ? _bcOnResult(codes[0].rawValue) : (_bcFrameId = requestAnimationFrame(scan)); })
          .catch(()  => { _bcFrameId = requestAnimationFrame(scan); });
      })();

    } catch(err) { status.textContent = _bcErrMsg(err); }

  } else {
    // ── Fallback: ZXing-js ───────────────────────────────────────────
    status.textContent = 'Cargando escáner…';
    const loaded = await _loadZXing();
    if (!loaded) {
      status.textContent = '⚠ No se pudo cargar el escáner. Verifica la conexión a internet.';
      return;
    }
    try {
      _bcZXing = new ZXing.BrowserMultiFormatReader();
      status.textContent = 'Apunta la cámara al código de barras…';
      _bcZXing.decodeFromVideoDevice(null, 'barcodeVideo', (result, err) => {
        if (result && !_bcDone) _bcOnResult(result.getText());
      }).catch(err => { status.textContent = _bcErrMsg(err); });
    } catch(err) { status.textContent = _bcErrMsg(err); }
  }
}

function _bcOnResult(raw) {
  if (_bcDone) return;
  _bcDone = true;

  const { visId, hiddenId, pre, suf, len } = _bcTarget;
  let v = raw.toUpperCase().trim();

  if (v.startsWith(pre)) v = v.slice(pre.length);
  if (suf) v = v.replace(new RegExp(suf.replace('-', '\\-') + '.*'), '');
  v = hiddenId === 'draft-item'
    ? v.replace(/[^A-Z0-9]/g, '').slice(0, len)
    : v.replace(/\D/g, '').slice(0, len);

  const vis    = document.getElementById(visId);
  const hidden = document.getElementById(hiddenId);
  if (vis)    vis.value    = v;
  if (hidden) hidden.value = v ? `${pre}${v}${suf}` : '';
  saveDraftOrden();

  const status = document.getElementById('bc-status');
  if (status) { status.style.color = '#4ade80'; status.textContent = `✓ Detectado: ${pre}${v}${suf}`; }
  setTimeout(closeBarcodeModal, 900);
}

function closeBarcodeModal() {
  if (_bcFrameId) { cancelAnimationFrame(_bcFrameId); _bcFrameId = null; }
  if (_bcStream)  { _bcStream.getTracks().forEach(t => t.stop()); _bcStream = null; }
  if (_bcZXing)   { try { _bcZXing.reset(); } catch(_) {} _bcZXing = null; }
  const modal = document.getElementById('barcodeModal');
  if (modal) modal.style.display = 'none';
}

// Cerrar con Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeBarcodeModal(); });

// ── Estado de procesos siguientes ─────────────────────────────────────────────
function saveProcesoState(imp, con) {
  localStorage.setItem(PROC_KEY, JSON.stringify({
    usa_impresion: imp,
    usa_conversion: con,
  }));
  applyProcesoTabs();
}

function applyProcesoTabs() {
  const raw = localStorage.getItem(PROC_KEY);
  if (!raw) return; // sin estado guardado → todos habilitados

  let procs;
  try { procs = JSON.parse(raw); } catch(e) { return; }

  [
    ['nav-impresion', procs.usa_impresion],
    ['nav-conversion', procs.usa_conversion],
  ].forEach(([id, enabled]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.opacity       = enabled ? '' : '0.35';
    el.style.pointerEvents = enabled ? '' : 'none';
    el.title               = enabled ? '' : 'Proceso no activado para esta orden';
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  updateClock();
  setInterval(updateClock, 1000);

  // Resaltar turno activo al cargar
  const inputTurno = document.getElementById('input-turno');
  if (inputTurno) {
    const t = inputTurno.value;
    document.querySelectorAll('.turno-btn').forEach(btn => {
      if (btn.getAttribute('onclick')?.includes(`'${t}'`)) {
        btn.style.background  = 'var(--red)';
        btn.style.color       = 'white';
        btn.style.borderColor = 'var(--red-dark)';
      }
    });
  }

  // Aplicar estado de procesos a las pestañas
  applyProcesoTabs();

  // Cargar draft y repoblar inputs visibles
  loadDraftOrden();
  updateMoDisplay();
  updateItemDisplay();

  // Guardar descripción al cambiar
  const desc = document.getElementById('draft-desc');
  if (desc) desc.addEventListener('input', saveDraftOrden);
});
