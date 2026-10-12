# Fixtures de replay

Cada arquivo é **uma requisição gravada**: `fixtures/<alvo>/<chave>.json`. A chave é o hash do estado e das perguntas no formato de fio (`common/decisions.py: request_key`). Mudou uma vírgula na instrução, mudou a chave, e a gravação antiga deixa de responder.

```json
{
  "key": "291d62ec5084066216f3",
  "target": "laya",
  "recorded_at": "2026-10-12",
  "synthetic": false,
  "origin": "laya-serve em http://127.0.0.1:8001, modelo multilingual",
  "request": {"state": {...}, "questions": {...}},
  "result": {"provider": "laya", "answers": {...}, "latency_ms": 91.2, "tokens_in": 108, "raw": {...}}
}
```

## O que há neste repositório

| Diretório | Origem | Como foi feito |
|---|---|---|
| `laya/` | **real** | `laya-serve` 0.4.6, checkpoint `convaiinnovations/laya-multilingual` (revisão `7b928d8`), CPU, 12/10/2026 |
| `llm-anthropic-claude-haiku-4-5-20251001/` | **real** | API da Anthropic via `init_chat_model`, 12/10/2026 |
| `fc-anthropic-...` e `geracao-anthropic-...` | **real** | function calling (módulo 02) e geração do projeto final, mesma data |
| `jev/` | **sintética** | `gerar_jev_sintetico.py`, a partir dos rótulos do golden set |

### Por que o Jev é sintético

O Jev está em acesso antecipado e este repositório foi montado sem `TYPESAFE_API_KEY`. Sem fixture nenhuma, os scripts com o Jev não rodariam em replay. As fixtures sintéticas:

- partem dos **rótulos** do golden set, com ruído determinístico e taxas de acerto escolhidas no gerador (premissas, não resultados);
- copiam a resposta do LLM ou do Laya quando a pergunta não tem rótulo;
- usam a contagem de tokens do Laya como aproximação e latência sorteada;
- saem com `"synthetic": true`: o replay avisa no terminal e as tabelas marcam "(sintético)".

Os números do Jev em replay **não medem o Jev**. Para trocar pelas reais:

```bash
# com TYPESAFE_API_KEY no .env da raiz
python 05-calibration-evaluation/05_replay_record.py --alvos jev
```

Uma gravação real nunca é sobrescrita pelo gerador sintético.

## Regras

- `data/` e `fixtures/` só mudam com commit explícito: `data: regrava fixtures do <alvo>`.
- Grave com `05_replay_record.py`, nunca à mão.
- O GPT-5.6 Luna não tem gravação aqui. Grave com `DECISION_LLM=openai:gpt-5.6-luna` e depois use `DECISION_TARGETS` para incluí-lo.
