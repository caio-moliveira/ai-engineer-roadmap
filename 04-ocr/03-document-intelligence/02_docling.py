from pathlib import Path
import os
import time
import requests

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TableFormerMode,
)


def processar_documento_pdf(
    caminho_arquivo: str,
    output_dir: str = "./output",
    idioma_ocr: list = ["pt"],
    modo_tabela: str = "ACCURATE",
    salvar_markdown: bool = True,
):
    """
    Processa um documento PDF nativamente pelo computador usando o SDK do Docling.
    """
    print("\n[SDK LOCAL] Processando usando processamento local da sua máquina...")
    pipeline_options = PdfPipelineOptions()

    pipeline_options.do_ocr = True
    pipeline_options.ocr_options = EasyOcrOptions(lang=idioma_ocr)
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode[modo_tabela]

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    result = converter.convert(caminho_arquivo)
    doc = result.document

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    if salvar_markdown:
        md = doc.export_to_markdown()
        Path(f"{output_dir}/saida_sdk.md").write_text(md, encoding="utf-8")

    print("Concluído! Vá verificar a pasta /output")
    return doc


def processar_via_api_docker(
    caminho_arquivo: str,
    endpoint_base: str = "http://localhost:5001",
    # --- Formatos de saída ---
    formatos_saida: list = ["md"],          # "md", "json", "html", "text", "doctags"
    # --- Opções de OCR ---
    motor_ocr: str = "easyocr",            # "easyocr", "tesseract", "rapidocr", "auto"
    idiomas_ocr: list = ["pt"],
    forcar_ocr: bool = True,               # força OCR mesmo em PDFs com texto nativo
    # --- Opções de tabela ---
    fazer_estrutura_tabela: bool = True,
    modo_tabela: str = "accurate",          # "fast" ou "accurate"
    # --- Opções de imagem ---
    modo_exportacao_imagem: str = "placeholder",  # "placeholder", "embedded", "referenced"
    descrever_figuras: bool = False,
    # --- Backend de PDF e pipeline ---
    backend_pdf: str = "pypdfium2",         # "dlparse_v1", "dlparse_v2", "pypdfium2"
    pipeline: str = "standard",             # "standard", "vlm"
    # --- Configurações de polling e saída ---
    intervalo_polling: float = 3.0,
    output_dir: str = "./output",
):
    """
    Processa o documento terceirizando o peso computacional para o container Docker
    com a API oficial do Docling. Usa o fluxo assíncrono de 3 etapas:
      1. Envia o arquivo  →  POST /v1/convert/file/async   → retorna task_id
      2. Aguarda conclusão →  GET  /v1/status/poll/{task_id} → polling até "success"
      3. Busca resultado   →  GET  /v1/result/{task_id}     → salva os arquivos
    """
    nome_arquivo = os.path.basename(caminho_arquivo)

    # Opções passadas como campos de formulário individuais (não como JSON)
    opcoes = {
        "from_formats": "pdf",
        "to_formats": formatos_saida,
        "pipeline": pipeline,
        "ocr_engine": motor_ocr,
        "ocr_lang": idiomas_ocr,
        "force_ocr": "true" if forcar_ocr else "false",
        "do_table_structure": "true" if fazer_estrutura_tabela else "false",
        "table_mode": modo_tabela,
        "image_export_mode": modo_exportacao_imagem,
        "do_picture_description": "true" if descrever_figuras else "false",
        "pdf_backend": backend_pdf,
    }

    try:
        # ── ETAPA 1: Envio do arquivo (assíncrono) ────────────────────────────
        print(f"\n[1/3] Enviando '{nome_arquivo}' para {endpoint_base}...")
        with open(caminho_arquivo, "rb") as f:
            response = requests.post(
                f"{endpoint_base}/v1/convert/file/async",
                files={"files": (nome_arquivo, f, "application/pdf")},
                data=opcoes,
            )

        if response.status_code != 200:
            print(f"Erro ao enviar arquivo! Status {response.status_code}: {response.text}")
            return

        task_id = response.json().get("task_id")
        print(f"[1/3] Tarefa criada com ID: {task_id}")

        # ── ETAPA 2: Polling de status ────────────────────────────────────────
        print(f"\n[2/3] Aguardando processamento (verificando a cada {intervalo_polling}s)...")
        while True:
            status_response = requests.get(f"{endpoint_base}/v1/status/poll/{task_id}")
            status = status_response.json().get("task_status", "unknown")
            print(f"      Status atual: {status}")

            if status.lower() in ("success", "completed", "done"):
                break
            elif status.lower() in ("failure", "error", "failed"):
                print(f"A tarefa falhou. Resposta: {status_response.json()}")
                return

            time.sleep(intervalo_polling)

        # ── ETAPA 3: Busca do resultado ───────────────────────────────────────
        print(f"\n[3/3] Buscando resultado...")
        result_response = requests.get(f"{endpoint_base}/v1/result/{task_id}")

        if result_response.status_code != 200:
            print(f"Erro ao buscar resultado! Status {result_response.status_code}: {result_response.text}")
            return

        documento = result_response.json().get("document", {})
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        mapa_formatos = {
            "md":       ("saida_API.md",       "md_content"),
            "json":     ("saida_API.json",      "json_content"),
            "html":     ("saida_API.html",      "html_content"),
            "text":     ("saida_API.txt",       "text_content"),
            "doctags":  ("saida_API.doctags",   "doctags_content"),
        }

        for fmt, (nome_saida, chave) in mapa_formatos.items():
            if fmt in formatos_saida:
                conteudo = documento.get(chave)
                if conteudo:
                    caminho_saida = f"{output_dir}/{nome_saida}"
                    Path(caminho_saida).write_text(conteudo, encoding="utf-8")
                    print(f"Salvo: {caminho_saida}")

        print("\nConcluído! Vá verificar a pasta /output")

    except requests.exceptions.ConnectionError:
        print("\nERRO DE CONEXÃO: O container Docker está rodando?")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "1.pdf")
    
    processar_documento_pdf(pdf_teste)
    
    # processar_via_api_docker(pdf_teste)