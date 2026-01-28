# ⚡ Módulo 5: Hardware & Performance Fundamentals

> **Goal:** Não quebrar o banco.  
> **Status:** Onde a mágica encontra a física.

## 1. VRAM is King
Esqueça TFLOPS. O gargalo é **Memory Bandwidth**.
Um modelo de 70 bilhões de parâmetros (Llama-3-70B) em FP16 precisa de ~140GB de VRAM só para carregar.
- **A100 (80GB):** Cabe metade.
- **H100 (80GB):** Cabe metade.
- **RTX 4090 (24GB):** Nem sonhando.

## 2. Quantização: Int8/Int4
Para rodar 70B em hardware "mortal", usamos quantização.
- **FP16:** 140GB
- **INT8:** 70GB (Cabe em 1x A100)
- **INT4:** 35GB (Cabe em 2x 4090)

**Tradeoff:** INT4 tem perda de qualidade quase imperceptível para tarefas gerais, mas pode falhar em raciocínio complexo.

## 3. Unit Economics (Custo de Inferência)
A métrica que importa é: **$ / 1M tokens**.
- **GPT-4o:** ~$5.00
- **Llama-3-70B (Self-Host AWS):** ~$0.50 (se você tiver 100% de utilização).
- **Llama-3-70B (Self-Host AWS):** ~$50.00 (se você tiver 1% de utilização).

> **Alerta:** Self-hosting só é mais barato se você tiver **tráfego massivo e constante** para manter a GPU ocupada.

## 🧠 Mental Model: "Aluguel vs Hipoteca"
- **API (Token-based):** Uber. Você paga pelo km rodado. Caro por km, mas zero custo parado.
- **Self-Host (GPU):** Carro Próprio. Você paga a parcela todo mês, usando ou não. Só vale a pena se rodar muito.

## ⏭️ Próximo Passo
Vamos falar de dados sujos.
Vá para **[Módulo 6: Fundamentos de OCR](../06-ocr-fundamentals)**.
