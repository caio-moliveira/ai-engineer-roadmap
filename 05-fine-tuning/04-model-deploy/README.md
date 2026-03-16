# 🚀 Módulo 8: Deploy & Inferência Pós-Treino

> **Goal:** Servir o modelo customizado.  
> **Status:** Onde o Adapter brilha.

## 1. LoRA Adapters no vLLM
Você não precisa subir um servidor vLLM dedicado de 70GB para cada cliente.
O vLLM suporta **Multi-LoRA Serving**.
- Servidor: Carrega o Llama-3-70B Base (1 vez).
- Request A: `model="cliente_juridico"` -> vLLM aplica Adapter A on-the-fly.
- Request B: `model="cliente_medico"` -> vLLM aplica Adapter B on-the-fly.
**Latência extra:** Quase zero.

## 2. Canary Deployment
Nunca troque o modelo base por um finetunado de uma vez.
Mande 1% do tráfego para o modelo novo.
Monitore:
- Taxa de erro (JSON inválido?)
- Tamanho da resposta (Ficou verboso?)
- Feedback do usuário (Thumbs down?).

## 3. Rollback
Se o modelo novo começar a alucinar:
Em vLLM, basta parar de enviar requests com o parâmetro `lora_name`. O modelo base continua lá, intacto.

## 🧠 Mental Model: "Hot Swapping"
Graças aos Adapters, trocar o comportamento do modelo em produção é tão rápido quanto trocar uma variável de ambiente. Não requer restart do servidor.

## ⏭️ Próximo Passo
O que pode dar errado a longo prazo?
Vá para **[Módulo 9: Riscos, Falhas & Manutenção](../09-risks-maintenance)**.
