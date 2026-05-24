# 🛠️ Aula 3: Pipeline — Planejamento e Dataset

> **Objetivo:** Tudo que acontece antes do `trainer.train()`.
> **Pergunta-chave:** Como garantir que mais da metade do sucesso do FT esteja resolvida antes de uma única GPU rodar?

A primeira metade do pipeline real de fine-tuning. PRD, escolha do modelo, schema de output, geração sintética com Claude, validação automática de cobertura. Mais da metade do sucesso de um FT está aqui — não no treino.

> 🔗 **Repositório do projeto:** [`caio-moliveira/ai-engineer-fine-tuning-example`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example)
> O documento técnico completo (com troubleshooting e apêndices) está em [`docs/CURSO_FINE_TUNING.md`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example/blob/main/docs/CURSO_FINE_TUNING.md).

---

## 1. O PRD — congelando decisões antes do código

Um **Product Requirements Document** simples, escrito antes da primeira linha de código, evita a armadilha clássica do FT: ficar reabrindo decisões de design durante a implementação. No nosso projeto, ele consolida sete decisões críticas:

| Decisão | Valor | Razão |
|---------|-------|-------|
| Modelo base | `Qwen/Qwen2.5-Coder-1.5B-Instruct` | Pequeno (cabe em qualquer GPU), variante Coder excelente em JSON, instruct-tuned, decente em pt-BR |
| Técnica | LoRA puro (PEFT + Transformers) | Sem Unsloth (incompatibilidade Windows), sem bitsandbytes |
| Precisão | bf16 | RTX 3060 (Ampere) suporta nativo, sem risco de overflow do fp16 |
| Dataset | 500 exemplos sintéticos | Suficiente para tarefa estruturada; com 425 de treino atingimos 89% exact-match |
| Gerador | Claude Haiku via Anthropic API | Qualidade alta, custo baixo (~USD 2-3 total) |
| Schema | Lista flat de objetos, 7 campos | Define o contrato do output — decisão mais crítica do projeto |
| Negativos | ~18% do dataset | Para o modelo aprender a devolver `[]` quando não há lei |

> ✅ **Princípio:** decisões congeladas em PRD evitam mudar design durante a implementação. Se algo precisar mudar, **mude o PRD primeiro**, então o código.

---

## 2. Escolha do modelo base — o que pesar

Cinco critérios em ordem de importância:

1. **Cabe na sua GPU?** Regra de bolso para LoRA em bf16: `VRAM ≈ params × 2 bytes × 1.5`. Qwen 1.5B em bf16: ~4 GB. Folga confortável em GPU de 12 GB.
2. **Conhece bem o idioma?** Modelos majoritariamente em inglês (Phi, Mistral antigo) têm pt-BR fraco. Qwen 2.5 e Llama 3.x são bons. Teste **antes** de treinar.
3. **Tem variante especializada para sua tarefa?** JSON/código → variante "Coder". Diálogo → "Instruct". Análise → "Chat".
4. **É open-weights com licença permissiva?** Llama tem restrições; Qwen 2.5 é Apache 2.0; Mistral mudou políticas. Cheque antes de produção comercial.
5. **Tem suporte ativo nas libs?** Compatibilidade com HuggingFace Transformers, PEFT, llama.cpp (para deploy GGUF posterior).

### Alternativas que consideramos

| Modelo | Pró | Contra |
|--------|-----|--------|
| **Qwen2.5-Coder-1.5B-Instruct** ✅ | Coder = ótimo em JSON; pt-BR decente; Apache 2.0 | Conhecimento jurídico zero — mas é o que vamos ensinar |
| Llama-3.2-1B | Marca forte, ótimo em pt-BR | Sem variante Coder; licença Meta restritiva |
| Phi-3.5-mini | Pequeno e rápido | pt-BR mais fraco; menos comunidade |
| Qwen2.5-1.5B (sem Coder) | Mesmas vantagens, mais geral | Coder dá vantagem mensurável em output estruturado |

---

## 3. Schema de output — o contrato

O **schema é o contrato** entre o modelo treinado e quem vai consumir. Decisões aqui se propagam para tudo: geração de dataset, métricas de avaliação, integração no app cliente. Defina *antes* de gerar a primeira linha do dataset.

```json
[
  {
    "tipo_lei": "LEI",
    "num_lei":  "8666",
    "ano_lei":  "1993",
    "artigo":   "37",
    "paragrafo": null,
    "inciso":    "XXI",
    "alinea":    null
  }
]
```

### Regras críticas do schema

