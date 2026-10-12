"""Smoke test: todo script de todo módulo roda em replay, sem chave e sem rede (RF-03)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

BLOCK = Path(__file__).resolve().parents[1]
MODULES = [
    "01-decision-fundamentals",
    "02-choice-routing",
    "03-noul-detection-verification",
    "04-score-ranking",
    "05-calibration-evaluation",
]
SKIP = {"05_replay_record.py"}  # grava: precisa de rede por definição

SCRIPTS = [f"{m}/{p.name}" for m in MODULES for p in sorted((BLOCK / m).glob("[0-9][0-9]_*.py")) if p.name not in SKIP]
SCRIPTS += ["01-decision-fundamentals/01_http_direct.py laya", "01-decision-fundamentals/02_sdk_first_call.py laya"]
SCRIPTS += ["06-final-project-hybrid-agent/main.py --lote --comparar"]


@pytest.mark.parametrize("script", SCRIPTS)
def test_script_roda_em_replay(script, tmp_path):
    path, *argv = script.split()
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}  # sem chave nenhuma
    env |= {"DECISION_PROVIDER": "replay", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "MPLBACKEND": "Agg",
            "LAYA_BASE_URL": "http://127.0.0.1:9"}  # porta fechada: se tentar a rede, falha
    proc = subprocess.run(
        [sys.executable, str(BLOCK / path), *argv],
        cwd=(BLOCK / path).parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
    )
    assert proc.returncode == 0, f"{script} falhou:\n{proc.stdout[-2000:]}\n{proc.stderr[-3000:]}"
    assert "pulando" not in proc.stdout, f"{script} pulou um alvo por falta de gravação:\n{proc.stdout[-2000:]}"
