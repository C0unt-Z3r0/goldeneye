"""
goldeneye/discovery/probe.py
Verificacao de hosts vivos usando Httpx.
"""

import subprocess
import json
import tempfile
import os
from typing import List, Dict
from rich.console import Console

console = Console()


def probe_hosts(targets: List[str]) -> List[Dict]:
    """
    Verifica quais hosts estao vivos e respondendo HTTP/HTTPS.
    Captura stdout diretamente em vez de arquivo temporario.
    """
    results = []

    if not targets:
        return results

    # Limitar a 500 alvos por vez
    if len(targets) > 500:
        console.print(f"[yellow][!] Muitos alvos ({len(targets)}). Limitando aos primeiros 500.[/yellow]")
        targets = targets[:500]

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for t in targets:
                f.write(t + "\n")
            targets_path = f.name

        cmd = [
            "/usr/local/bin/httpx",
            "-l", targets_path,
            "-json",
            "-silent",
            "-timeout", "8",
            "-retries", "1",
            "-threads", "25",
            "-rate-limit", "10",
        ]

        console.print(f"[grey][*] Httpx: verificando hosts vivos ({len(targets)} alvos)...[/grey]")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        # Processar stdout linha por linha
        if result.stdout:
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    results.append({
                        "url": data.get("url", ""),
                        "status_code": data.get("status_code", 0),
                        "title": data.get("title", ""),
                        "tech": data.get("tech", []),
                        "webserver": data.get("webserver", ""),
                        "ip": data.get("host", ""),
                    })
                except json.JSONDecodeError:
                    pass

        # Tambem verificar stderr para debug
        if result.stderr and "WRN" not in result.stderr:
            console.print(f"[yellow][!] Httpx aviso: {result.stderr.strip()[:200]}[/yellow]")

        os.unlink(targets_path)

    except FileNotFoundError:
        console.print("[yellow][!] Httpx nao encontrado em /usr/local/bin/httpx[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[yellow][!] Httpx timeout (10min)[/yellow]")
    except Exception as e:
        console.print(f"[yellow][!] Httpx erro: {e}[/yellow]")

    return results
