from __future__ import annotations

import html
import json
from pathlib import Path


def write_dashboard(summary_path: str | Path, output_path: str | Path) -> Path:
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    rows = []
    for group in summary["groups"]:
        t = group["treatment"]
        label = " / ".join(t[key] for key in ("model", "topology", "memory", "strategy", "context"))
        values = (label, group["n"], group["task_success_rate"], group["task_success_ci95"], group["tool_call_accuracy"], group["hallucination_rate"], group["recovery_rate"], group["mean_tokens"], group["mean_latency_ms"], group["mean_cost_usd"])
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in values) + "</tr>")
    warning = "SIMULAÇÃO: resultados fixture não são evidência empírica." if summary["simulated"] else "Execução de modelo real. Verifique logs e versões."
    document = f"""<!doctype html><html lang=\"pt-BR\"><meta charset=\"utf-8\"><title>Long-Horizon Reliability</title>
<style>body{{font-family:system-ui;max-width:1500px;margin:3rem auto;padding:0 1rem;color:#172033}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}td,th{{padding:.55rem;border-bottom:1px solid #d6dce5;text-align:left}}th{{background:#edf2f8}}.notice{{padding:1rem;background:#fff4d7;border-left:4px solid #c58500}}</style>
<h1>Long-Horizon Agent Reliability</h1><p class=\"notice\">{warning}</p><p>{summary['runs']} runs · schema {summary['schema_version']}</p>
<table><thead><tr><th>Tratamento</th><th>n</th><th>Sucesso</th><th>IC 95%</th><th>Precisão tool</th><th>Alucinações/run</th><th>Recuperação</th><th>Tokens</th><th>Latência ms</th><th>Custo USD</th></tr></thead><tbody>{''.join(rows)}</tbody></table></html>"""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output
