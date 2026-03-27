---
name: analise-financeira
description: Diretrizes e framework para análise financeira de investimentos, propostas comerciais e projetos. Use quando precisar avaliar viabilidade, calcular ROI, interpretar DRE/balanço ou comparar cenários financeiros.
---

# Skill: Análise Financeira de Negócios

## Visão Geral
Esta skill fornece o framework para análise financeira rigorosa de propostas, investimentos e projetos de negócios B2B. Use quando o usuário pedir avaliação de custo-benefício, ROI, ou viabilidade financeira.

## Quando Usar
- Análise de proposta comercial ou orçamento
- Avaliação de investimento em tecnologia ou infraestrutura
- Comparação de cenários (fazer vs. comprar, contratar vs. terceirizar)
- Interpretação de indicadores financeiros (EBITDA, margem, churn, LTV/CAC)

## Framework de Análise (Siga Esta Ordem)

### 1. Mapeamento de Custos
Categorize todos os custos:
- **CAPEX** (investimento único): licenças, implantação, hardware
- **OPEX** (recorrente): mensalidades, suporte, manutenção, pessoal adicional
- **Custos ocultos**: treinamento, migração de dados, downtime durante transição

### 2. Mapeamento de Benefícios
Quantifique em R$:
- Redução de horas manuais (horas × custo/hora do cargo)
- Redução de erros (valor médio de retrabalho × frequência)
- Ganho de receita (se aplicável)
- Redução de riscos (multas evitadas, incidentes prevenidos)

### 3. Cálculo dos Indicadores-Chave

**ROI (Return on Investment)**
```
ROI = ((Benefício Total - Custo Total) / Custo Total) × 100
Referência: ROI > 20% em 24 meses = VIÁVEL
```

**Payback Period**
```
Payback = Investimento Total / Benefício Mensal
Referência: Payback < 18 meses = ÓTIMO | < 36 meses = ACEITÁVEL
```

**TIR (Taxa Interna de Retorno)**
- Compare com o custo de capital da empresa (geralmente 15-25% a.a. no Brasil)

### 4. Análise de Sensibilidade
Sempre apresente 3 cenários:
- **Pessimista**: benefícios 30% menores, custos 20% maiores
- **Base**: valores estimados
- **Otimista**: benefícios 20% maiores, custos como estimados

## Benchmarks de Mercado (Brasil 2024-2025)

| Categoria | ROI Típico | Payback Típico |
|-----------|-----------|----------------|
| ERP para PMEs | 150-300% em 3 anos | 14-22 meses |
| Automação com IA | 200-500% em 2 anos | 6-14 meses |
| Migração Cloud | 100-200% em 3 anos | 18-30 meses |
| CRM B2B | 250-400% em 2 anos | 8-16 meses |

## Sinais de Alerta em Propostas
- ROI < 15% → questionar premissas ou negociar preço
- Payback > 36 meses → alto risco, exige garantias contratuais
- Benefícios baseados apenas em "estimativas do fornecedor" → solicitar cases comprovados
- Ausência de SLA → não assinar sem incluir cláusula de nível de serviço

## Formato de Saída Esperado
Estruture a análise em: **Resumo Executivo** (3 linhas) → **Detalhamento** → **Veredicto** (APROVAR / NEGOCIAR / REJEITAR) → **Próximos Passos**.
