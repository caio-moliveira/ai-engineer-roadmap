# 🐍 Módulo 2: Ambiente Profissional Python

> **Goal:** Nunca mais ouvir "funciona na minha máquina".  
> **Status:** Adeus pip freeze, olá uv.

## 1. O Novo Padrão: `uv`
Esqueça `pip`, `poetry`, `conda`.
O `uv` (escrito em Rust) é 100x mais rápido e substitui todos eles.

### Comandos Essenciais
```bash
# Criar venv e instalar python (tudo em um)
uv venv
uv pip install -r requirements.txt
```

## 2. `pyproject.toml`
O arquivo de configuração único.
Define dependências, versão do python, configs de linter (Ruff) e testes (Pytest).

## 3. Ambientes Reproduzíveis
Simplesmente instalar dependências não garante reprodução.
- **Lockfiles (`uv.lock`):** Garante que a versão da sub-dependência da sub-dependência seja exata.

## 4. Docker Multi-Stage Builds
Em produção, não queremos o compilador C++ ou o Git instalado. Queremos apenas o binário Python e as libs.

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
RUN pip install uv
COPY . .
RUN uv pip install --system -r requirements.txt

# Stage 2: Runtime (Tiny)
FROM python:3.11-slim-distroless
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app
CMD ["python", "main.py"]
```

## 🧠 Mental Model: "Contêiner é Imutável"
Seu ambiente local deve ser um espelho do ambiente de produção.
Se você rodar `uv sync`, deve ter certeza absoluta que o ambiente está idêntico ao do colega.

## ⏭️ Próximo Passo
Como colaboramos nesse código?
Vá para **[Módulo 3: Git & Workflow Profissional](../03-git-workflow)**.