- **Sempre lista**, mesmo com 0 ou 1 item. Nunca `null`, nunca objeto solto. *Por quê:* consumidor itera sem casos especiais.
- **Todos os valores são string ou `null`**. Nunca inteiro, nunca string vazia. *Por quê:* string vazia e null carregam significados diferentes; mistura confunde o modelo.
- **Vocabulário fechado para `tipo_lei`**: 21 valores válidos (CF, LEI, LC, DEC, etc.). *Por quê:* impossível alucinar tipo novo.
- **Formatos canônicos**: `num_lei` só dígitos (`"8666"` não `"8.666"`); `inciso` sempre romano maiúsculo; `alinea` sempre minúscula.

> 💡 **Princípio fundamental:** quanto mais estrito o schema, mais o modelo **memoriza padrões consistentes** e menos alucina. Cada chave opcional ou valor "às vezes" enfraquece o aprendizado. Vale ser quase paranoico aqui.

---

## 4. Estratégia structure-first — invertendo a anotação

O caminho tradicional para criar dataset de extração é: pegar textos reais, contratar anotadores, validar. Caro, lento, sujeito a viés do anotador. Nós invertemos:

```
PASSO 1: amostrar a ESTRUTURA          (amostrador.py)
           ↓ "vou citar Lei 8666/93 art 37 XXI + CF art 37 caput"
PASSO 2: Claude redige o PARÁGRAFO      (gerar_dataset.py)
           ↓ prompt: "escreva um acórdão citando: …", 4 estilos rotacionados
PASSO 3: validar a COBERTURA            (validador.py)
           ↓ apelidos das leis aparecem no texto? se não → descarta
PASSO 4: par (texto, JSON) → exemplo de treino com ground truth POR DESIGN
```

**Vantagens:**
- Ground truth é construído *por design*, não por anotação.
- Distribuição de quais leis, quantos campos, quais combinações fica controlada.
- Negativos (texto sem lei) são triviais de gerar.
- Custo escala bem: **~USD 0.005 por exemplo** com Claude Haiku.

### O catálogo curado de leis

Cada lei no catálogo ([`src/catalogo_leis.py`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example/blob/main/src/catalogo_leis.py)) tem:

```python
{
    "tipo_lei": "LEI",
    "num_lei": "8666",
    "ano_lei": "1993",
    "apelidos": ["Lei nº 8.666/93", "Lei de Licitações", ...],
    "peso": 10,                          # frequência relativa na amostragem
    "artigos_validos": ["3", "6", "22", "37"],  # artigos reais
}
```

Três campos fazem trabalho importante:
- **`peso`**: define quais leis aparecem mais (Constituição Federal peso 20, decretos raros peso 1-3). Amostragem ponderada reflete distribuição real.
- **`apelidos`**: formas que o texto pode citar a lei. Usados depois para validar cobertura.
- **`artigos_validos`**: evita gerar "Lei 8.666 art. 999" (que não existe).

---

## 5. Amostragem ponderada — como decidir a distribuição

O dataset tem que refletir a distribuição esperada de uso real, não ser "balanceado" no sentido ingênuo.

### Distribuição de quantos campos por dispositivo

| Combinação | % | Exemplo |
|------------|---|---------|
| Só lei | 25% | "Lei 8.666 de 1993" |
| Lei + artigo | 30% | "art. 37 da CF" |
| Lei + artigo + parágrafo | 15% | "art. 37, §1º" |
| Lei + artigo + inciso | 20% | "art. 5º, XXII, CF" |
| Lei + artigo + parágrafo + inciso | 7% | "art. 5º, §2º, III" |
| Lei + artigo + inciso + alínea | 3% | "art. 195, IV, b" |

### Negativos — 18% sem nenhuma lei

Negativos são o detalhe mais frequentemente esquecido em datasets de extração. **Sem eles, o modelo aprende que todo texto jurídico cita lei** e alucina referências em parágrafos neutros.

```
Escreva UM parágrafo de texto jurídico no estilo {estilo} que
NÃO cite nenhuma lei, decreto, súmula, código ou dispositivo legal.
Pode mencionar princípios gerais, posições doutrinárias, jurisprudência
genérica, mas nunca uma referência específica.
```

O par fica: `(texto sem lei, [])`. O modelo aprende a devolver lista vazia, e nas métricas medimos **FP em negativos**. No nosso resultado: 0%.

### Reprodutibilidade

```python
import random, os
random.seed(int(os.environ.get("SEED", "3407")))
```

