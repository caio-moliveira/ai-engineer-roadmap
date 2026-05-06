# Módulo 06 — Receipt OCR API (Projeto Final)

Uma API REST pronta para produção que processa imagens de recibos usando um pipeline de IA em dois estágios: **GLM-OCR** (via Ollama) para extração de texto e **GPT-4.1-mini** (via LangChain + OpenAI) para parsing estruturado. Os resultados são persistidos em SQLite e expostos por uma API CRUD completa com frontend mobile integrado.

---

## Arquitetura

```
Celular / Navegador
       │
       ▼
POST /receipts  (upload de imagem multipart)
       │
       ├─► Ollama  ──► GLM-OCR        →  texto OCR bruto
       │
       ├─► OpenAI  ──► GPT-4.1-mini   →  JSON estruturado
       │                                  { description, amount,
       │                                    purchase_time, location }
       ▼
  SQLite  (receipts.db)
       │
       ▼
  Resposta JSON  +  UI no navegador
```

---

## Stack de Tecnologias

| Camada | Ferramenta |
|--------|-----------|
| Framework de API | FastAPI |
| Modelo de OCR | GLM-OCR via Ollama |
| Modelo de parsing | GPT-4.1-mini via LangChain + OpenAI |
| Banco de dados | SQLite (stdlib `sqlite3`) |
| Validação de schema | Pydantic v2 |
| Frontend | HTML/JS vanilla servido pelo próprio FastAPI |

---

## Estrutura do Projeto

```
06-final-project/
├── main.py        # entry point: app FastAPI, lifespan, routers
├── database.py    # conexão SQLite e init do banco
├── schemas.py     # modelos Pydantic (ReceiptOut, ReceiptPatch)
├── crud.py        # operações de banco: get, insert, update, delete
├── service.py     # pipeline de IA: OCR (GLM-OCR) + parsing (GPT-4.1-mini)
├── router.py      # rotas HTTP REST — orquestra service + crud
├── frontend.py    # HTML do frontend mobile + rota GET /
├── receipts.db    # criado automaticamente na primeira execução
└── README.md
```

---

## Endpoints da API

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/` | Interface web mobile-friendly |
| `POST` | `/receipts` | Upload de imagem → OCR → parsing → salvar |
| `GET` | `/receipts` | Listar todos os recibos (mais recentes primeiro) |
| `GET` | `/receipts/{id}` | Buscar um recibo por ID |
| `PATCH` | `/receipts/{id}` | Atualizar qualquer campo |
| `DELETE` | `/receipts/{id}` | Deletar um recibo |
| `GET` | `/docs` | Swagger UI interativo |

---

## Schema do Banco de Dados

```sql
CREATE TABLE receipts (
    id            TEXT PRIMARY KEY,     -- UUID v4
    description   TEXT,                 -- o que foi comprado / nome da loja
    amount        REAL,                 -- valor total pago (float)
    purchase_time TEXT,                 -- data e hora em ISO 8601
    location      TEXT,                 -- endereço ou cidade/estado
    raw_text      TEXT,                 -- saída completa do OCR (para debug)
    created_at    TEXT NOT NULL         -- timestamp UTC em ISO 8601
);
```

---

## Configuração

### 1. Dependências

```bash
pip install fastapi uvicorn python-multipart ollama \
            langchain-openai langchain-core python-dotenv
```

### 2. Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou nesta pasta):

```env
OPENAI_API_KEY=sk-...
```

### 3. Ollama — baixar o GLM-OCR

```bash
ollama pull glm-ocr
```

### 4. Executar

```bash
python main.py
```

O servidor sobe em `http://0.0.0.0:8000`.

---

## Acessando pelo Celular

Desde que o celular esteja na **mesma rede Wi-Fi** que o computador:

1. Descubra seu IP local:
   ```bash
   # Windows
   ipconfig | findstr "IPv4"

   # Mac / Linux
   ifconfig | grep "inet "
   ```

2. Abra no navegador do celular:
   ```
   http://<seu-ip-local>:8000
   ```

3. Toque na área da câmera → câmera traseira abre → tire a foto → **Scan Receipt**.

> O atributo `capture="environment"` no input de arquivo abre diretamente a câmera traseira no Android e iOS, sem precisar escolher da galeria.

---

## Exemplo de Resposta

```json
{
  "id": "a3f2c1d0-...",
  "description": "Compra no Pão de Açúcar",
  "amount": 87.45,
  "purchase_time": "2026-05-06T14:32:00",
  "location": "Av. Paulista, 1000 — São Paulo, SP",
  "raw_text": "...",
  "created_at": "2026-05-06T17:00:00+00:00"
}
```

---

## Formatos de Imagem Suportados

`.png` `.jpg` `.jpeg` `.webp` `.bmp` `.tiff`

---

## Observações

- `receipts.db` é criado automaticamente na mesma pasta na primeira execução.
- O campo `raw_text` armazena a saída completa do GLM-OCR — útil para depurar problemas de extração.
- O endpoint PATCH atualiza apenas os campos fornecidos; os demais permanecem inalterados.
