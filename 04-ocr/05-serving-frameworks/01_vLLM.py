from openai import OpenAI
from PIL import Image
import base64
from pathlib import Path
from io import BytesIO

# Cliente OpenAI apontando para seu vLLM local
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

# Caminho da imagem
BASE_DIR = Path(__file__).resolve().parent
arquivo = BASE_DIR / ".." / "docs" / "imagem.jpg"

# ===== REDUZ A IMAGEM =====
img = Image.open(arquivo)

# Mantém proporção e reduz tamanho máximo
img.thumbnail((768, 768))

# Salva em memória
buffer = BytesIO()
img.save(buffer, format="JPEG", quality=70)

# Converte para base64
image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

# ===== OCR =====
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-VL-3B-Instruct-AWQ",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extraia todo o texto da imagem."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ],
    max_tokens=500
)

print(response.choices[0].message.content)