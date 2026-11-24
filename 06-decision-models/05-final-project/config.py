"""Configuração de ambiente: backends, modelos, versão padrão do grafo e preços.

Tudo aqui vem de variáveis de ambiente (ou do `.env` da raiz). Os limiares e as regras de negócio
NÃO ficam aqui: ficam em `policy.py`, versionados no código junto com o resto da equipe.
"""

from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Exporta o .env para os.environ: o SDK do Jev e os clients do LangChain leem as chaves de lá.
load_dotenv()


class Settings(BaseSettings):
    # Modelo de decisão: jev (precisa de TYPESAFE_API_KEY) ou laya (local, porta 8001).
    decision_backend: Literal["jev", "laya"] = "jev"
    # No Windows, use 127.0.0.1 e não localhost (localhost tenta IPv6 primeiro e atrasa ~2 s).
    laya_base_url: str = "http://127.0.0.1:8001"

    # O LLM do agente em dois tamanhos, no formato provedor:modelo do init_chat_model.
    llm_small: str = "anthropic:claude-haiku-5-5"
    llm_large: str = "anthropic:claude-sonnet-5-5"
    # Teto de tokens de saída do modelo barato, para controlar custo. Uma resposta longa demais sai
    # truncada; o juiz reprova e a cascata refaz no modelo grande (que não tem esse teto).
    llm_small_max_tokens: int = 1024

    # Porta da API. Não é a 8000 porque ela costuma estar ocupada (outras APIs do curso, containers Docker).
    app_port: int = 8010

    # Versão do grafo usada quando a requisição não diz qual: v1, v2 ou v3.
    agent_version: Literal["v1", "v2", "v3"] = "v3"

    # Preços em US$ por milhão de tokens (entrada, saída), para o resumo de economia.
    # Os padrões são os do Claude Haiku 5.5 e do Claude Sonnet 5.5; ajuste se trocar de modelo.
    price_small_in: float = 0.10
    price_small_out: float = 0.50
    price_large_in: float = 2.00
    price_large_out: float = 10.00


@lru_cache
def get_settings() -> Settings:
    return Settings()
