# 🛡️ Módulo 3: Noul, Detecção e Verificação

> **Objetivo:** decompor perguntas amplas em afirmações verificáveis.
> **Pergunta-chave:** "é spam?" é uma pergunta ou seis?

---

## 📚 Índice Prático e Documentação

1. **[Spam decomposto](#1-uma-pergunta-ou-seis)**
   * Docs: [Noul](https://docs.typesafe.ai/primitives/noul)
   * Exemplo: `01_spam_decomposed.py`
2. **[Multirrótulo](#2-multirrótulo)**
   * Exemplo: `02_multilabel.py`
3. **[Guardrail de entrada](#3-guardrail-antes-do-llm)**
   * Exemplo: `03_guardrail_input.py`
4. **[Verificação de saída](#4-verificação-depois-do-llm)**
   * Exemplo: `04_verify_output.py`
5. **[Gate de risco de tool call](#5-automodemiddleware)**
   * Docs: [langchain-typesafe: middleware experimental](https://docs.langchain.com/oss/python/integrations/providers/typesafe) | [LangChain middleware](https://docs.langchain.com/oss/python/langchain/middleware)
   * Exemplo: `05_langchain_middleware.py`

---

## 1. Uma pergunta ou seis?

"É spam?" mistura várias coisas. O script compara um Noul direto com **seis Nouls verificáveis**: pede credencial, urgência artificial, promete prêmio, remetente inconsistente, link suspeito e pede pagamento. Os seis viram uma **soma ponderada em código**.

A versão decomposta é auditável: você sabe por que um e-mail foi barrado. Ela também deixa ajustar um peso sem tocar no modelo e mede cada sinal contra o rótulo. O golden set (`data/golden_spam.json`) tem legítimos difíceis de propósito: uma cobrança real que pede pagamento e um aviso real de login que parece phishing.

## 2. Multirrótulo

Um ticket pode pedir reembolso **e** ameaçar cancelar. Um Choice só devolve uma opção; quatro Nouls dão quatro probabilidades independentes. O script mostra que o Choice nunca acerta exatamente um ticket com dois rótulos.

| Use | Quando |
|---|---|
| Choice | opções mutuamente exclusivas (fila, categoria, tool) |
| Nouls | afirmações independentes (sinais, rótulos, verificações) |

## 3. Guardrail antes do LLM

Três Nouls na entrada do agente de vendas: injection, dado sensível e fora de escopo. Bloqueia se **qualquer** probabilidade passar do limiar. O script varre os limiares e mostra a troca entre ataques barrados (recall) e perguntas legítimas bloqueadas (taxa de falso positivo), sobre as 20 perguntas adversariais do golden set de vendas.

## 4. Verificação depois do LLM

Três Nouls sobre o trio (pergunta, dados, resposta): responde ao pedido? inventa número? segue a política? O golden set (`data/golden_verify.json`) tem 24 respostas, boas e com defeitos plantados: número inventado, previsão, dado pessoal e recomendação de demissão.

O estado aqui é grande, porque inclui a tabela de dados inteira. Com o Laya, confira `usage.truncated` na resposta crua.

## 5. AutoModeMiddleware

O middleware experimental intercepta as tools que você listar e faz um Noul antes de executar: "esta chamada é arriscada ou não autorizada?". Acima de 0,5, a tool **não roda**. O script mede o gate com 12 chamadas do golden set (`data/golden_tool_calls.json`): metade pedida explicitamente, metade com argumentos trocados, injeção indireta ou exfiltração. O modelo de chat é falso e roteirizado: o que medimos é o gate, não o LLM.

Ele é *fail-closed*: se o classificador falhar, a tool não roda. Para pedir aprovação humana em vez de bloquear, combine com o `HumanInTheLoopMiddleware` do Bloco 3.

---

## 🏋️ Exercício

Coloque guardrail **antes** e verificação **depois** do LLM no agente do Bloco 3:

1. Reaproveite `GUARDRAIL` e `VERIFICACAO` de `common/specs.py`, adaptando a política ao domínio do agente.
2. Monte um golden set adversarial com pelo menos 20 entradas (injeção direta, injeção escondida em documento, dado sensível, fora de escopo).
3. Meça recall e taxa de falso positivo em três limiares e escolha um. Escreva o custo de cada tipo de erro antes de escolher.

## ⏭️ Próximo Passo
Nem toda pergunta é sim ou não: algumas são "quanto". **[Módulo 4: Score, ranking e priorização](../04-score-ranking)**.
