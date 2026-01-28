# 🤖 Módulo 1: Ecossistema Moderno de Modelos (2025+)

> **Goal:** Escolher a ferramenta certa para o trabalho.  
> **Status:** O mercado muda toda semana. Os princípios não.

## 1. O Grande Dilema: API vs Self-Hosted

| Critério | API (OpenAI/Anthropic) | Self-Hosted (Llama 3/Mistral) |
|:---|:---|:---|
| **Custo Inicial** | Zero. | Alto (GPUs ou Cloud). |
| **Custo em Escala** | Linear (Caro). | Fixo + Eletricidade (Mais barato em escala massiva). |
| **Privacidade** | Confiar no ToS do vendor. | Controle total (Air-gapped possível). |
| **Qualidade** | SOTA (State of the Art). | Ótimo, mas atrasado 6-12 meses do SOTA. |
| **Ops** | Zero. | Pesado (K8s, vLLM, Drivers). |

> **Regra de Ouro:** Comece com API. Mova para Self-Hosted apenas se o custo explodir (> $10k/mês) ou se a privacidade (HIPAA/GDPR rígido) exigir.

## 2. Model Routing Pattern
Não use GPT-4o para tudo. É queimar dinheiro.

1.  **O "Router" (Modelo Pequeno):** Recebe o request do usuário.
    - Classifica a complexidade: "Simples" (Oi/Tchau) ou "Complexo" (Resuma este contrato jurídico).
2.  **Caminho A (Rápido):** Llama-3-8B ou GPT-4o-mini.
3.  **Caminho B (Inteligente):** Claude 3.5 Sonnet ou GPT-4o.

## 3. Critérios de Seleção (2025)
- **Latência (TTFT):** Para chatbots, o usuário precisa ver o primeiro token em < 500ms.
- **Context Window:** Se você vai resumir livros, precisa de 128k+ tokens.
- **Licença:** Cuidado com licenças "Open Weights" que proíbem uso comercial em certos cenários.

## 🧠 Mental Model: "Commodity Intelligence"
Inteligência está virando eletricidade.
- GPT-4 é alta voltagem (caro, poderoso).
- Llama-3-8B é bateria AA (barato, portátil).
Não ligue um relógio de parede em alta voltagem.

## ⏭️ Próximo Passo
Onde baixar esses "Open Weights"?
Vá para **[Módulo 2: Ecossistema Hugging Face](../02-hugging-face)**.
