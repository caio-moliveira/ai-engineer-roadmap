# 🦙 Módulo 3: Ollama (Prototipagem Local Rápida)

> **Goal:** DX (Developer Experience) perfeita.  
> **Status:** O "Docker" dos LLMs.

## 1. Por que Ollama?
Antes do Ollama: Configurar Python, Cuda, Torch, compilar llama.cpp... (4 horas).
Com Ollama:
```bash
ollama run llama3
```
(5 minutos).

## 2. Quando usar?
- **Desenvolvimento Local:** Testar prompts sem gastar $ API.
- **Air-gapped demos:** Mostrar IA em um laptop sem internet.
- **CI/CD:** Rodar testes de integração leves.

## 3. Quando NÃO usar?
**Produção de Alta Escala.**
Ollama foca em *usabilidade*, não em *throughput* máximo (embora esteja melhorando).
Para servir 10.000 usuários, você quer controle total sobre o Batching, o que o **vLLM** oferece melhor.

## 4. Workflow de Engenharia
1.  **Dev (MacBook):** Desenvolve usando Ollama (`llama3:8b`).
2.  **Teste:** Valida prompts e tools.
3.  **Staging/Prod (GPU Server):** Deploy usando contêiner Docker oficial do vLLM apontando para o mesmo modelo.

## 🧠 Mental Model: "SQLite vs PostgreSQL"
- **Ollama é SQLite:** Fácil, arquivo único, ótimo para dev e apps leves.
- **vLLM é PostgreSQL:** Robusto, configurável, feito para aguentar o tranco de uma empresa inteira.

## ⏭️ Próximo Passo
Vamos falar do PostgreSQL dos LLMs.
Vá para **[Módulo 4: vLLM](../04-vllm)**.
