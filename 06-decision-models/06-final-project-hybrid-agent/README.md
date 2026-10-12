# 🏁 Módulo 6: Projeto Final, Agente Híbrido

> **Objetivo:** entregar um agente em LangGraph com decisões em modelo de decisão e geração em LLM, medido.
> **Pergunta-chave:** quanto custa cada decisão do seu agente, antes e depois?

---

## O agente

O agente de vendas do `workshop-jev`, reconstruído com decisões no lugar certo:

```
guardrail ─┬─ bloqueado ──────────────────────────────────────────► fim
           └─ triagem ─┬─ nenhuma tool / confiança baixa ─────────► fim (sem dado / humano)
                       └─ consulta → gerar (LLM) → verificar ─┬─ aprovada ─► fim
                                                              └─ reprovada ─► fim (resposta segura)
```

| Node | Tipo | Pergunta | Provider |
|---|---|---|---|
| `guardrail` | 3 Nouls | injection, dado sensível, fora de escopo | configurável |
| `triagem` | Choice | qual das 7 tools (ou nenhuma) | configurável |
| `consulta` | código | lê o resultado da tool | — |
| `gerar` | LLM | redige a resposta com os dados | `geracao` no config |
| `verificar` | 3 Nouls | responde? inventa número? segue a política? | configurável |

Numa pergunta respondida, são quatro chamadas de modelo: três decisões e uma geração.

## Arquivos

| Arquivo | O que tem |
|---|---|
| `config.yaml` | provider por node (`jev`, `laya`, `llm:<modelo>`), modelo de geração e limiares |
| `graph.py` | o `StateGraph`: state, nodes e arestas condicionais |
| `tools.py` | as tools; aqui leem resultados gravados em `../data/tool_results/` |
| `main.py` | uma pergunta, o lote sobre o golden set e a comparação entre providers |

## Como rodar

Imports flat, como no projeto final do Bloco 4: rode **de dentro da pasta**.

```bash
cd 06-decision-models/06-final-project-hybrid-agent
python main.py --lote                         # golden set de vendas com os providers do config.yaml
python main.py --comparar                     # o agente inteiro com cada provider, lado a lado
AGENTE_PROVIDER=laya python main.py --lote    # todas as decisões no Laya
DECISION_PROVIDER=live python main.py "Qual região vendeu mais em 2026?"
```

O relatório vai para `saida/relatorio.md`. Ele traz recall e taxa de falso positivo do guardrail, acurácia da triagem, % automatizado, latência p95 das decisões e da geração, custo por mil perguntas separado entre decisão e geração, e a concordância entre providers.

---

## 📦 Entregáveis

Use o seu próprio domínio e o seu golden set. O `workshop-jev` é a referência de implementação.

1. **Grafo** com guardrail, triagem, geração e verificação, com três providers configuráveis por node (Jev, Laya e um LLM).
2. **Golden set** do seu domínio com pelo menos 80 itens, incluindo adversariais, no formato do módulo 05.
3. **Harness:** Jev e Laya rodados no harness do módulo 05, mesmo que você escolha um só para o agente.
4. **Relatório** com custo, latência p95, acurácia e concordância, antes (tudo no LLM) e depois (decisões no modelo de decisão).
5. **Limiares justificados** com a curva do módulo 05: escolhidos numa metade do golden set, relatados na outra. Inclua o custo que você atribuiu a cada tipo de erro.

### Checklist de revisão

- [ ] O mesmo `DecisionSpec` alimenta todos os providers (nenhum prompt por modelo).
- [ ] Nenhum preço no código: tudo em `pricing.yaml`, com data e fonte.
- [ ] Roda em replay sem chave (`DECISION_PROVIDER=replay`).
- [ ] Fixtures sintéticas, se houver, aparecem marcadas no relatório.
- [ ] Rotas FastAPI, se houver, chamam SDKs síncronos dentro de `asyncio.to_thread`.

## ⏭️ Próximo Passo
Quer entender o que há por baixo e ter um modelo de decisão sob medida? **[Módulo 7 (bônus)](../07-bonus-build-your-own)**.
