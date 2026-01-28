# 🧠 Módulo 7: Mentalidade de Engenharia

> **Goal:** Pensar como um Senior.  
> **Status:** O diferencial.

## 1. Probabilístico vs Determinístico
Engenharia tradicional: `if a == b: return true`. (100% certeza).
Engenharia de IA: `llm.generate()`. (95% certeza).
Seu sistema precisa ser **Resiliente a Falhas**. O "caminho feliz" raramente acontece 100% das vezes. Projete mecanismos de *fallback*.

## 2. Observabilidade é Tudo
Em software normal, stack trace resolve.
Em IA, você precisa saber:
- Qual foi o prompt exato?
- Qual foi a latência do retrieval?
- Quantos tokens gastamos?
Use ferramentas de tracing (Langsmith / Langfuse). `print()` não é observabilidade.

## 3. Custo e Latência
Todo engenheiro sênior sabe o preço das coisas.
- GPT-4 custa 30x mais que GPT-3.5. Vale a pena para *esta* feature?
- O usuário espera 10s? Se não, precisamos de Streaming ou Cache.

## 🧱 Checklist de Formatura do Bloco 1
- [ ] Sei criar um ambiente limpo com `uv`.
- [ ] Uso `async/await` por padrão.
- [ ] Meus commits seguem um padrão.
- [ ] Sei validar outputs de LLM com Pydantic.

## 🎓 Graduação
Você tem a base. Agora vamos construir coisas reais.

**Próximo Bloco: [RAG Systems](../../02-rag-systems)**
