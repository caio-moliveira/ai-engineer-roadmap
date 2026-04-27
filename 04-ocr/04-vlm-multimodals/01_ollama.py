from pathlib import Path
import tempfile
import fitz  # PyMuPDF
import ollama


MODEL = "qwen3-vl:8b"
#MODEL = "glm-ocr"


def ocr_image(image_path: Path, mode: str = "Text Recognition") -> str:
    """
    mode pode ser:
    - Text Recognition
    - Table Recognition
    - Figure Recognition
    """
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": f"{mode}: {image_path}",
                "images": [str(image_path)],
            }
        ],
        options={
            "temperature": 0,
            "num_ctx": 16384,
        },
    )

    return response["message"]["content"]


def pdf_to_page_images(pdf_path: Path, dpi: int = 200):
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)

    images = []

    for page_num, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image_path = temp_path / f"{pdf_path.stem}_page_{page_num:03d}.png"
        pix.save(image_path)
        images.append(image_path)

    return images, temp_dir


def ocr_pdf(pdf_path: Path, mode: str = "Text Recognition") -> str:
    page_images, temp_dir = pdf_to_page_images(pdf_path)

    try:
        results = []

        for i, image_path in enumerate(page_images, start=1):
            print(f"OCR página {i}/{len(page_images)}: {image_path.name}")
            text = ocr_image(image_path, mode=mode)
            results.append(f"\n\n# Página {i}\n\n{text}")

        return "".join(results)

    finally:
        temp_dir.cleanup()


def process_file(input_path: str, mode: str = "Text Recognition") -> str:
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    if path.suffix.lower() == ".pdf":
        return ocr_pdf(path, mode=mode)

    if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
        return ocr_image(path, mode=mode)

    raise ValueError(f"Formato não suportado: {path.suffix}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    arquivo = BASE_DIR / ".." / "docs" / "imagem.jpg"

    resultado = process_file(
        arquivo,
        mode="Text Recognition",
    )

    saida = Path(arquivo).with_suffix(".md")
    saida.write_text(resultado, encoding="utf-8")

    print(f"Resultado salvo em: {saida}")