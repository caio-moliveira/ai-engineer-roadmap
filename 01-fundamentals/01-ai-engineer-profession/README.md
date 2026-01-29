# 🧑‍💻 O Framework da Profissão de AI Engineer

> **Definição:** Um AI Engineer é um Engenheiro de Software especializado em orquestrar modelos de IA não-determinísticos para construir sistemas confiáveis em produção.

Ao contrário do Cientista de Dados (que treina modelos) ou do Engenheiro de ML (que coloca modelos em produção), o foco do AI Engineer é **produto** e **sistema**. Se você domina os três pilares abaixo, você está pronto para operar em nível sênior no mercado.

---

## 🏛️ Pilar 1: Fluência em Foundation Models
Não se trata de saber como o Transformer funciona matematicamente, mas de saber como o modelo **"pensa"** e como controlá-lo. É a capacidade de tratar LLMs como componentes de software.

### O que você deve dominar:
- **Prompt Engineering Profissional:** Vai muito além de "aja como um especialista". Envolve Chain-of-Thought, ReAct, e decomposição de problemas complexos.
- **Saídas Estruturadas (Structured Outputs):** A habilidade de forçar o modelo a retornar JSON/Schemas rigorosos (Pydantic), transformando texto probabilístico em dados determinísticos.
- **Raciocínio e Decomposição:** Saber quando usar um modelo "rápido e burro" (ex: GPT-4o-mini) versus um modelo "lento e inteligente" (ex: Claude 3.5 Sonnet ou o1).
- **Trade-offs de Seleção:** Latência vs Custo vs Acurácia. Você escolhe o modelo certo para a tarefa certa.
- **Multimodalidade:** Orquestrar texto, áudio e vídeo no mesmo pipeline de raciocínio.
- **Fine-tuning vs Contexto:** Saber, conceitualmente, quando RAG resolve e quando você realmente precisa de LoRA/QLoRA para adaptar o comportamento do modelo.

> **Mindset:** "O modelo é meu kernel. Eu preciso saber como alocar memória (contexto), gerenciar processos (agentes) e tratar exceções (recusas)."

---

## 🏛️ Pilar 2: Arquitetura de Sistemas
Demos não sobrevivem ao mundo real. AI Engineers constroem sistemas que escalam, falham com elegância e custam pouco.

### O que você deve dominar:
- **Sistemas RAG Avançados:** Além da busca vetorial simples. Retromapeamento de consultas, reranking, hybrid search e chunking semântico.
- **Arquitetura Orientada a Eventos:** Pipelines assíncronos onde LLMs "ouvem" filas e disparam webhooks.
- **Orquestração de Agentes:** Criar loops de feedback onde o modelo usa ferramentas (API calls, SQL queries) para resolver problemas multi-etapa.
- **Observabilidade em IA:** Como debugar algo que não é determinístico? (Tracing, Evals, Logging de Tokens).
- **Caching & Otimização:** Cache semântico para reduzir custos e roteamento inteligente de queries.

> **Mindset:** "Incerteza é uma feature, não um bug. O sistema ao redor do LLM deve ser robusto o suficiente para lidar com alucinações e falhas."

---

## 🏛️ Pilar 3: Engenharia de Produção
No final do dia, você é um Engenheiro. Se o código é ruim, o produto é ruim. O hype de IA não perdoa engenharia amadora.

### O que você deve dominar:
- **Python de Classe Mundial:** Type hints, async/await, pydantic, generators, decorators. Código limpo e testável.
- **APIs & Backend:** Design de APIs RESTful (FastAPI), injeção de dependência e contratos claros.
- **Containerização & Cloud:** Dockerfiles otimizados (multi-stage), Kubernetes (básico) e geranciamento de segredos em nuvem (AWS/GCP).
- **DevOps para AI (LLMOps):** Versionamento de prompts como código, CI/CD que roda testes de avaliação (Evals) antes do deploy.
- **Infraestrutura:** Servir modelos locais (vLLM, Ollama) vs APIs gerenciadas, entendendo o impacto na latência e na conta do cloud provider.

> **Mindset:** "Se não está no Git, não existe. Se não tem teste, está quebrado. Se não tem log, não aconteceu."

---

## 🎯 Conclusão: A Identidade Profissional

O AI Engineer Moderno vive na interseção desses três mundos:
1.  Ele fala a língua dos **Modelos** (Pilar 1).
2.  Ele desenha a planta dos **Sistemas** (Pilar 2).
3.  Ele constroi com a solidez da **Engenharia** (Pilar 3).

Diferente do Backend Dev, ele entende a incerteza estatística.
Diferente do Data Scientist, ele entrega software de produção, não notebooks.

Este roadmap foi desenhado para te dar maestria nesses três pilares.
