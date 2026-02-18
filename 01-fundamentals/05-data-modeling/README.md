# Data Modeling & Structured Output

Este módulo foca em **Data Modeling** (modelagem de dados), uma competência essencial para Engenheiros de IA. Garantir que os dados que entram e saem dos seus sistemas (e especialmente dos LLMs) estejam estruturados e validados é o que diferencia uma "demo" de um produto robusto.

## 1. Fundamentos do Pydantic

O arquivo `01_pydantic_overview.py` consolida os conceitos fundamentais do **Pydantic v2**.

**Conceitos abordados:**
*   **Basic Fields**: Definição de campos obrigatórios, opcionais e defaults.
*   **Validators**: `@field_validator` para limpeza de dados e `@model_validator` para regras de negócio entre campos.
*   **Serialization**: Conversão de objetos para dicionários/JSON (`model_dump`, `model_dump_json`).
*   **Tipos Avançados**: Uso de `Enum`, `UUID`, `IPv4Address`, `HttpUrl`, `Decimal` para garantir integridade.

> 📚 **Documentação Oficial**: [Pydantic Docs](https://docs.pydantic.dev/latest/)

Para rodar este exemplo:
```bash
python 01_pydantic_overview.py
```

---

## 2. Structured Output com LangChain e FastAPI

A segunda parte deste módulo demonstra como forçar um LLM a responder em um formato estruturado (JSON) validado por um schema Pydantic. Isso é crucial para integrar IA em APIs, onde o frontend ou outros serviços esperam dados previsíveis.

### Estrutura dos Arquivos
*   `models.py`: Define o schema de saída (`CapitalData`) e entrada (`GenerateRequest`) usando Pydantic.
*   `endpoint.py`: Contém a lógica do LangChain. Utiliza o parâmetro `response_format` para garantir a estrutura.
*   `router.py` & `main.py`: Configuração da API FastAPI.

### Structured Output
No arquivo `endpoint.py`, utilizamos a capacidade nativa dos modelos modernos de seguir schemas.

```python
# Trecho do endpoint.py
agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="...",
    # O Pydantic Model é passado diretamente aqui!
    response_format=CapitalData
)
```

Isso garante que o retorno do agente não seja apenas um texto solto, mas um objeto `CapitalData` com campos tipados (`population: int`, `country: str`, etc.), facilitando a integração.

> 📚 **Referência Completa**: [LangChain Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)

### Rodando a API
Para iniciar o servidor FastAPI e testar o endpoint:

1.  Certifique-se de ter as dependências instaladas e o arquivo `.env` configurado.
2.  Execute:
    ```bash
    uv run uvicorn main:app --app-dir . --reload
    ```
3.  Acesse a documentação interativa em: `http://127.0.0.1:8000/docs`
