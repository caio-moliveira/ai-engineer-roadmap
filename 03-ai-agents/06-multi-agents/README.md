# 👥 Módulo 6: Multi-Agent Systems

> **Goal:** Saber quando *não* usar multi-agentes.  
> **Status:** Use com moderação.

## 1. O Hype vs A Realidade
Demos de Multi-Agentes são lindas. Swarms resolvendo problemas complexos.
Na prática:
- **Latência:** Multiplica por N agentes.
- **Custo:** Multiplica por N agentes.
- **Debug:** Fica exponencialmente mais difícil entender quem errou.

> **Regra:** Se um agente consegue fazer, use um agente. Só use Multi-Agente se as ferramentas ou contextos forem incompatíveis (ex: um Coder Agent precisa de acesso a arquivos locais, um Research Agent precisa de acesso à Web, e por segurança você quer isolá-los).

## 2. Padrões de Orquestração

### Supervisor (O Chefe)
Um LLM central decide quem trabalha.
- "Coder, escreva o script."
- "Reviewer, valide o script."
- O Supervisor roteia o estado.

### Hierárquico (Manager -> Tech Lead -> Dev)
Estrutura de árvore. Útil para decompor problemas grandes.

### Joint Collaboration (Mesa Redonda)
Agentes conversam entre si e passam o bastão.
- Mais caótico, mas pode gerar soluções criativas.

## 3. A Falácia da Comunicação
LLMs conversando com LLMs em inglês é ineficiente.
Eles devem trocar **Estado Estruturado (JSON)**, não texto.
LangGraph facilita isso compartilhando o `State`.

## 🧠 Mental Model: "A Lei de Conway"
O design do sistema reflete a estrutura de comunicação.
Se você criar 10 agentes especialistas que não se falam direito, terá um sistema fragmentado e burocrático.

## ⏭️ Próximo Passo
Como impedir que eles façam besteira?
Vá para **[Módulo 7: Deep Agents (Segurança e Guardrails)](../07-deep-agents)**.
