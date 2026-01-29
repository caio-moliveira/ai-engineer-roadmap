# 🚢 Módulo 09: Deploy, Infra e Produção

> **Goal:** Levar valor para o usuário final.
> **Ferramentas:** `Docker`, `Terraform` (básico), `GCP/AWS`.

## 1. Docker para IA
Não é igual a web apps normais.
- **Tamanho:** Imagens com PyTorch/CUDA podem ter 5GB+. Use `:slim` versions.
- **Cache:** Otimize camadas para não baixar dependências a cada build.
- **Multistage Builds:** Build em uma imagem pesada, copie apenas o binário/env para a final.

## 2. Variáveis de Ambiente (12-Factor App)
Jamais comite `.env`.
- Em dev: `.env` local.
- Em prod: Ijection via Secret Manager (AWS Secrets Manager, Google Secret Manager).
- Pydantic Settings valida se as chaves existem no startup. Se faltar `OPENAI_API_KEY`, o app nem sobe (Fail Fast).

## 3. Estratégias de Deploy
- **Serverless (Cloud Run/Lambda):** Ótimo para a API (FastAPI) que chama a OpenAI. Escala a zero.
- **GPU Instances (EC2/GKE):** Necessário se você roda modelos locais (Ollama, vLLM). Não escala a zero fácil.

## 4. Custos e Latência
- **Streaming:** O usuário não pode esperar 15s por uma resposta. Implemente Server-Sent Events (SSE).
- **Rate Limiting:** Proteja sua carteira. Não deixe um usuário estourar sua cota da OpenAI.

## 🏁 Conclusão do Bloco 1
Parabéns! Você agora tem a **base de engenharia** que 90% dos "criadores de prompts" não têm.
Você sabe construir, testar e operar.

**Próxima Etapa:** Construir um sistema RAG real, do zero.
Nos vemos no **Bloco 2: Sistemas RAG**.
