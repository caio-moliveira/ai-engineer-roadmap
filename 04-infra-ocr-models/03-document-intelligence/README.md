# 🏭 Módulo 8: Document Intelligence em Produção

> **Goal:** Processar 1 milhão de páginas sem chorar.  
> **Status:** Engenharia de Sistemas Distribuídos.

## 1. Assincronia é Lei
OCR demora. GPT-4o Vision demora.
- **Síncrono (API):** O usuário faz upload e espera o loading girar por 40 segundos. Timeout. Falha.
- **Assíncrono (Job):**
    1. Usuário faz Upload -> Recebe "Job ID 123".
    2. Servidor joga arquivo no S3.
    3. Servidor joga mensagem no SQS.
    4. Worker (Lambda/EC2) pega mensagem, processa OCR, salva no Vector DB.
    5. Front-end faz polling ou recebe WebSocket: "Processamento Concluído".

## 2. Idempotência
E se o worker morrer no meio do processamento da página 50 de 100?
O sistema deve ser capaz de **recomeçar** sem duplicar as primeiras 49 páginas no banco.
- Use `file_hash` como chave de deduplicação.

## 3. DLQ (Dead Letter Queue)
Arquivos corrompidos vão travar seus workers.
Se um arquivo falhar 3 vezes, mova-o para uma DLQ e alerte um humano. Não deixe ele entupir a fila principal.

## 4. Segurança (PII)
Documentos têm CPF, Endereço, Salário.
- **Redaction:** Use bibliotecas (Presidio da Microsoft) para mascarar PII *antes* de enviar para o GPT-4 ou Vector DB.
- Nunca treine/fine-tune em dados com PII não tratado.

## 🧱 Checklist de Produção
- [ ] O pipeline é 100% assíncrono?
- [ ] Existe uma DLQ configurada?
- [ ] Detectamos e rejeitamos arquivos zip bomb / maliciosos?
- [ ] O custo está sendo monitorado por página?
- [ ] Estamos mascarando PII sensível?

## 🎓 Graduação
Você completou o Bloco 4.
Você agora sabe a diferença entre "rodar um modelo" e "operar uma infraestrutura de IA".

**Próximo Bloco: [Fine-Tuning](../../05-fine-tuning)**
