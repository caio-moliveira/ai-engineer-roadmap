"""Aula 05 · Script 02: verificar a resposta do LLM com o Jev em vez de um LLM juiz.

Depois que o LLM escreve, alguém confere: a resposta responde a pergunta? Inventou algum dado
que não estava no contexto? O jeito comum é chamar outro LLM como juiz. Aqui, as mesmas duas
perguntas vão para o Jev (dois Nouls) e para um LLM juiz (structured output), e comparamos
veredito, tokens e latência.

As respostas a verificar estão escritas no script, para o resultado não depender de geração:
uma correta, uma que inventa dados e uma que enrola.

Rode: python 06-decision-models/05-when-to-use-jev/02_verify_llm_output.py
Precisa de TYPESAFE_API_KEY e da chave do LLM juiz (padrão: ANTHROPIC_API_KEY).
Para usar o GPT-5.6 Luna como juiz: LLM_MODEL=openai:gpt-5.6-luna
"""

import os
import sys
import time

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()
if not os.environ.get("TYPESAFE_API_KEY"):
    sys.exit("Defina TYPESAFE_API_KEY no .env da raiz para chamar o Jev.")

LLM_MODEL = os.environ.get("LLM_MODEL", "anthropic:claude-sonnet-5-5")

CONTEXTO = "Pedido 4821: enviado em 03/11 pela Jadlog. Previsão de entrega: 07/11. Frete pago: R$ 19,90."
PERGUNTA = "Quando chega o meu pedido 4821?"

RESPOSTAS = {
    "correta": "Seu pedido 4821 foi enviado em 03/11 pela Jadlog e a previsão de entrega é 07/11.",
    "inventa": "Seu pedido 4821 chega amanhã, 05/11, e como cortesia o frete foi reembolsado.",
    "enrola": "Agradecemos o contato! Nossa equipe trabalha para entregar todos os pedidos o quanto antes.",
}

VERIFICACAO = {
    "responde": Noul(instructions="A resposta responde a pergunta do cliente?"),
    "inventa": Noul(
        instructions="A resposta afirma algum fato, data ou valor que não está no contexto?",
        criteria={
            "true": "contém pelo menos uma informação ausente do contexto ou contrária a ele",
            "false": "tudo o que a resposta afirma está no contexto",
        },
    ),
}


class Veredito(BaseModel):
    responde: bool = Field(description="A resposta responde a pergunta do cliente?")
    inventa: bool = Field(
        description="A resposta afirma algum fato, data ou valor que não está no contexto?"
    )


juiz = init_chat_model(LLM_MODEL).with_structured_output(
    Veredito, method="json_schema", include_raw=True
)

print(f"Contexto: {CONTEXTO}\nPergunta: {PERGUNTA}")
with TypeSafeClient() as client:
    for nome, resposta in RESPOSTAS.items():
        estado = {"contexto": CONTEXTO, "pergunta": PERGUNTA, "resposta": resposta}

        start = time.perf_counter()
        jev = client.system_one(state=estado, questions=VERIFICACAO)
        jev_ms = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        out = juiz.invoke(
            "Avalie a resposta do atendente.\n\n"
            f"Contexto: {CONTEXTO}\nPergunta: {PERGUNTA}\nResposta: {resposta}"
        )
        juiz_ms = (time.perf_counter() - start) * 1000
        usage = out["raw"].usage_metadata or {}

        print(f"\n[{nome}] {resposta}")
        print(
            f"  Jev:       responde P={jev.nouls['responde'].noul:.2f}   inventa P={jev.nouls['inventa'].noul:.2f}"
            f"   [{jev.usage.input_tokens} tokens de entrada, {jev.usage.output_tokens} de saída, {jev_ms:.0f} ms]"
        )
        print(
            f"  LLM juiz:  responde={out['parsed'].responde!s:<5}  inventa={out['parsed'].inventa!s:<5}"
            f"   [{usage.get('input_tokens', 0)} tokens de entrada, {usage.get('output_tokens', 0)} de saída, {juiz_ms:.0f} ms]"
        )

print(
    "\nO esperado: a correta passa; a que inventa reprova em 'inventa'; a que enrola reprova em"
    "\n'responde'. Confira se os dois acertaram. Além do veredito:"
    "\n- O Jev devolve uma probabilidade: você escolhe o limiar de reprovação (0,3 para dado"
    "\n  inventado, se errar for caro). O LLM juiz devolve só verdadeiro ou falso."
    "\n- Verificação roda em toda resposta do sistema. Tokens e latência se multiplicam pelo volume."
)
