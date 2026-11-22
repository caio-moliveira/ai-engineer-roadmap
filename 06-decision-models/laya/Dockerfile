# Laya (Convai Innovations, Apache 2.0) servindo o protocolo /v1/systemone do Jev, em CPU.
# Uso, da raiz do repositório:  docker compose --profile decision up laya
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    USE_TF=0 \
    TORCH_DISABLE_NATIVE_JIT=1

# torch CPU primeiro, para o pip não puxar a build CUDA (vários GB).
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.10.0 \
 && pip install "laya[serve]==0.4.6"

ENV LAYA_HOST=0.0.0.0 \
    LAYA_PORT=8001 \
    LAYA_MODELS=multilingual \
    LAYA_DEFAULT_MODEL=multilingual \
    LAYA_PRELOAD=1 \
    HF_HOME=/cache/huggingface

EXPOSE 8001
HEALTHCHECK --interval=15s --timeout=5s --start-period=180s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health')"
CMD ["laya-serve"]
