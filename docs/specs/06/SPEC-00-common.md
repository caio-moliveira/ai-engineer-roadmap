# SPEC-00: infraestrutura compartilhada (`common/`)

Status: concluída

## Objetivo
Um `DecisionClient` com a mesma interface para Jev, Laya, LLM e replay, mais métricas, golden sets e preços, para que todo módulo meça do mesmo jeito.

## Cobre do PRD
Seção 6; RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07.

## Interfaces
- `common.decisions`: `DecisionSpec`, `Answer`, `DecisionResult`, `DecisionClient`, `request_key`, `answers_from_systemone`.
- `common.providers.get_client(alvo)`: `jev`, `jev-langchain`, `laya` e `llm:<provedor:modelo>`. O modo vem de `DECISION_PROVIDER`.
- `common.providers.replay`: `ReplayClient`, `RecordingClient`, `replay_transport` (httpx2) e `cached_call`.
- `common.metrics`: acurácia, F1 macro, Brier, ECE, faixas de confiabilidade, kappa, percentis, curva de automação, recall@k e nDCG.
- `common.golden.load(nome)`: itens com `state`, `labels` e `tags`.
- `common.specs`: as perguntas dos golden sets, que são o contrato de nomes com os rótulos.
- `common/pricing.yaml`: preço por modelo, com data e fonte.
- `docker-compose.yaml` da raiz: serviço `laya`, perfil `decision`, porta 8001.

## Critérios de aceite
- `uv run pytest 06-decision-models/tests -q` passa sem chave e sem rede.
- O SDK e o `langchain-typesafe` produzem a mesma chave de fixture (teste `test_mesma_chave_pelo_sdk_e_pelo_langchain`).
- Um modelo sem preço levanta `PricingMissingError`.
- `docker compose --profile decision up laya` responde em `/v1/systemone`.

## Fora
Cache semântico, retries próprios (o SDK já faz) e streaming.
