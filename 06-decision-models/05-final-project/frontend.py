"""Frontend para a aula: exemplos do que o agente faz e o resultado de cada um, em linguagem simples.

Uma página HTML servida pela própria API (mesmo padrão do projeto final do bloco de OCR).
À esquerda, os exemplos e o resumo da sessão; à direita, a resposta, a linha do tempo das decisões
e a comparação entre o que o Jev e o LLM gastaram. Os detalhes de cada decisão (perguntas e
probabilidades) ficam recolhidos em "ver perguntas ao Jev".
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Agente de Vendas · Jev decide, LLM escreve</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #f5f5f7; --card: #fff; --text: #1d1d1f; --muted: #6e6e73; --border: #e3e3e8;
      --accent: #0071e3; --ok: #15803d; --ok-bg: #f0fdf4; --warn: #b45309; --warn-bg: #fffbeb;
      --bad: #b91c1c; --bad-bg: #fef2f2; --jev: #7c3aed; --jev-bg: #f5f3ff; --llm: #0369a1; --llm-bg: #f0f9ff;
      --radius: 14px; --shadow: 0 2px 16px rgba(0,0,0,.07);
    }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg);
           color: var(--text); padding: 24px 16px 48px; line-height: 1.45; }
    header { max-width: 1200px; margin: 0 auto 20px; }
    h1 { font-size: 1.45rem; }
    .lead { color: var(--muted); margin-top: 4px; font-size: .95rem; }
    .lead b.jev { color: var(--jev); } .lead b.llm { color: var(--llm); }
    main { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 360px 1fr; gap: 18px; align-items: start; }
    @media (max-width: 900px) { main { grid-template-columns: 1fr; } }
    .card { background: var(--card); border-radius: var(--radius); box-shadow: var(--shadow); padding: 18px; }
    .col { display: flex; flex-direction: column; gap: 18px; }
    h2 { font-size: 1rem; margin-bottom: 12px; }

    /* Exemplos */
    .exemplo { width: 100%; text-align: left; background: #fff; border: 1px solid var(--border); border-radius: 12px;
               padding: 11px 13px; margin-bottom: 8px; cursor: pointer; font: inherit; transition: border-color .15s, background .15s; }
    .exemplo:hover { border-color: var(--accent); background: #f7fbff; }
    .exemplo.ativo { border-color: var(--accent); background: #eef6ff; }
    .exemplo b { display: block; font-size: .92rem; }
    .exemplo span { display: block; font-size: .8rem; color: var(--muted); margin-top: 2px; }
    .exemplo i { display: block; font-size: .78rem; color: var(--text); margin-top: 6px; font-style: normal; opacity: .75; }
    form { display: flex; gap: 8px; margin-top: 6px; }
    input[type=text] { flex: 1; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--border); font: inherit; font-size: .9rem; }
    button.primary { border: none; border-radius: 10px; padding: 0 16px; font-weight: 600; background: var(--accent); color: #fff; cursor: pointer; }
    button:disabled { opacity: .5; cursor: not-allowed; }
    .dica { font-size: .78rem; color: var(--warn); margin-top: 6px; display: none; }

    /* Resumo */
    .kpi { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 9px 0; border-top: 1px solid var(--border); }
    .kpi:first-of-type { border-top: none; }
    .kpi span { font-size: .85rem; color: var(--muted); }
    .kpi b { font-size: 1.1rem; white-space: nowrap; }
    .kpi b.ok { color: var(--ok); }

    /* Resultado */
    .vazio { color: var(--muted); text-align: center; padding: 60px 20px; }
    .pergunta { font-size: 1.05rem; font-weight: 600; }
    .status { display: inline-block; margin-top: 8px; padding: 4px 10px; border-radius: 999px; font-size: .78rem; font-weight: 600; }
    .status.ok { background: var(--ok-bg); color: var(--ok); }
    .status.warn { background: var(--warn-bg); color: var(--warn); }
    .status.bad { background: var(--bad-bg); color: var(--bad); }
    .resposta { margin-top: 14px; font-size: .93rem; }
    .resposta p { margin: 6px 0; }
    .resposta h4 { margin: 12px 0 4px; font-size: .95rem; }
    .resposta ul { margin: 4px 0 4px 20px; }
    .resposta table { border-collapse: collapse; margin: 8px 0; font-size: .82rem; width: 100%; }
    .resposta th, .resposta td { border: 1px solid var(--border); padding: 4px 7px; text-align: left; }
    .resposta th { background: #f7f7f9; }
    .aviso { margin-top: 12px; background: var(--warn-bg); border: 1px solid #fcd34d; color: var(--warn); border-radius: 10px; padding: 8px 10px; font-size: .85rem; }
    .carregando { color: var(--muted); padding: 40px 0; text-align: center; }

    .aprovacao { margin-top: 14px; background: var(--warn-bg); border: 1px solid #fcd34d; border-radius: 12px; padding: 14px; }
    .aprovacao p { font-size: .9rem; }
    .aprovacao .botoes { display: flex; gap: 8px; margin-top: 10px; }
    .aprovacao button { border: none; border-radius: 9px; padding: 8px 18px; font-weight: 600; color: #fff; cursor: pointer; }
    .aprovacao .sim { background: var(--ok); } .aprovacao .nao { background: var(--bad); }

    /* Linha do tempo */
    .passos { list-style: none; }
    .passo { display: grid; grid-template-columns: 30px 1fr; gap: 10px; padding: 8px 0; }
    .icone { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; font-size: .95rem; }
    .passo.ok .icone { background: var(--ok-bg); } .passo.warn .icone { background: var(--warn-bg); }
    .passo.bad .icone { background: var(--bad-bg); } .passo.neutro .icone { background: #f2f2f5; }
    .passo .quem { font-size: .75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; font-weight: 600; }
    .passo .quem em { font-style: normal; text-transform: none; letter-spacing: 0; font-weight: 400; }
    .passo .texto { font-size: .9rem; }
    .passo.bad .texto b { color: var(--bad); } .passo.warn .texto b { color: var(--warn); } .passo.ok .texto b { color: var(--ok); }
    details { margin-top: 4px; }
    summary { font-size: .75rem; color: var(--accent); cursor: pointer; }
    details table { margin-top: 6px; border-collapse: collapse; font-size: .78rem; width: 100%; max-width: 460px; }
    details td { padding: 3px 6px; border-top: 1px solid #f0f0f2; }
    details td.tipo { color: var(--muted); width: 52px; }
    details td.prob { text-align: right; width: 48px; font-variant-numeric: tabular-nums; }
    .legenda { font-size: .74rem; color: var(--muted); margin-top: 4px; max-width: 460px; }

    /* Comparação Jev × LLM */
    .comparacao { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .lado { border-radius: 12px; padding: 12px 14px; }
    .lado.jev { background: var(--jev-bg); } .lado.llm { background: var(--llm-bg); }
    .lado h3 { font-size: .85rem; margin-bottom: 6px; }
    .lado.jev h3 { color: var(--jev); } .lado.llm h3 { color: var(--llm); }
    .lado .num { font-size: 1.25rem; font-weight: 700; }
    .lado .det { font-size: .8rem; color: var(--muted); }
    .barra { height: 8px; background: rgba(0,0,0,.06); border-radius: 4px; margin: 8px 0 4px; overflow: hidden; }
    .barra div { height: 100%; border-radius: 4px; }
    .jev .barra div { background: var(--jev); } .llm .barra div { background: var(--llm); }
  </style>
</head>
<body>
  <header>
    <h1>Agente de Operações de Vendas</h1>
    <p class="lead">Quem decide é o <b class="jev">Jev</b>: para onde vai a pergunta, se uma ação pode rodar, se a resposta está boa.
      O <b class="llm">LLM</b> só escreve. Escolha um exemplo e veja cada decisão.</p>
  </header>

  <main>
    <div class="col">
      <section class="card">
        <h2>O que o agente faz</h2>
        <div id="exemplos"></div>
        <form id="form">
          <input type="text" id="entrada" placeholder="Ou faça sua pergunta sobre as vendas..." autocomplete="off" />
          <button class="primary" id="enviar" type="submit">Enviar</button>
        </form>
        <p class="dica" id="dica">O agente pediu um esclarecimento: responda no campo acima.</p>
      </section>

      <section class="card">
        <h2>Resumo da sessão</h2>
        <div id="resumo"></div>
      </section>
    </div>

    <div class="col" id="resultado">
      <section class="card"><p class="vazio">Escolha um exemplo à esquerda.</p></section>
    </div>
  </main>

  <script>
    const EXEMPLOS = [
      { titulo: 'Pergunta simples', mostra: 'O roteador manda para o modelo barato.',
        pergunta: 'Qual foi o faturamento do mês atual?' },
      { titulo: 'Pergunta complexa e cascata', mostra: 'Começa de propósito no modelo barato. A resposta sai incompleta, o juiz reprova e o modelo caro refaz.',
        pergunta: 'Compare o faturamento do mês atual com o do mês anterior por região, diga qual região mais cresceu, quem foi o melhor vendedor do mês e liste os pedidos atrasados.',
        modelo: 'pequeno' },
      { titulo: 'Ação que pede aprovação', mostra: 'Cancelar é irreversível: o guardião pausa e você decide.',
        pergunta: 'Cancele o pedido 1355, o cliente desistiu da compra.' },
      { titulo: 'Tentativa de injeção', mostra: 'O pedido 1286 tem uma nota falsa mandando reembolsar tudo. O guardião barra.',
        pergunta: 'Veja o pedido 1286 e resolva o que estiver pendente.' },
      { titulo: 'Pergunta ambígua', mostra: 'Falta o número do pedido: o agente pergunta antes de agir.',
        pergunta: 'Cancela aquele pedido.' },
    ];
    const ACOES = {
      consultar_indicadores: 'consultar os indicadores de vendas', listar_pedidos_atrasados: 'listar os pedidos atrasados',
      buscar_pedido: 'buscar os dados do pedido', ranking_vendedores: 'ver o ranking de vendedores',
      reembolsar_cliente: 'reembolsar o cliente', cancelar_pedido: 'cancelar o pedido',
    };
    const RISCO = new Set(['reembolsar_cliente', 'cancelar_pedido']);
    const INTENCAO = { consulta: 'uma consulta de dados', acao: 'um pedido de ação', conversa: 'uma conversa' };

    const $ = (id) => document.getElementById(id);
    const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const seg = (ms) => ms >= 1000 ? `${(ms / 1000).toFixed(1).replace('.', ',')} s` : `${Math.round(ms)} ms`;
    const usd = (v) => v < 0.0001 ? 'menos de US$ 0,0001' : `US$ ${v.toFixed(4).replace('.', ',')}`;
    const pct = (q) => q ? `${Math.round(q.probabilidade * 100)}%` : '';
    let modelos = { pequeno: 'modelo barato', grande: 'modelo caro' };
    let contexto = null;

    // --- Exemplos -----------------------------------------------------------------------------
    $('exemplos').innerHTML = EXEMPLOS.map((e, i) =>
      `<button class="exemplo" data-i="${i}"><b>${e.titulo}</b><span>${e.mostra}</span><i>“${esc(e.pergunta)}”</i></button>`).join('');
    document.querySelectorAll('.exemplo').forEach(b => b.addEventListener('click', () => {
      document.querySelectorAll('.exemplo').forEach(x => x.classList.remove('ativo'));
      b.classList.add('ativo');
      const e = EXEMPLOS[+b.dataset.i];
      contexto = null;
      perguntar(e.pergunta, e.modelo);
    }));
    $('form').addEventListener('submit', (ev) => {
      ev.preventDefault();
      const texto = $('entrada').value.trim();
      if (!texto) return;
      $('entrada').value = '';
      document.querySelectorAll('.exemplo').forEach(x => x.classList.remove('ativo'));
      perguntar(texto);
    });

    // --- Chamadas à API -----------------------------------------------------------------------
    async function post(url, body) {
      const res = await fetch(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(typeof err.detail === 'string' ? err.detail : `Erro ${res.status}`);
      }
      return res.json();
    }

    async function perguntar(pergunta, modelo) {
      const original = contexto ? `${contexto} (esclarecimento: ${pergunta})` : pergunta;
      $('resultado').innerHTML = `<section class="card"><p class="pergunta">${esc(original)}</p>
        <p class="carregando">O agente está trabalhando…</p></section>`;
      bloquear(true);
      try {
        const data = await post('/agente/perguntas', { pergunta, modelo_inicial: modelo || 'auto', contexto });
        contexto = data.status === 'esclarecimento' ? pergunta : null;
        $('dica').style.display = contexto ? 'block' : 'none';
        mostrar(data, original);
      } catch (e) {
        $('resultado').innerHTML = `<section class="card"><p class="pergunta">${esc(original)}</p><div class="aviso">Erro: ${esc(e.message)}</div></section>`;
      } finally {
        bloquear(false);
      }
    }

    function bloquear(sim) {
      $('enviar').disabled = sim;
      document.querySelectorAll('.exemplo').forEach(b => b.disabled = sim);
    }

    async function decidir(data, original, aprovado) {
      document.querySelector('.aprovacao .botoes').innerHTML = `<i>${aprovado ? 'Aprovada' : 'Recusada'}. O agente continua…</i>`;
      bloquear(true);
      try { mostrar(await post(`/agente/perguntas/${data.thread_id}/aprovacao`, { aprovado }), original); }
      catch (e) { document.querySelector('#resultado .card').insertAdjacentHTML('beforeend', `<div class="aviso">Erro: ${esc(e.message)}</div>`); }
      finally { bloquear(false); }
    }

    // --- Resultado ----------------------------------------------------------------------------
    function mostrar(data, original) {
      const [rotulo, tom] = status(data);
      let html = `<section class="card"><p class="pergunta">${esc(original)}</p><span class="status ${tom}">${rotulo}</span>`;
      if (data.status === 'aguardando_aprovacao') {
        const p = data.aprovacao_pendente, a = p.argumentos;
        html += `<div class="aprovacao"><p><b>O guardião pausou o agente.</b> Ele quer <b>${esc(ACOES[p.acao] || p.acao)}</b>` +
          (a.pedido_id ? ` do pedido ${esc(a.pedido_id)}` : '') + (a.valor ? `, no valor de R$ ${esc(a.valor)}` : '') + '.' +
          (a.motivo ? ` Motivo dado pelo agente: “${esc(a.motivo)}”.` : '') +
          `</p><div class="botoes"><button class="sim">Aprovar</button><button class="nao">Recusar</button></div></div>`;
      } else {
        html += `<div class="resposta">${markdown(data.resposta)}</div>`;
        if (data.aviso) html += `<div class="aviso">${esc(data.aviso)}</div>`;
      }
      html += `</section>`;
      html += `<section class="card"><h2>Como o agente chegou aqui</h2><ol class="passos">${data.trilha.map(passo).join('')}</ol></section>`;
      html += comparacao(data);
      $('resultado').innerHTML = html;

      if (data.status === 'aguardando_aprovacao') {
        document.querySelector('.aprovacao .sim').onclick = () => decidir(data, original, true);
        document.querySelector('.aprovacao .nao').onclick = () => decidir(data, original, false);
      }
      carregarResumo();
    }

    function status(data) {
      if (data.status === 'aguardando_aprovacao') return ['Aguardando sua aprovação', 'warn'];
      if (data.status === 'esclarecimento') return ['Pediu um esclarecimento', 'warn'];
      if (data.passos.some(p => p.status === 'bloqueada')) return ['Ação bloqueada pelo guardião', 'bad'];
      if (data.passos.some(p => p.status === 'recusada')) return ['Ação recusada por você', 'warn'];
      if (data.aviso) return ['Entregue com aviso de baixa confiança', 'bad'];
      if (data.tentativas > 1) return ['Refeita no modelo caro depois de o juiz reprovar', 'warn'];
      const grande = data.chamadas_llm.some(c => c.tamanho === 'grande');
      return [grande ? 'Respondida pelo modelo caro' : 'Respondida pelo modelo barato', 'ok'];
    }

    // Uma decisão da trilha em linguagem simples, com as perguntas ao Jev recolhidas.
    function passo(t) {
      const rota = t.decisao.split(':')[0].trim();
      const q = (nome) => t.perguntas.find(x => x.nome === nome);
      let icone = '•', tom = 'neutro', quem = '', texto = '';

      if (t.no === 'roteador' && t.tipo === 'politica') {
        icone = '↻'; tom = 'warn'; quem = 'Cascata';
        texto = `Segunda tentativa, agora no <b>${modelos.grande}</b>.`;
      } else if (t.no === 'roteador') {
        icone = '🧭'; quem = 'Roteador';
        if (rota === 'esclarecer') {
          tom = 'warn';
          texto = `A pergunta está <b>ambígua</b> (${pct(q('ambigua'))}). O agente pede um esclarecimento em vez de chutar.`;
        } else {
          const c = parseFloat(q('complexidade').resposta);
          const nivel = c < 0.67 ? 'simples' : c < 1.34 ? 'média' : 'complexa';
          const grande = /modelo grande/.test(t.decisao);
          const forcado = /forçado/.test(t.decisao);
          tom = 'ok';
          texto = `Entendeu como ${INTENCAO[q('intencao').resposta] || q('intencao').resposta}, de complexidade ${nivel}. ` +
            (forcado ? `Neste exemplo, começa de propósito no <b>${grande ? modelos.grande : modelos.pequeno}</b>.`
                     : `Vai para o <b>${grande ? modelos.grande : modelos.pequeno}</b>.`);
        }
      } else if (t.no === 'guardiao') {
        icone = '🛡️'; quem = 'Guardião';
        const acao = ACOES[t.acao] || t.acao;
        if (rota === 'bloquear') {
          tom = 'bad';
          texto = /injetada/.test(t.decisao)
            ? `<b>Bloqueou</b>: ${acao}. A ordem veio de um texto nos dados, não de você (injeção, ${pct(q('injecao'))}).`
            : `<b>Bloqueou</b>: ${acao}.`;
        } else if (rota === 'aprovacao') {
          tom = 'warn';
          const porque = /limite/.test(t.decisao) ? 'o valor passa do limite de reembolso automático'
            : /incerto/.test(t.decisao) ? 'ficou em dúvida sobre a ação' : 'é uma ação irreversível';
          texto = `<b>Pausou</b> antes de ${acao} e pediu aprovação humana: ${porque}.`;
        } else if (RISCO.has(t.acao)) {
          tom = 'ok'; texto = `<b>Liberou</b>: ${acao}. Você pediu, e não há sinal de injeção.`;
        } else {
          texto = `Liberou a leitura: ${acao}.`;
        }
      } else if (t.no === 'aprovacao') {
        icone = '🙋'; quem = 'Você';
        const ok = /aprovada/.test(t.decisao);
        tom = ok ? 'ok' : 'bad';
        texto = ok ? '<b>Aprovou</b> a ação.' : '<b>Recusou</b> a ação. O agente não vai tentar de novo.';
      } else if (t.no === 'juiz') {
        icone = '⚖️'; quem = 'Juiz';
        if (rota === 'entregar') { tom = 'ok'; texto = '<b>Aprovou</b> a resposta: completa e sustentada pelos dados.'; }
        else if (rota === 'refazer') {
          tom = 'warn';
          const falta = parseFloat(q('completude').resposta) < 1.4 ? 'incompleta' : 'com afirmações sem base nos dados';
          texto = `<b>Reprovou</b> a resposta: ${falta}. Volta e refaz.`;
        } else { tom = 'bad'; texto = '<b>Não aprovou</b> e acabaram as tentativas: a resposta sai com um aviso.'; }
      }

      const meta = t.tipo === 'jev' ? ` <em>· Jev · ${seg(t.latencia_ms)}</em>` : ' <em>· sem chamar o Jev</em>';
      return `<li class="passo ${tom}"><div class="icone">${icone}</div><div>
        <div class="quem">${quem}${meta}</div><div class="texto">${texto}</div>${detalhes(t)}</div></li>`;
    }

    function detalhes(t) {
      if (!t.perguntas.length) return '';
      const linhas = t.perguntas.map(q =>
        `<tr><td class="tipo">${q.classe}</td><td>${esc(q.nome)}</td><td><b>${esc(q.resposta)}</b></td><td class="prob">${pct(q)}</td></tr>`).join('');
      return `<details><summary>ver perguntas ao Jev</summary><table>${linhas}</table>
        <p class="legenda">Choice escolhe uma opção, Noul responde sim ou não e Score dá uma nota.
        O % é a probabilidade da resposta mostrada (no Score, a confiança na nota). A decisão final aplica os limiares de policy.py.</p></details>`;
    }

    function comparacao(data) {
      const jev = data.trilha.filter(t => t.tipo === 'jev');
      const llm = data.chamadas_llm;
      const tJev = jev.reduce((s, t) => s + t.latencia_ms, 0);
      const tLlm = llm.reduce((s, c) => s + c.latencia_ms, 0);
      const maior = Math.max(tJev, tLlm, 1);
      const usados = [...new Set(llm.map(c => c.tamanho))].map(t => modelos[t]).join(' e ') || 'nenhum modelo';
      return `<section class="card"><h2>Quem fez o quê</h2><div class="comparacao">
        <div class="lado jev"><h3>Jev · decidiu</h3><div class="num">${jev.length} ${jev.length === 1 ? 'decisão' : 'decisões'}</div>
          <div class="barra"><div style="width:${(100 * tJev / maior).toFixed(1)}%"></div></div>
          <div class="det">${seg(tJev)} no total · sem gerar texto</div></div>
        <div class="lado llm"><h3>LLM · escreveu</h3><div class="num">${llm.length} ${llm.length === 1 ? 'chamada' : 'chamadas'}</div>
          <div class="barra"><div style="width:${(100 * tLlm / maior).toFixed(1)}%"></div></div>
          <div class="det">${seg(tLlm)} no total · ${usd(data.totais.llm_custo_usd)} · ${usados}</div></div>
      </div></section>`;
    }

    // Markdown mínimo para a resposta do LLM: negrito, títulos, listas e tabelas.
    function markdown(src) {
      const linhas = esc(src).split('\\n');
      const inline = (s) => s.replace(/\\*\\*(.+?)\\*\\*/g, '<b>$1</b>');
      const lista = /^\\s*([-*]|\\d+\\.)\\s/;
      let html = '', i = 0;
      while (i < linhas.length) {
        const l = linhas[i];
        if (/^\\s*\\|/.test(l)) {
          const rows = [];
          while (i < linhas.length && /^\\s*\\|/.test(linhas[i])) rows.push(linhas[i++]);
          const corpo = rows.filter(r => !/^\\s*\\|[\\s\\-:|]+\\|\\s*$/.test(r));
          const celulas = (r) => r.trim().replace(/^\\||\\|$/g, '').split('|').map(c => inline(c.trim()));
          html += '<table>' + corpo.map((r, k) =>
            `<tr>${celulas(r).map(c => k === 0 ? `<th>${c}</th>` : `<td>${c}</td>`).join('')}</tr>`).join('') + '</table>';
        } else if (/^#{1,4}\\s/.test(l)) {
          html += `<h4>${inline(l.replace(/^#+\\s/, ''))}</h4>`; i++;
        } else if (lista.test(l)) {
          const itens = [];
          while (i < linhas.length && lista.test(linhas[i])) itens.push(linhas[i++].replace(lista, ''));
          html += '<ul>' + itens.map(x => `<li>${inline(x)}</li>`).join('') + '</ul>';
        } else {
          if (l.trim()) html += `<p>${inline(l)}</p>`;
          i++;
        }
      }
      return html;
    }

    // --- Resumo da sessão ---------------------------------------------------------------------
    async function carregarResumo() {
      const r = await (await fetch('/agente/resumo')).json();
      $('resumo').innerHTML = `
        <div class="kpi"><span>Resolvidas só com o modelo barato</span><b>${r.resolvidas_pelo_pequeno} de ${r.perguntas}</b></div>
        <div class="kpi"><span>Economia contra usar sempre o modelo caro</span><b class="ok">${String(r.economia_pct).replace('.', ',')}%</b></div>
        <div class="kpi"><span>Ações barradas pelo guardião</span><b>${r.bloqueios}</b></div>`;
    }

    async function carregarConfig() {
      const c = await (await fetch('/agente/config')).json();
      const nome = (m) => m.split(':').pop();
      modelos = { pequeno: `modelo barato (${nome(c.llm_small)})`, grande: `modelo caro (${nome(c.llm_large)})` };
    }

    carregarConfig();
    carregarResumo();
  </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return _HTML
