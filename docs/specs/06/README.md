# SPECs do Bloco 6: Modelos de Decisão

O PRD (`plano.md`, versão 0.1 de 12/10/2026) diz o que o bloco é. Uma SPEC diz o que uma fatia entrega, com precisão para implementar e testar.

## Ordem de implementação

| Ordem | SPEC | Entrega | Status |
|---|---|---|---|
| 0 | [SPEC-00](SPEC-00-common.md) | `common/`, golden sets, replay, CI | concluída |
| 1 | [SPEC-05](SPEC-05-calibration-evaluation.md) | harness e gravação (todo módulo mede com ele) | concluída |
| 2 | [SPEC-01](SPEC-01-decision-fundamentals.md) | fundamentos | concluída |
| 3 | [SPEC-02](SPEC-02-choice-routing.md) | Choice | concluída |
| 4 | [SPEC-03](SPEC-03-noul-detection-verification.md) | Noul | concluída |
| 5 | [SPEC-04](SPEC-04-score-ranking.md) | Score | concluída |
| 6 | [SPEC-06](SPEC-06-final-project.md) | agente híbrido | concluída |
| 7 | [SPEC-07](SPEC-07-bonus.md) | bônus | concluída |

"Concluída" significa que todos os critérios de aceite passam em replay. As fixtures do Jev são sintéticas até alguém gravar com `TYPESAFE_API_KEY` (ver `06-decision-models/fixtures/README.md`).

## Formato

1. **Objetivo**: uma frase.
2. **Cobre do PRD**: seções e requisitos (RF-xx).
3. **Interfaces**: o que a SPEC expõe para as outras.
4. **Critérios de aceite**: verificáveis por teste ou comando.
5. **Fora**: o que não entra.

## Decisões tomadas na implementação

| Tema | PRD | Implementado | Por quê |
|---|---|---|---|
| Golden sets | em aberto (item 11.1) | um por tema (tickets, spam, rerank, verify, tool_calls) e o de vendas do workshop-jev | é a proposta do próprio PRD |
| Chave da fixture | `fixtures/<provider>/<id>.json` | `fixtures/<alvo>/<hash do estado e das perguntas>.json` | qualquer script reaproveita a gravação sem passar id; mudar a pergunta invalida a gravação |
| Modo | `DECISION_PROVIDER=replay` | `replay`, `live` ou `record` | o modo `record` é o que o `05_replay_record.py` usa |
| LLM de baseline gravado | GPT-5.6 Luna e Claude Haiku 4.5 | só Claude Haiku 4.5 | a conta OpenAI estava sem crédito na gravação |
| Escolha de tool (módulo 02) | agente do Bloco 3 | agente de vendas do workshop-jev | precisa de golden set rotulado; o exercício leva o padrão ao Bloco 3 |
| Python | 3.12+ | 3.13+ | é a versão do resto da trilha |
| Laya | 421M, ONNX int8 | checkpoint multilíngue (mmBERT-base, 322M), PyTorch em CPU | 421M é o checkpoint em inglês; o multilíngue é o que serve para pt-BR |
| Infra compartilhada | `common/` importado por todos os módulos | igual | exceção consciente à regra da trilha, restrita ao Bloco 6 |
