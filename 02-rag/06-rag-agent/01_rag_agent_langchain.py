import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

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
    """Retrieve information to help answer a query about climate change."""
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
    tools = [retrieve_context]

    # promtp, caso precise
    prompt = (
        "Você tem acesso a ferramenta 'retrieve_context' que busca informações no PDF. "
        "Use a ferramenta para ajudar a responder as perguntas do usuário."
    )   

    # 3. Criar o Agente (ReAct pattern via LangGraph)
    # create_react_agent já configura o bind das tools e o loop de execução
    agent_executor = create_agent(model, tools, system_prompt=prompt)

    # 4. Executar
    query = "Quais são as principais causas das mudanças climáticas segundo o texto?"
    print(f"\nUser: {query}")
    
    # O stream retorna o estado do grafo a cada passo
    for event in agent_executor.stream(
        {"messages": [("user", query)]},
        stream_mode="values",
    ):
        # Imprime a última mensagem gerada no passo atual
        event["messages"][-1].pretty_print()

if __name__ == "__main__":
    main()
