"""Módulo 01 · Script 05 (exercício): código, modelo de decisão, LLM ou classificador treinado?

O fluxo abaixo é o agente de e-mail do Bloco 3 (03-ai-agents/03-langgraph-orchestration),
quebrado em etapas. Para cada etapa, escolha onde ela deve rodar:

- "codigo":       regra determinística resolve (formato, lookup, conta, roteamento por flag).
- "decisao":      pergunta fechada sobre texto livre, com opções conhecidas e necessidade de probabilidade.
- "llm":          precisa GERAR texto ou raciocinar em vários passos com ferramentas.
- "classificador": pergunta fechada, alto volume, rótulos estáveis e milhares de exemplos rotulados.

Preencha MINHA_RESPOSTA e rode: python 01-decision-fundamentals/05_decision_matrix.py
Não chama nenhum modelo.
"""

ETAPAS = [
    ("ler_email", "Extrair remetente, assunto e corpo do e-mail recebido (JSON da caixa de entrada)."),
    ("idioma", "Detectar se o e-mail está em português para escolher o template."),
    ("intencao", "Classificar a intenção: dúvida, reclamação, pedido de reembolso ou elogio."),
    ("urgente", "Dizer se o cliente está parado e precisa de resposta hoje."),
    ("buscar_contexto", "Buscar trechos da base de conhecimento relacionados ao e-mail (RAG)."),
    ("abrir_ticket", "Abrir um ticket no sistema de suporte com os campos extraídos."),
    ("redigir_resposta", "Escrever a resposta ao cliente usando os trechos encontrados."),
    ("verificar_resposta", "Checar se a resposta promete algo fora da política (prazo, reembolso, desconto)."),
    ("precisa_humano", "Decidir se o caso vai para revisão humana antes de enviar."),
    ("spam_massa", "Filtrar spam em 2 milhões de e-mails por dia, com 500 mil e-mails já rotulados."),
]

OPCOES = {"codigo", "decisao", "llm", "classificador"}

# Preencha aqui. Deixe None para ver o gabarito da etapa.
MINHA_RESPOSTA: dict[str, str | None] = {etapa: None for etapa, _ in ETAPAS}

GABARITO = {
    "ler_email": ("codigo", "O e-mail já chega estruturado: é parse, não interpretação."),
    "idioma": ("codigo", "Biblioteca de detecção de idioma resolve com custo zero; não precisa de modelo grande."),
    "intencao": ("decisao", "Choice com 4 opções conhecidas, sobre texto livre, e a probabilidade decide se automatiza."),
    "urgente": ("decisao", "Noul ou Score de urgência: pergunta fechada que precisa de confiança calibrada."),
    "buscar_contexto": ("codigo", "Busca vetorial é código (embedding + índice). Um Score pode reordenar os candidatos (módulo 04)."),
    "abrir_ticket": ("codigo", "Chamada de API com campos já decididos. Nenhum modelo precisa estar no caminho."),
    "redigir_resposta": ("llm", "É geração de texto: o único lugar do fluxo em que um LLM é insubstituível."),
    "verificar_resposta": ("decisao", "Nouls verificáveis sobre a resposta gerada: segue a política? promete prazo? (módulo 03)."),
    "precisa_humano": ("codigo", "Regra sobre as probabilidades já calculadas: se confiança < limiar, humano. O limiar vem do módulo 05."),
    "spam_massa": ("classificador", "Volume enorme, rótulos estáveis e meio milhão de exemplos: um classificador treinado custa quase nada por chamada."),
}

acertos = 0
respondidas = 0
for etapa, descricao in ETAPAS:
    certo, porque = GABARITO[etapa]
    minha = MINHA_RESPOSTA.get(etapa)
    if minha is not None and minha not in OPCOES:
        raise ValueError(f"{etapa}: '{minha}' não é uma opção válida ({sorted(OPCOES)})")
    marca = "·"
    if minha is not None:
        respondidas += 1
        acertos += minha == certo
        marca = "✓" if minha == certo else "✗"
    print(f"{marca} {etapa:<18} {descricao}")
    print(f"    gabarito: {certo:<13} {porque}")
    if minha is not None and minha != certo:
        print(f"    você disse: {minha}")

contagem = {opcao: sum(1 for c, _ in GABARITO.values() if c == opcao) for opcao in sorted(OPCOES)}
print(f"\nNo gabarito: {contagem}")
print("Só 1 de 10 etapas precisa gerar texto. Num agente de produção, a maior parte das chamadas")
print("a modelo são decisões, e é aí que está a parte da conta que ninguém olha.")
if respondidas:
    print(f"\nVocê acertou {acertos} de {respondidas}.")
else:
    print("\nPreencha MINHA_RESPOSTA no topo do arquivo e rode de novo.")
