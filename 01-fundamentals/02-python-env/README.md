# 🐍 Module 2: Professional Python Environment

> **Goal:** Set up a reproducible, production-grade environment.  
> **Prerequisites:** A terminal and a dream.

## 1. The "Works on My Machine" Problem
In 2024/2025, if you use `pip install` directly into your global environment, you are wrong.
Python dependency management is notoriously difficult. If you don't isolate projects, you will break your OS tools.

### The Old Way (Deprecated)
- `pip install -r requirements.txt` (Slow, no locking, breaks easily).
- `virtualenv venv` (Manual).
- `conda` (Heavy, academic, license issues for enterprise).

### The New Standard: `uv`
Built by the creators of Ruff (Astral). It is written in Rust and is 10-100x faster than pip.
It replaces: `pip`, `pip-tools`, `poetry`, `pyenv`, and `virtualenv`.

## 2. Setup Guide (Follow This)

### Step 1: Install `uv`
Mac/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Initialize a Project
```bash
# Create a new project
uv init my-ai-agent
cd my-ai-agent

# Create a virtual environment (automatically managed)
uv venv
```

### Step 3: Add Dependencies
```bash
# Adds to pyproject.toml AND installs to .venv
uv add fastapi pydantic uvicorn python-dotenv openai
```

### Step 4: Run
```bash
uv run main.py
```

## 3. `pyproject.toml` Explained
This is the single source of truth.

```toml
[project]
name = "my-ai-agent"
version = "0.1.0"
description = "A production AI agent"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110.0",
    "pydantic>=2.7.0",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.3.0",
    "pytest>=8.0.0",
]
```

## 4. Docker for AI Engineers (The Final Boss)
Eventually, this must run on the cloud.
We use a **Multi-Stage Build** to keep images small.

```dockerfile
# BATTERIES-INCLUDED AI IMAGE
FROM python:3.12-slim-bookworm as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies strictly
RUN uv sync --frozen --no-install-project --no-dev

# ---------------------------------------
# RUNNER IMAGE
FROM python:3.12-slim-bookworm
WORKDIR /app

# Copy the environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure we use the virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Copy code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧠 Mental Model: "Immutable Artifacts"
Your goal is to create a Docker Image that is **Immutable**.
- Once built, it never changes.
- Configuration is injected via Environment Variables (`OPENAI_API_KEY`), not hardcoded.

## ⚠️ Common Mistakes
- **Committing `.venv`**: Never do this. Add it to `.gitignore`.
- **Using `requirements.txt` without locking**: Versions change. Your app will break. Use `uv.lock`.
- **Root installation**: Never runs `pip install` as root in Docker. It's a security risk.

## ⏭️ Next Step
Now that your environment is clean, let's look at how to manage code changes.
Go to **[Module 3: Git & Professional Workflow](../03-git-workflow)**.
