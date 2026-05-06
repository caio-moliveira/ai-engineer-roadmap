from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Receipt Scanner</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #f5f5f7;
      --card: #ffffff;
      --primary: #1d1d1f;
      --accent: #0071e3;
      --accent-hover: #0077ed;
      --muted: #6e6e73;
      --border: #d2d2d7;
      --success-bg: #f0fdf4;
      --success-border: #86efac;
      --radius: 14px;
      --shadow: 0 2px 16px rgba(0,0,0,.08);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--primary);
      min-height: 100dvh;
      padding: 24px 16px 48px;
    }

    h1 { font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 4px; }
    .subtitle { text-align: center; color: var(--muted); font-size: .875rem; margin-bottom: 28px; }

    .card {
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 20px;
      margin-bottom: 16px;
    }

    /* Upload area */
    .upload-label {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
      border: 2px dashed var(--border);
      border-radius: 10px;
      padding: 28px 16px;
      cursor: pointer;
      transition: border-color .2s, background .2s;
    }
    .upload-label:hover { border-color: var(--accent); background: #f0f7ff; }
    .upload-label svg { color: var(--muted); }
    .upload-label span { font-size: .9rem; color: var(--muted); }
    .upload-label strong { font-size: 1rem; color: var(--primary); }
    #fileInput { display: none; }

    #preview {
      display: none;
      width: 100%;
      max-height: 240px;
      object-fit: contain;
      border-radius: 8px;
      margin-top: 14px;
    }

    .btn {
      display: block;
      width: 100%;
      padding: 14px;
      border: none;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background .2s, opacity .2s;
    }
    .btn-primary { background: var(--accent); color: #fff; margin-top: 14px; }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-primary:disabled { opacity: .5; cursor: not-allowed; }

    /* Spinner */
    .spinner {
      display: none;
      width: 22px; height: 22px;
      border: 3px solid rgba(255,255,255,.4);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin .7s linear infinite;
      margin: 0 auto;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* Result */
    #result { display: none; }
    .result-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 4px;
    }
    .field { background: var(--success-bg); border: 1px solid var(--success-border); border-radius: 8px; padding: 10px 12px; }
    .field-label { font-size: .7rem; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-bottom: 2px; }
    .field-value { font-size: .95rem; font-weight: 500; word-break: break-word; }
    .field.full { grid-column: 1 / -1; }
    .amount-value { font-size: 1.4rem; font-weight: 700; color: #16a34a; }

    /* History */
    h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: 12px; }
    .receipt-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 0;
      border-bottom: 1px solid var(--border);
    }
    .receipt-item:last-child { border-bottom: none; padding-bottom: 0; }
    .receipt-info { flex: 1; min-width: 0; }
    .receipt-desc { font-size: .9rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .receipt-meta { font-size: .775rem; color: var(--muted); margin-top: 2px; }
    .receipt-amount { font-weight: 700; font-size: .95rem; color: var(--accent); white-space: nowrap; }
    .btn-delete {
      background: none; border: none; cursor: pointer;
      color: #dc2626; font-size: 1.1rem; padding: 4px 6px;
      border-radius: 6px; transition: background .15s;
      flex-shrink: 0;
    }
    .btn-delete:hover { background: #fee2e2; }

    .empty { text-align: center; color: var(--muted); font-size: .875rem; padding: 16px 0; }
    .error { color: #dc2626; font-size: .875rem; margin-top: 10px; text-align: center; }
  </style>
</head>
<body>

  <h1>Receipt Scanner</h1>
  <p class="subtitle">Tire uma foto ou envie uma imagem de recibo para extrair os dados</p>

  <!-- Upload card -->
  <div class="card">
    <label class="upload-label" for="fileInput">
      <svg width="36" height="36" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
      </svg>
      <strong>Tirar foto ou escolher arquivo</strong>
      <span>PNG, JPG, WEBP suportados</span>
    </label>
    <input id="fileInput" type="file" accept="image/*" capture="environment" />
    <img id="preview" alt="Pré-visualização do recibo" />
    <button class="btn btn-primary" id="submitBtn" disabled>
      <span id="btnText">Escanear Recibo</span>
      <div class="spinner" id="spinner"></div>
    </button>
    <p class="error" id="error"></p>
  </div>

  <!-- Result card -->
  <div class="card" id="result">
    <div class="result-grid">
      <div class="field full">
        <div class="field-label">Descrição</div>
        <div class="field-value" id="r-description">—</div>
      </div>
      <div class="field">
        <div class="field-label">Valor</div>
        <div class="field-value amount-value" id="r-amount">—</div>
      </div>
      <div class="field">
        <div class="field-label">Data &amp; Hora</div>
        <div class="field-value" id="r-time">—</div>
      </div>
      <div class="field full">
        <div class="field-label">Local</div>
        <div class="field-value" id="r-location">—</div>
      </div>
    </div>
  </div>

  <!-- History card -->
  <div class="card">
    <h2>Histórico</h2>
    <div id="history"><p class="empty">Nenhum recibo ainda.</p></div>
  </div>

  <script>
    const API = '';
    const fileInput  = document.getElementById('fileInput');
    const preview    = document.getElementById('preview');
    const submitBtn  = document.getElementById('submitBtn');
    const btnText    = document.getElementById('btnText');
    const spinner    = document.getElementById('spinner');
    const errorEl    = document.getElementById('error');
    const resultCard = document.getElementById('result');

    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (!file) return;
      preview.src = URL.createObjectURL(file);
      preview.style.display = 'block';
      submitBtn.disabled = false;
      resultCard.style.display = 'none';
      errorEl.textContent = '';
    });

    submitBtn.addEventListener('click', async () => {
      const file = fileInput.files[0];
      if (!file) return;

      setLoading(true);
      errorEl.textContent = '';

      const form = new FormData();
      form.append('file', file);

      try {
        const res = await fetch(`${API}/receipts`, { method: 'POST', body: form });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Erro no servidor: ${res.status}`);
        }
        const data = await res.json();
        renderResult(data);
        loadHistory();
      } catch (e) {
        errorEl.textContent = e.message;
      } finally {
        setLoading(false);
      }
    });

    function renderResult(r) {
      document.getElementById('r-description').textContent = r.description || '—';
      document.getElementById('r-amount').textContent =
        r.amount != null ? `R$ ${r.amount.toFixed(2)}` : '—';
      document.getElementById('r-time').textContent =
        r.purchase_time ? new Date(r.purchase_time).toLocaleString('pt-BR') : '—';
      document.getElementById('r-location').textContent = r.location || '—';
      resultCard.style.display = 'block';
      resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async function loadHistory() {
      const historyEl = document.getElementById('history');
      try {
        const res = await fetch(`${API}/receipts`);
        const items = await res.json();
        if (!items.length) {
          historyEl.innerHTML = '<p class="empty">Nenhum recibo ainda.</p>';
          return;
        }
        historyEl.innerHTML = items.map(r => `
          <div class="receipt-item" id="item-${r.id}">
            <div class="receipt-info">
              <div class="receipt-desc">${r.description || 'Desconhecido'}</div>
              <div class="receipt-meta">${r.location || ''} &bull; ${
                r.purchase_time
                  ? new Date(r.purchase_time).toLocaleDateString('pt-BR')
                  : 'Sem data'
              }</div>
            </div>
            <div class="receipt-amount">${r.amount != null ? 'R$ ' + r.amount.toFixed(2) : '—'}</div>
            <button class="btn-delete" title="Excluir" onclick="removeReceipt('${r.id}')">&#x1F5D1;</button>
          </div>
        `).join('');
      } catch {
        historyEl.innerHTML = '<p class="empty">Erro ao carregar histórico.</p>';
      }
    }

    async function removeReceipt(id) {
      await fetch(`${API}/receipts/${id}`, { method: 'DELETE' });
      document.getElementById(`item-${id}`)?.remove();
      const historyEl = document.getElementById('history');
      if (!historyEl.children.length)
        historyEl.innerHTML = '<p class="empty">Nenhum recibo ainda.</p>';
    }

    function setLoading(on) {
      submitBtn.disabled = on;
      btnText.style.display = on ? 'none' : 'inline';
      spinner.style.display = on ? 'block' : 'none';
    }

    loadHistory();
  </script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def frontend():
    return _HTML
