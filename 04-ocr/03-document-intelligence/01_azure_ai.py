import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult
from dotenv import load_dotenv

load_dotenv()


def analyze_read(file_path: str):    
    client = DocumentIntelligenceClient(
        endpoint=os.getenv("AI_SERVICE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AI_SERVICE_KEY"))
    )

    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo '{file_path}' não encontrado!")
        return

    poller = client.begin_analyze_document(
        "prebuilt-read",
        body=content_bytes,
        content_type="application/pdf",
        output_content_format=DocumentContentFormat.MARKDOWN,
    )
    
    result: AnalyzeResult = poller.result()

    return {"text": result.content}
    # return result
    

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "Caratinga.pdf")
    print("--- [AZURE AI] Iniciando Análise do Documento ---")
    print("⏳ Carregando arquivo e enviando requisição para nuvem...")
    resultado = analyze_read(pdf_teste)
    print(resultado)
    # if resultado and "text" in resultado:
    #     print("\n=== TEXTO EXTRAÍDO PELA AZURE ===")
    #     print(resultado["text"])
    # else:
    #     print("\nNenhum texto foi retornado ou ocorreu um erro.")
