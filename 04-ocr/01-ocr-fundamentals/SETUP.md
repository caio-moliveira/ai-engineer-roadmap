# ⚙️ Guia de Instalação Oficial: Tesseract & EasyOCR

Para começarmos a colocar a mão na massa na prática de OCR, precisamos configurar nosso ambiente. 
Abaixo montamos o passo-a-passo minucioso para instalar os dois motores clássicos que usaremos ao longo da disciplina.

---

## 1. Instalando o Tesseract OCR

> **Atenção:** O Tesseract **não** é apenas uma biblioteca Python. Ele é um software C++ que roda direto no sistema operacional. O pacote que usamos no Python (`pytesseract`) é apenas um intermediário (wrapper) que envia o comando da imagem para o executável do seu PC ler. Portanto, você precisa instalar o software "core" primeiro.

### 🪟 Windows
1. Baixe o instalador mais recente, mantido pela Universidade de Mannheim, na página oficial de builds compilados: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Durante o processo de instalação do assistente, procure pela aba **"Additional language data (download)"**, expanda a árvore de opções e marque **"Portuguese"** para garantir que o modelo da língua portuguesa seja instalado junto.
3. **Passo Crítico (Variável de Ambiente):** Por padrão, ele é instalado em `C:\Program Files\Tesseract-OCR`. Você precisa adicionar esse diretório na variável `PATH` do seu Windows.
   * *Alternativa caso não queira mexer no PATH:* Você pdoe avisar o seu script Python exatamente onde o software está escondido adicionando a linha:
     `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
4. Instale o pacote Python usando o `uv`:
   ```bash
   uv add pytesseract
   ```

### 🐧 Linux (Ubuntu/Debian)
O processo no Linux é bem mais nativo e direto por linha de comando.
```bash
sudo apt update
sudo apt install tesseract-ocr
# Para instalar a capacidade de ler em português:
sudo apt install tesseract-ocr-por
```
1. Instale o pacote Python usando o `uv`:
   ```bash
   uv add pytesseract
   ```

### 🍎 macOS
Se você usa Mac, a melhor forma é utilizar o gerenciador Homebrew.
```bash
brew install tesseract
# Instala arquivos de modelo de linguagens adicionais (ex: 'por' para pt-br)
brew install tesseract-lang
```
1. Instale o pacote Python usando o `uv`:
   ```bash
   uv add pytesseract
   ```

---

## 2. Instalando o EasyOCR

Ao contrário do Tesseract, o EasyOCR é completamente construído e distribuído como pacote Python. Como ele processa as imagens usando Deep Learning debaixo dos panos (PyTorch), você tem a opção de rodá-lo pela sua Placa de Vídeo (GPU) ou pelo Processador comum (CPU).

### Passo 1: Configurar a fundação (PyTorch)
Antes de baixar o EasyOCR, nós sempre recomendamos que você garanta que o PyTorch está na sua máquina para evitar conflitos de versão pesados.
* Acesse o [Site Oficial do PyTorch](https://pytorch.org/get-started/locally/) para gerar o comando perfeito caso você tenha uma GPU Nvidia.
* **Instalação Padrão (Sem Placa de Vídeo dedicada - a mais comum):**
  ```bash
  uv add torch torchvision torchaudio
  ```

### Passo 2: O pacote core
Uma vez que a dependência de DL está resolvida, instale o EasyOCR no terminal:
```bash
uv add easyocr
```

### ⚠️ O que acontece no primeiro uso?
O EasyOCR usa pesos neurais pesados para adivinhar onde o texto está e qual letra é. 
Na primeira vez que você executar o script Python instanciando o Reader:
```python
import easyocr

# O Easy vai tentar encontrar e ativar o processamento paralelo (CUDA) se você tiver.
reader = easyocr.Reader(['pt', 'en']) 
```
A biblioteca fará um download automático dos modelos pré-treinados hospedados na nuvem e salvará localmente numa pasta oculta do seu usuário (geralmente `~/.EasyOCR/model`). Isso pode levar alguns minutos em conexões mais lentas — não ache que o código está travado, apenas tenha paciência para que a barra de progresso no terminal finalize. Nas vezes seguintes que você rodar o script, será instantâneo!