O número `3407` vem de tradição ([David Picard, 2021](https://arxiv.org/abs/2109.08203), meio brincadeira meio sério). Use qualquer seed fixo — o importante é que seja reproduzível.

---

## 6. Loop de geração com Claude

O script [`src/gerar_dataset.py`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example/blob/main/src/gerar_dataset.py) implementa o loop principal:

```python
for _ in range(meta_de_exemplos):
    if random.random() < PERC_NEGATIVOS:        # 0.18
        prompt = construir_prompt_negativo()
        ground_truth = []
    else:
        dispositivos, estilo = amostrar_paragrafo()
        prompt = construir_prompt_redacao(dispositivos, estilo)
        ground_truth = dispositivos

    paragrafo = chamar_claude(prompt)            # anthropic.messages.create

    if validar_cobertura(paragrafo, dispositivos):
        salvar_jsonl({
            "prompt": paragrafo,
            "completion": json.dumps(ground_truth, ensure_ascii=False),
        })
    else:
        continue  # descarta e tenta outra; até 3 retries por exemplo
```

### Detalhes que importam na engenharia do script

- **Append incremental** em `data/dataset.jsonl`, não acumula em memória. Você não quer perder 400 exemplos por um KeyboardInterrupt.
- **Resumível**: se cair, recomeça contando linhas existentes no arquivo.
- **Rate limit defensivo**: `time.sleep(0.3)` entre chamadas, retry exponencial em 429.
- **Print de progresso** a cada 10 exemplos.
- **Split 85/15 train/test** ao final, com seed determinística.

| Métrica | Valor |
|---------|-------|
| Exemplos gerados | **500** |
| Tempo total | **~30 min** |
| Custo Claude Haiku | **USD 2-3** |
| Split train/test | **85/15** |

---

## 7. Validação de cobertura — o filtro automático

Claude às vezes "criativa demais" e escreve um parágrafo que não cita uma das leis pedidas. Sem filtro, esse par `(texto, ground_truth)` vira ruído: o modelo aprende a inventar referências. Daí [`src/validador.py`](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example/blob/main/src/validador.py):

```python
def validar_cobertura(paragrafo: str, dispositivos: list[dict]) -> bool:
    """
    Para cada lei do ground truth, pelo menos UM dos seus apelidos
    deve aparecer no texto (normalizado: lowercase, sem acentos, sem pontuação).
    """
    texto_norm = normalizar(paragrafo)

    for disp in dispositivos:
        lei = buscar_no_catalogo(disp["tipo_lei"], disp["num_lei"])
        apelidos_norm = [normalizar(a) for a in lei["apelidos"]]

        if not any(ap in texto_norm for ap in apelidos_norm):
            return False

    return True
```

> ✅ **Por que isso é poderoso:** você consegue um ground truth *garantidamente verdadeiro* sem revisão manual. Cada exemplo que entra no `dataset.jsonl` passou pelo filtro. Difícil de replicar com anotação humana em larga escala.

---

## 8. O que vai estar no `train.jsonl`

Formato final, uma linha por exemplo:

```jsonl
{"prompt": "Em decisão recente, o STF reafirmou que a Lei nº 8.666/93, art. 37, XXI, exige licitação pública…", "completion": "[{\"tipo_lei\":\"LEI\",\"num_lei\":\"8666\",\"ano_lei\":\"1993\",\"artigo\":\"37\",\"paragrafo\":null,\"inciso\":\"XXI\",\"alinea\":null}]"}
{"prompt": "O princípio da legalidade impõe limites ao poder de polícia…", "completion": "[]"}
```

No fim desta aula você tem:

- Um **PRD** com decisões congeladas
- Um **modelo base** escolhido com justificativa
- Um **schema** definido formalmente
- `data/train.jsonl` com ~425 exemplos validados
- `data/test.jsonl` com ~75 exemplos para avaliação posterior

---

## 📚 Referências da aula

- **Repositório do projeto.** *ai-engineer-fine-tuning-example*. — [github.com/caio-moliveira/ai-engineer-fine-tuning-example](https://github.com/caio-moliveira/ai-engineer-fine-tuning-example)
- **Wang et al. (2022).** *Self-Instruct: Aligning Language Models with Self-Generated Instructions*. — [arxiv.org/abs/2212.10560](https://arxiv.org/abs/2212.10560)
- **Taori et al. (2023).** *Stanford Alpaca: An Instruction-following LLaMA Model*. — [github.com/tatsu-lab/stanford_alpaca](https://github.com/tatsu-lab/stanford_alpaca)
- **Picard (2021).** *Torch.manual_seed(3407) is all you need*. — [arxiv.org/abs/2109.08203](https://arxiv.org/abs/2109.08203)
- **Qwen team.** *Qwen2.5 Technical Report*. — [arxiv.org/abs/2412.15115](https://arxiv.org/abs/2412.15115)
- **Anthropic.** *Claude API — Messages Reference*. — [docs.anthropic.com/en/api/messages](https://docs.anthropic.com/en/api/messages)

---

## ⏭️ Próximo passo

Dataset pronto. Hora de treinar, avaliar e fazer deploy.
Vá para **[Aula 4: Treino, Avaliação e Deploy Local](../04-train-deploy)**.
