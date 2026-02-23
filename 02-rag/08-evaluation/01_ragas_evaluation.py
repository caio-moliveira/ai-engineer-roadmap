from utils import load_and_index_pdf
import pandas as pd
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy,
    context_recall,
)
from dotenv import load_dotenv

load_dotenv()

def run_evaluation():
    # 1. Preparar o RAG (VectorStore + LLM)
    try:
        vectorstore = load_and_index_pdf(reindex=False)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print("Certifique-se de que o PDF existe no caminho esperado em 06-rag-agent/utils.py")
        return

    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    
    # Config
    llm_generator = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embeddings = OpenAIEmbeddings()




    # 2. Definir Dataset de Teste
    # ... (creation of dataset remains the same) ...
    questions = [
        "Quais são os principais gases de efeito estufa mencionados?",
        "Qual o impacto do aquecimento global nos oceanos?",
        "O que o texto diz sobre energias renováveis?"
    ]

    ground_truths = [
        "O texto menciona principalmente dióxido de carbono (CO2), metano e óxido nitroso.", 
        "O aquecimento causa aumento do nível do mar, acidificação e impacto na vida marinha.",
        "O texto destaca a importância de transição para fontes como solar e eólica para reduzir emissões."
    ]

    # 3. Gerar Respostas e Coletar Contextos
    print(f"Gerando respostas para {len(questions)} perguntas...")
    
    answers = []
    contexts = []

    MOCK_WRONG_ANSWERS = True  # Mude para False para voltar a usar as respostas reais da IA

    for query in questions:
        # Recupera documentos
        docs = retriever.invoke(query)
        retrieved_texts = [doc.page_content for doc in docs]
        contexts.append(retrieved_texts)

        if not MOCK_WRONG_ANSWERS:
            # Gera resposta real usando o LLM generator
            messages = [
                ("system", "Você é um assistente útil. Use o contexto abaixo para responder a pergunta."),
                ("human", f"Contexto: {retrieved_texts}\n\nPergunta: {query}")
            ]
            ai_msg = llm_generator.invoke(messages)
            answers.append(ai_msg.content)
            
            print(f"\nPergunta: {query}")
            print(f"Resposta da IA: {ai_msg.content}")
            
    if MOCK_WRONG_ANSWERS:
        # Força respostas totalmente desconexas e alucinadas
        answers = [
            "A receita de bolo de cenoura leva 3 ovos, farinha e muita cobertura de chocolate.",
            "O maior problema nos oceanos modernos é que os pinguins estão roubando as pranchas de surf.",
            "O texto diz que a energia mais recomendada é ligar baterias em hamsters girando rodelas."
        ]
        print("\n[!] AVISO: Usando respostas MOCKADAS (totalmente erradas) para testar as métricas!")
        for q, a in zip(questions, answers):
            print(f"\nPergunta: {q}\nResposta Fake: {a}")

    # 4. Montar Dataset no formato HuggingFace/RAGAS
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)

    metrics = [
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
    ]

    # Executa a avaliação
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm_generator,
        embeddings=embeddings
    )

    print("\n--- Resultados da Avaliação ---")
    print(results)
    
    # Exportar para DataFrame pandas para melhor visualização (opcional)
    df = results.to_pandas()
    print("\nDetalhamento por pergunta:")
    # Configurações do Pandas para exibição completa (caso use print normal)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None)

    # Exibição formatada
    print(df[['user_input', 'faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']].to_markdown(index=False))

if __name__ == "__main__":
    run_evaluation()
