from pathlib import Path
import json
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
    salvar_json: bool = True,
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

    if salvar_json:
        doc_dict = doc.export_to_dict()
        Path(f"{output_dir}/saida_sdk.json").write_text(
            json.dumps(doc_dict, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
    print("[SDK LOCAL] Concluído! Vá verificar a pasta /output")
    return doc


def processar_via_api_docker(
    caminho_arquivo: str, 
    endpoint_url: str = "http://localhost:5001/v1/convert/file"
):
    """
    Processa o mesmo documento, mas terceirizando todo o peso computacional 
    para o container do Docker rodando silenciosamente a API oficial do Docling.
    """    
    print(f"\n[API MICROSERVIÇO] Enviando PDF para {endpoint_url}...")
    start_time = time.time()
    
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    try:
        print("[API MICROSERVIÇO] Pingando o servidor do Docker aguardando resposta...")
        with open(caminho_arquivo, "rb") as f:
            files = {"files": (nome_arquivo, f, "application/pdf")}
            data = {"options": '{"to_formats": ["md"]}'}
            
            response = requests.post(endpoint_url, files=files, data=data)
            
            if response.status_code != 200:
                print(f"Erro na API! Retorno {response.status_code}: {response.text}")
                return
                
            resultados = response.json()
            
            if isinstance(resultados, dict):
                resultados = [resultados]
                
            tempo = time.time() - start_time
            print(f"[API MICROSERVIÇO] Sucesso em {tempo:.2f}s!")
                
            for res in resultados:
                # O Markdown fica em md_content quando acessado via API (no raiz ou em document)
                doc_markdown = res.get("document", {}).get("md_content") or res.get("md_content")
                    
                if doc_markdown:
                    output_dir = "./output"
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    Path(f"{output_dir}/saida_API.md").write_text(doc_markdown, encoding="utf-8")
                    print(f"[API MICROSERVIÇO] Resposta salva na máquina local em {output_dir}/saida_API.md!")
                    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO FATAL: Falha de conexão. O seu container de Docker está realmente ligado?")
    except Exception as e:
        print(f"Ocorreu um problema ao enviar para a API: {e}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_teste = os.path.join(BASE_DIR, "..", "docs", "Caratinga.pdf")
    
    # processar_documento_pdf(pdf_teste)
    
    processar_via_api_docker(pdf_teste)