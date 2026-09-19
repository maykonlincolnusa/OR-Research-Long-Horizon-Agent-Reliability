# Protocolo de pesquisa v0.1

## Hipóteses

- H1: memória com orçamento melhora sucesso e recuperação em horizontes longos, com custo em tokens e latência.
- H2: planner-executor reduz chamadas inválidas versus ReAct quando há dependências entre etapas.
- H3: o efeito de memória varia por modelo e estratégia de contexto.

## Unidade experimental

Uma observação é `(task_id, tratamento, seed)`. O tratamento fixa modelo, topologia, memória, estratégia e contexto. Use as mesmas tarefas e seeds em todas as células pareadas.

## Fatores

| Fator | Níveis iniciais |
| --- | --- |
| Modelo | `fixture-gpt-like`, `fixture-open-small` (depois, reais) |
| Topologia | `single-agent`, `multi-agent` |
| Memória | `none`, `bounded` |
| Estratégia | `react`, `planner-executor` |
| Contexto | `full`, `sliding`, `summary` |

## Desfechos

Primário: `task_success`. Secundários: alucinações, precisão de tool-call, tokens, latência, custo e recuperação após falha injetada. `recovered_after_failure` é calculado somente entre runs com falha injetada.

## Logs e reprodutibilidade

Cada run recebe `run_id`. `results/events.jsonl` guarda eventos estruturados com `run_id`, `task_id`, timestamp lógico e payload sanitizado. Não registre prompts proprietários, variáveis de ambiente, tokens de acesso ou diffs completos sem uma política de retenção.

`results/manifest.json` registra hashes SHA-256 do dataset e da configuração. Um resultado sem manifesto correspondente não deve entrar na análise confirmatória.

Uma configuração representa uma rodada e sobrescreve seus três artefatos de saída. Para preservar uma rodada anterior, use caminhos `output`, `event_log` e `manifest` em um novo diretório, por exemplo `results/2026-09-19-baseline/`.

## Regras contra viés

- Congele benchmark, prompts, versões e orçamento antes da rodada confirmatória.
- Separe desenvolvimento de teste final.
- Armazene commit, ambiente, configuração, logs, patch e saída do avaliador.
- Reporte médias, ICs e tamanhos de efeito; compare tratamentos de maneira pareada por tarefa/seed.

O executor fixture tem parâmetros artificiais. Apenas análise e schema devem ser reaproveitados para resultados reais.
