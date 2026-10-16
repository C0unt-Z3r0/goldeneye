"""
goldeneye/runners/testssl_runner.py
Execução e parsing estruturado do testssl.sh.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console

from goldeneye.parsers.testssl_parser import parse_testssl_json

console = Console()
DEFAULT_TIMEOUT_SECONDS = 900


def run_testssl(
    target: str,
    port: int = 443,
    output_dir: Optional[Path] = None,
) -> List[Dict]:
    """Executa testssl.sh e converte o JSON estruturado em achados.

    O scan é considerado malsucedido quando a ferramenta não existe, excede
    o timeout ou não produz JSON válido. Nesses casos, retorna lista vazia,
    mas informa o erro explicitamente — nunca declara o alvo seguro.
    """
    console.print(f"\n[cyan][*] TestSSL em {target}:{port}...[/cyan]")
    console.print(
        "[yellow][!] CDN/proxy pode afetar os resultados; confirme o escopo "
        "e a autorização antes de testar o alvo.[/yellow]"
    )

    safe_target = re.sub(r"[^A-Za-z0-9_.-]+", "_", target).strip("._") or "target"

    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / f"testssl_{safe_target}_{port}.json"
        return _run_and_parse(target, port, json_file)

    # Sem diretório de saída, mantém o JSON apenas durante o parsing.
    with tempfile.TemporaryDirectory(prefix="goldeneye-testssl-") as temp_dir:
        json_file = Path(temp_dir) / f"testssl_{safe_target}_{port}.json"
        return _run_and_parse(target, port, json_file)


def _run_and_parse(target: str, port: int, json_file: Path) -> List[Dict]:
    # Evita interpretar um JSON antigo como se fosse desta execução.
    try:
        json_file.unlink(missing_ok=True)
    except OSError as exc:
        console.print(f"[red][!] Não foi possível preparar o arquivo JSON de saída: {exc}[/red]")
        return []

    cmd = [
        "testssl",
        "--jsonfile-pretty",
        str(json_file),
        f"{target}:{port}",
    ]

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError:
        console.print(
            "[red][!] testssl não encontrado. Instale o testssl.sh antes de executar.[/red]"
        )
        return []
    except subprocess.TimeoutExpired:
        console.print(
            f"[red][!] TestSSL excedeu o timeout de {DEFAULT_TIMEOUT_SECONDS}s; "
            "o scan não foi considerado concluído.[/red]"
        )
        return []
    except OSError as exc:
        console.print(f"[red][!] Não foi possível executar testssl: {exc}[/red]")
        return []

    if process.returncode != 0:
        console.print(
            f"[yellow][!] testssl terminou com código {process.returncode}; "
            "os resultados serão aceitos somente se o JSON estiver válido.[/yellow]"
        )

    if not json_file.is_file():
        console.print(
            "[red][!] testssl não produziu o arquivo JSON esperado; "
            "não é possível concluir que o alvo está seguro.[/red]"
        )
        if process.stderr:
            console.print(f"[dim]{process.stderr.strip()[-1000:]}[/dim]")
        return []

    try:
        with json_file.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        results = parse_testssl_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        console.print(f"[red][!] Não foi possível interpretar o JSON do testssl: {exc}[/red]")
        return []

    if results:
        console.print(f"[red][!] {len(results)} achado(s) TLS/SSL extraído(s) do JSON.[/red]")
    elif process.returncode == 0:
        console.print(
            "[green][+] JSON válido: nenhum problema TLS/SSL acionável foi identificado.[/green]"
        )
    else:
        console.print(
            "[yellow][!] JSON válido, mas o scan terminou com erro; "
            "não classifique o alvo como seguro.[/yellow]"
        )

    return results


def run_testssl_scan(targets: List[tuple], output_dir: Path) -> List[Dict]:
    """Executa TestSSL em lote. targets = [(host, port), ...]."""
    all_results = []
    for host, port in targets:
        results = run_testssl(host, port, output_dir)
        all_results.extend(results)
    return all_results
