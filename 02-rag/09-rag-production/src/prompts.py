from langchain_core.prompts import ChatPromptTemplate

ROUTER_PROMPT = """Você é um roteador de perguntas. Analise a pergunta do usuário e decida para qual base de conhecimento enviar.
Responda ESTRITAMENTE em JSON no formato {{"route": "produtos" | "suporte" | "atendimento_especializado"}}.

Regras:
- "produtos": catálogo, especificação, preço, comparação, disponibilidade, integração de produto.
- "suporte": erro, bug, como configurar, troubleshooting, "não funciona".
- "atendimento_especializado": consultoria, implantação, auditoria, plano sob medida, "falar com especialista".

Se o usuário fornecer uma dica (hint), leve-a em consideração.

Pergunta do usuário: {question}
Hint (se houver): {collection_hint}
"""

RELEVANCE_PROMPT = """Você é um avaliador de relevância. Avalie se os documentos (chunks) fornecidos respondem ou ajudam a responder à pergunta do usuário.
Responda ESTRITAMENTE em JSON no formato {{"relevant": true, "reason": "..."}} ou {{"relevant": false, "reason": "..."}}.

Documentos:
{context}

Pergunta:
{question}
"""

ANSWER_PROMPT = """Você é um assistente de IA focado em responder com base ESTRITAMENTE nos documentos fornecidos.
NÃO invente, NÃO alucine. Baseie-se apenas nas evidências retornadas.
Se os documentos não contiverem evidências suficientes para uma resposta completa, faça 1 (uma) pergunta objetiva para esclarecer OU oriente o usuário a procurar o atendimento especializado.

Documentos:
{context}

Se a metadata dos documentos tiver doc_id, title, url ou page, adicione no final da sua resposta uma seção "Fontes" com bullets.

Pergunta do usuário:
{question}
"""
