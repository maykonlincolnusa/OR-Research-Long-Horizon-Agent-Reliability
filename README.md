# OR Research — Long-Horizon Agent Reliability

Pergunta central: **como arquitetura de memória, estratégia de planejamento e escolha de modelo afetam a confiabilidade de agentes autônomos em tarefas de engenharia de software de longo horizonte?**

Esta primeira versão é um laboratório **local, reprodutível e sem chaves de API**. O executor `fixture-*` simula agentes para validar o desenho experimental, logs e análise antes de conectar modelos reais. Seus números não são evidência empírica.

## Rodar localmente

```powershell
$env:PYTHONPATH = "src"
py -m unittest discover -s tests -v
py -m longhorizon validate --dataset data/benchmarks/seed_tasks.jsonl
py -m longhorizon run --config configs/experiment.local.json
py -m longhorizon analyze --results results/runs.jsonl --output results/summary.json
py -m longhorizon dashboard --summary results/summary.json --output results/dashboard.html
```

Cada rodada cria `runs.jsonl`, `events.jsonl` e `manifest.json`. O manifesto prende hashes do dataset e da configuração, versão do harness e runtime usado.

O protocolo está em [docs/research-protocol.md](docs/research-protocol.md) e o esqueleto do paper em [paper/outline.md](paper/outline.md).
