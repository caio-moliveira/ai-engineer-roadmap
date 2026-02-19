import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

from langchain_community.tools import DuckDuckGoSearchRun

# Importa nossa função utilitária
from utils import load_and_index_pdf

load_dotenv()

print("--- Inicializando Vector Store Globalmente para a Tool ---")
# Inicializa o vectorstore globalmente para que a tool possa acessá-lo.
# Em apps reais, você injetaria isso via 'bind_tools' ou closures,
# mas para este script simples, global funciona bem.
try:
    vectorstore = load_and_index_pdf()
except FileNotFoundError as e:
    print(f"Erro crítico: {e}")
    # Cria um dummy para não quebrar a definição da tool se falhar
    vectorstore = None 

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query about climate change. Use this tool FIRST for any questions related to the document content."""
    if not vectorstore:
        return "Erro: Banco de dados não disponível.", []
        
    print(f"\n[Tool] Buscando por: '{query}'")
    retrieved_docs = vectorstore.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata.get('source', 'PDF')}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

def main():
    print("--- 04. RAG Agent (LangGraph + Custom Tool) ---")
    
    if not vectorstore:
        print("Abortando: VectorStore não carregado.")
        return

    # 1. Configurar o Modelo
    # 'gpt-4o-mini' é o nome correto do modelo mais recente/rápido
    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # 2. Definir Tools
    search_tool = DuckDuckGoSearchRun()
    tools = [retrieve_context, search_tool]

    # promtp, caso precise
    prompt = (
        "Você é um assistente útil. Você tem acesso às ferramentas: 'retrieve_context' (busca no PDF de Mudanças Climáticas) e 'duckduckgo_search' (busca na Web). "
        "Siga estas regras estritamente:\n"
        "1. Para saudações ou perguntas de conversa fiada (ex: 'Oi', 'Tudo bem?', 'Quem é você?'), responda NATURALMENTE e NÃO USE NENHUMA FERRAMENTA.\n"
        "2. Para perguntas sobre o conteúdo do documento (Mudanças Climáticas), use PRIMEIRO a ferramenta 'retrieve_context'.\n"
        "3. Se a busca no PDF ('retrieve_context') não retornar informações relevantes ou suficientes, você DEVE usar a ferramenta 'duckduckgo_search' para buscar na web.\n"
        "4. Sempre cite a fonte da informações (PDF ou Web).\n"
    )   

    # 3. Criar o Agente (ReAct pattern via LangGraph)
    # create_react_agent já configura o bind das tools e o loop de execução
    agent_executor = create_agent(model, tools, system_prompt=prompt)

    # 4. Executar
    # Exemplo 1: Pergunta sobre o PDF
    query1 = "Quais são as principais causas das mudanças climáticas segundo o texto?"
    print(f"\nUser: {query1}")
    for event in agent_executor.stream({"messages": [("user", query1)]}, stream_mode="values"):
        event["messages"][-1].pretty_print()

    # Exemplo 2: Chitchat
    query2 = "Oi, tudo bem?"
    print(f"\nUser: {query2}")
    for event in agent_executor.stream({"messages": [("user", query2)]}, stream_mode="values"):
        event["messages"][-1].pretty_print()

    # Exemplo 3: Pergunta fora do contexto (Fallback)
    query3 = "Qual é a cotação atual do Bitcoin?"
    print(f"\nUser: {query3}")
    for event in agent_executor.stream({"messages": [("user", query3)]}, stream_mode="values"):
        event["messages"][-1].pretty_print()

if __name__ == "__main__":
    main()
