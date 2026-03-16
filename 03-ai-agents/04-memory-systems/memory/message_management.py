from typing import List, Optional, Union

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_openai import ChatOpenAI

# Gerenciamento de mensagens é crucial para:
# 1. Reduzir custos de tokens.
# 2. Manter a performance do modelo dentro da janela de contexto.
# 3. Evitar confusão com informações irrelevantes ou muito antigas.

class MessageManagement:
    """
    Utilitários para manipular o histórico de mensagens (trim, summarize, delete).
    """

    @staticmethod
    def trim_history(
        messages: List[BaseMessage], 
        max_tokens: int = 1000,
        strategy: str = "last"
    ) -> List[BaseMessage]:
        """
        Remove mensagens antigas para caber no limite de tokens.
        """
        # Utiliza a utility oficial do LangChain
        return trim_messages(
            messages,
            max_tokens=max_tokens,
            strategy=strategy,
            token_counter=len, # Simplificação para o exemplo: conta 1 p/ 1
            start_on="human",
            include_system=True
        )

    @staticmethod
    async def summarize_history(
        messages: List[BaseMessage], 
        llm: ChatOpenAI
    ) -> str:
        """
        Gera um resumo das mensagens para comprimir o contexto.
        """
        combined_text = "\n".join([f"{m.type}: {m.content}" for m in messages])
        prompt = f"Resuma a conversa abaixo de forma concisa, mantendo fatos importantes:\n\n{combined_text}"
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return str(response.content)

    @staticmethod
    def delete_by_index(messages: List[BaseMessage], indices: List[int]) -> List[BaseMessage]:
        """
        Remove mensagens específicas por índice (útil para edição de histórico).
        """
        return [m for i, m in enumerate(messages) if i not in indices]

def compare_strategies():
    """
    Tabela comparativa de estratégias de gerenciamento de memória.
    """
    return {
        "Trim": "Rápido, baixo custo, mas perde contexto antigo totalmente.",
        "Summarize": "Mantém essência, mas consome tokens para gerar o resumo (LLM call).",
        "Filtering": "Preciso, mas exige lógica complexa para decidir o que filtrar."
    }
