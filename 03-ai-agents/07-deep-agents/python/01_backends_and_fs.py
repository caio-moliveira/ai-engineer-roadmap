import os
import shutil
from dotenv import load_dotenv

# Nota: As rotinas abaixo assumem a presença do pacote oficial `deepagents` no ambiente
# pip install deepagents
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend
from langchain_core.messages import HumanMessage

load_dotenv()

# ==========================================
# 1. Por que usar Deep Agents (O Harness)?
# ==========================================
# O `create_deep_agent` é um wrapper superior ao `create_agent` que injeta nativamente:
# - Gerenciamento robusto de Estado/Memória Temporária
# - Capacidades de Planejamento (To-Do Lists) para a IA
# - Acesso seguro a File Systems e Terminal (Console Sandboxed)
# Tudo isso trocando apenas a Engine base (Backend).


def test_ephemeral_state_backend():
    print("\n" + "="*50)
    print(" 1. STATE BACKEND (EFÊMERO - DEFAULT)")
    print("="*50)
    
    # Por padrão, se você não passar nada, ele usa um StateBackend.
    # Os arquivos / rascunhos que o agente criar ficarão APENAS na RAM (State do Langgraph).
    print("[Harness]: Subindo agente invisível (RAM apenas)...")
    
    agent = create_deep_agent(
        model="openai:gpt-4o-mini",
        system_prompt="Você é um bloco de notas. Escreva um poema no arquivo 'poema.txt' e depois o leia."
    )
    
    response = agent.invoke(
        {"messages": [HumanMessage(content="Escreva 'Rosas sao vermelhas' em um arquivo poema.txt e me mostre o Ls.")]},
        config={"configurable": {"thread_id": "ephemeral_01"}}
    )
    
    print(f"\n[Agente State]: \n{response['messages'][-1].content}")
    

def test_local_filesystem_backend():
    print("\n\n" + "="*50)
    print(" 2. FILESYSTEM BACKEND (DURÁVEL & SANDBOXED)")
    print("="*50)
    
    # Preparando um diretório seguro (Sandbox)
    sandbox_dir = "./meu_sandbox"
    os.makedirs(sandbox_dir, exist_ok=True)
    
    print(f"[Harness]: Conectando Agente ao diretório seguro: {sandbox_dir}")
    print("[Segurança]: virtual_mode=True impede que a LLM leia C:// ou .env externos (Path Traversal)")
    
    # O FilesystemBackend anexa as ferramentas 'ls', 'read_file', 'write_file' automaticamente!
    backend = FilesystemBackend(root_dir=sandbox_dir, virtual_mode=True)
    
    agent = create_deep_agent(
        model="openai:gpt-4o-mini",
        backend=backend,
        system_prompt="Você interage com o HD do usuário. Não invente coisas, veja de fato o HD."
    )
    
    print("\n[Usuário]: Crie um arquivo chamado 'saudacao.txt' com a frase 'Ola Mundo Real'.")
    
    response = agent.invoke(
        {"messages": [HumanMessage(content="Crie um arquivo chamado 'saudacao.txt' com a frase 'Ola Mundo Real', depois dê um grep verificando se gravou.")]},
        config={"configurable": {"thread_id": "fs_01"}}
    )
    
    print(f"\n[Agente FS]: \n{response['messages'][-1].content}")
    print("\nVerificando o HD fisicamente pelo Python:")
    if os.path.exists("./meu_sandbox/saudacao.txt"):
        with open("./meu_sandbox/saudacao.txt", "r") as f:
            print(f" -> Conteúdo C://.../meu_sandbox/saudacao.txt: {f.read()}")
            
    # Clean up (Limpeza didática)
    shutil.rmtree(sandbox_dir, ignore_errors=True)

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: Variável de ambiente OPENAI_API_KEY ausente.")
    else:
        # Nota: Só funcionará se o pacote 'deepagents' puder rodar no ecossistema
        try:
            test_ephemeral_state_backend()
            test_local_filesystem_backend()
        except ImportError:
            print("\n[Erro]: Pacote `deepagents` não está instalado no seu ambiente local (pip install deepagents).")
            print("Este script demonstra teoricamente sua implementação e ferramentas nativas.\n")
