import os
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat, AnalyzeResult
from dotenv import load_dotenv

load_dotenv()


def analyze_read(file_path: str, output_dir: str = "./output"):
    client = DocumentIntelligenceClient(
        endpoint=os.getenv("AI_SERVICE_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AI_SERVICE_KEY"))
    )

    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado!")
        return

    poller = client.begin_analyze_document(
        "prebuilt-read",
        body=content_bytes,
        content_type="application/pdf",
        output_content_format=DocumentContentFormat.MARKDOWN,
    )

    result: AnalyzeResult = poller.result()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    caminho_saida = Path(output_dir) / "saida_azure.md"
    caminho_saida.write_text(result.content, encoding="utf-8")
    print(f"Salvo: {caminho_saida}")

    return {"text": result.content}


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "1.pdf")
    print("--- [AZURE AI] Iniciando Análise do Documento ---")
    analyze_read(pdf_teste)
