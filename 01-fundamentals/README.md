# 🏗️ Bloco 1: Fundamentos Reais

> **Objetivo:** Estabelecer o padrão profissional.  
> **Status:** Obrigatório.

## 🛑 Pare. Leia isto.
Este não é um curso de "Python para Iniciantes".
Este não é um curso de "Como usar o Git".
Assumimos que você sabe codar.

Aqui, vamos alinhar o que significa "Codar para Sistemas de IA".
Sistemas de IA são:
1.  **Probabilísticos:** O código deve lidar com falhas e incertezas.
2.  **Assíncronos:** Modelos são lentos. Bloquear a main thread é crime.
3.  **Caros:** Cada caractere custa dinheiro. Eficiência é vital.

---

## 📚 Ementa do Módulo

### [Módulo 1: Profissão e Mercado](./01-ai-engineer-profession)
- **Papel:** O que diferencia um AI Engineer de um ML Engineer e de um Backend Dev.
- **Mercado:** O que as empresas realmente esperam (não é só fazer demos).
- **Mindset:** Produto > Modelo.

### [Módulo 2: Ambiente Profissional Moderno](./02-python-environment)
- **Ferramentas:** `uv` (o novo padrão), `pyproject.toml`.
- **Reproducibilidade:** Por que `pip freeze` não é suficiente.
- **Docker:** Multi-stage builds para containers leves.

### [Módulo 3: Git & Workflow Profissional](./03-git-workflow)
- **Padrão:** Conventional Commits.
- **CI/CD:** GitHub Actions para validar prompts e código (não só código).
- **Branch Strategy:** Feature flags vs Long-lived branches.

### [Módulo 4: Python para Engenheiros de IA](./04-python-for-ai)
- **Async/Await:** Obrigatório para LLMs.
- **Typing:** Pydantic e Type Hints rigorosos.
- **Generators:** Streaming de tokens (Server-Sent Events).
- **Resiliência:** `tenacity` para retries inteligentes.

### [Módulo 5: FastAPI Foundations](./05-fastapi)
- **Por que FastAPI:** O padrão industrial para servir ML.
- **Async:** Tratando 1000 requests simultâneos.
- **Dependency Injection:** Gerenciando conexões de banco e clientes OpenAI.

### [Módulo 6: Pydantic v2](./06-pydantic-v2)
- **Schema First:** Definindo a estrutura antes do prompt.
- **Validação:** Garantindo que o LLM não quebre seu frontend.
- **Field Validators:** Regras de negócio dentro do schema.

### [Módulo 7: Mentalidade de Engenharia](./07-engineering-mindset)
- **Sistemas:** Pensar em grafos, não em scripts.
- **Observabilidade:** Se você não loga, não sabe o que aconteceu.
- **Custo:** Token counting e orçamento.

---

## 🧠 Mudanças Mentais Necessárias
- **De Script para Sistema:** Seu notebook Jupyter não é produção. Ponto final.
- **De Otimista para Defensivo:** A API da OpenAI vai cair. O modelo vai alucinar. Seu código deve sobreviver.

## 🚀 Como começar
Vá para **[Módulo 1: Profissão e Mercado](./01-ai-engineer-profession)**.
