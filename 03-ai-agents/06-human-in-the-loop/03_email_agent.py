import os
import imaplib
import smtplib
import email
from email.message import EmailMessage
from email.header import decode_header
from dotenv import load_dotenv

from typing import Callable
from langchain.agents import create_agent
from langchain.agents.middleware import (
    wrap_model_call, 
    dynamic_prompt, 
    HumanInTheLoopMiddleware,
    ModelRequest, 
    ModelResponse
)
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain.tools import tool

load_dotenv()

# ==========================================
# Configurações do Gmail (via .env)
# ==========================================
# Crie as seguintes variáveis no seu arquivo .env:
# GMAIL_USER="seu-email@gmail.com"
# GMAIL_APP_PASSWORD="sua-senha-de-app-do-google"
# TARGET_SENDER="email_do_chefe@empresa.com"

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TARGET_SENDER = os.getenv("TARGET_SENDER", "caiomoliveira@hotmail.com")

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"


@tool
def check_inbox(sender: str) -> str:
    """Busca o último email não lido de um remetente específico na caixa de entrada."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return "Erro: Credenciais do Gmail ausentes no .env."
        
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")
        
        status, messages = mail.search(None, f'(FROM "{sender}")')
        
        mail_ids = messages[0].split()
        if not mail_ids:
            return f"Nenhum email encontrado de {sender}."
            
        latest_id = mail_ids[-1]
        _, msg_data = mail.fetch(latest_id, "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            charset = part.get_content_charset() or "utf-8"
                            body = part.get_payload(decode=True).decode(charset, errors="replace")
                            break
                else:
                    charset = msg.get_content_charset() or "utf-8"
                    body = msg.get_payload(decode=True).decode(charset, errors="replace")
                    
                mail.logout()
                return f"Assunto: {subject}\n\nCorpo:\n{body.strip()}"
    except Exception as e:
        return f"Erro ao acessar IMAP: {e}"

@tool
def send_email_response(to: str, subject: str, draft_reason: str) -> str:
    """
    Ferramenta para enviar uma resposta de email elaborada.
    AÇÃO SENSÍVEL: Sujeito à aprovação humana.
    """
    try:
        msg = EmailMessage()
        msg.set_content(draft_reason)
        msg["Subject"] = f"Re: {subject}"
        msg["From"] = GMAIL_USER
        msg["To"] = to
        
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            
        return "Email enviado com sucesso para o SMTP!"
    except Exception as e:
        return f"Erro ao enviar via SMTP: {e}"



@wrap_model_call
def log_agent_activity(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Middleware para logging da abstração do agente."""
    print("🤖 [LLM Call] O modelo analisando a solicitação...")
    response = handler(request)
    return response

@dynamic_prompt
def inject_personality(request: ModelRequest) -> str:
    """Injeta contexto dinâmico no system prompt do agente."""
    return (
        "Você é um assistente pessoal encarregado de ler emails usando a ferramenta check_inbox "
        "e formular respostas curtas, educadas e assertivas. "
        "Não invente informações sensíveis. "
        "Após ler a mensagem e gerar o conteúdo, você deve atuar invocar send_email_response."
    )

def main():
    print("=== Assistente Pessoal de Email (Langchain Middleware) ===")
    print(f"Alvo configurado: {TARGET_SENDER}")
    
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("\n🔧 CONFIGURAÇÃO NECESSÁRIA! 🔧")
        print("Antes de continuar, coloque GMAIL_USER e GMAIL_APP_PASSWORD no .env.")
        print("Para senhas de App do Google, consulte a aba de Segurança da conta.")
        return

    # HITL Governança
    hitl = HumanInTheLoopMiddleware(
        interrupt_on={
            "check_inbox": False,           
            "send_email_response": {  
                "allowed_decisions": ["approve", "edit", "reject"]
            }
        }
    )

    agent = create_agent(
        model="gpt-4o-mini",
        tools=[check_inbox, send_email_response],
        checkpointer=InMemorySaver(),
        middleware=[inject_personality, log_agent_activity, hitl]
    )

    config = {"configurable": {"thread_id": "email-session-100"}}

    print("\n[Sistema] Iniciando busca automatizada de emails para ler e redigir...")
    
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": f"Busque o último e-mail recebido de {TARGET_SENDER}, avalie o conteúdo, redija uma resposta profissional direta ao ponto e a prepare para envio."}
        ]
    }, config=config)

    if "__interrupt__" in result:
        print("\n" + "="*50)
        print("⏸️ [SISTEMA PAUSADO] Revisão de Email Pendente")
        print("="*50)
        
        pending_action = result["__interrupt__"][0].value
        
        args = pending_action["action_requests"][0]["args"]

        
        print("\n=== RASCUNHO GERADO PELO MODELO ===")
        print(f"Para: {args.get('to')}")
        print(f"Assunto: {args.get('subject')}")
        print("-" * 50)
        print(f"Mensagem:\n{args.get('draft_reason')}")
        print("="*50)
        
        print("\n>> Decisões Disponíveis:")
        print("1 - APROVAR e Enviar.")
        print("2 - REJEITAR.")
        print("3 - EDITAR mensagem ANTES de enviar (via terminal).")
        
        choice = input("Digite 1, 2 ou 3: ")
        
        if choice.strip() == "1":
            print("\n>> Aprovando pacote de dados para o SMTP...")
            resume_data = {"decisions": [{"type": "approve"}]}
            agent.invoke(Command(resume=resume_data), config=config)
            print("🚀 Fluxo de envio concluído!")
            
        elif choice.strip() == "2":
            print("\n>> Rejeitando ToolCall. O modelo será perdoado e fluxo abortado.")
            resume_data = {"decisions": [{"type": "reject", "feedback": "Usuário cancelou do terminal."}]}
            agent.invoke(Command(resume=resume_data), config=config)
            
        elif choice.strip() == "3":
            print("\n>> Modo Edição:")
            novo_texto = input("Escreva a nova mensagem final completa do email:\n> ")
            
            resume_data = {
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "send_email_response",
                            "args": {
                                "to": args.get("to"),
                                "subject": args.get("subject"),
                                "draft_reason": novo_texto
                            }
                        }
                    }
                ]
            }
            print("\n>> Modificando Payload e Aprovando o ToolCall editado para o SMTP...")
            agent.invoke(Command(resume=resume_data), config=config)
            print("🚀 Fluxo de envio (editado) concluído!")
            
    else:
        print("\n✅ Fluxo encerrado sem interrupções ativas.")
        print(f"Resposta Contextual: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
