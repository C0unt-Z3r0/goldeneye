"""
goldeneye/runners/nmap_runner.py
Executor do Nmap com timeout e validacao do resultado.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()
DEFAULT_TIMEOUT_SECONDS = 1800


def run_nmap(
    target: str,
    output_dir: Path,
    scan_type: str = "quick",
    ports: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Optional[Path]:
    """Executa Nmap com timeout; so aceita XML novo e retorno bem-sucedido."""
    if not target or target.startswith("-") or any(ch in target for ch in "\r\n\0"):
        console.print("[red][!] Alvo inválido; execução cancelada.[/red]")
        return None
    if timeout <= 0:
        raise ValueError("timeout deve ser maior que zero")

    output_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", target).strip("._") or "target"
    xml_path = output_dir / f"nmap_{scan_type}_{slug}.xml"

    scan_profiles = {
        "quick": ["-sV", "-sC", "-O", "--top-ports", "1000"],
        "full": ["-sV", "-sC", "-O", "-p", "1-65535"],
        "stealth": ["-sS", "-sV", "--top-ports", "1000", "-T2"],
    }
    if scan_type not in scan_profiles:
        console.print(f"[red][!] Tipo de scan inválido: {scan_type}[/red]")
        return None

    cmd = ["nmap", *scan_profiles[scan_type]]
    if ports and scan_type == "quick":
        cmd = [arg for arg in cmd if arg not in {"--top-ports", "1000"}]
    if os.environ.get("GOLDENEYE_ANON"):
        console.print("[yellow][!] GOLDENEYE_ANON não torna o tráfego anônimo; ele não oculta a origem do scan.[/yellow]")
    if ports == "top100":
        cmd.extend(["--top-ports", "100"])
    elif ports:
        if not re.fullmatch(r"[0-9,\\-]+", ports):
            console.print("[red][!] Formato de portas inválido.[/red]")
            return None
        cmd.extend(["-p", ports])
    cmd.extend(["-oX", str(xml_path), target])

    try:
        xml_path.unlink(missing_ok=True)
    except OSError as exc:
        console.print(f"[red][!] Não foi possível preparar o XML: {exc}[/red]")
        return None

    console.print(f"\n[gold1][*] Executando Nmap ({scan_type}) em {target}...[/gold1]")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task(f"[cyan]Scan em andamento (limite {timeout}s)...", total=None)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, check=False
            )
    except FileNotFoundError:
        console.print("[red][!] Nmap não encontrado. Instale o Nmap antes de executar.[/red]")
        return None
    except subprocess.TimeoutExpired:
        console.print(f"[red][!] Nmap excedeu o timeout de {timeout}s; resultado inconclusivo.[/red]")
        xml_path.unlink(missing_ok=True)
        return None
    except OSError as exc:
        console.print(f"[red][!] Não foi possível executar Nmap: {exc}[/red]")
        return None

    if result.returncode != 0:
        console.print(f"[red][!] Nmap terminou com código {result.returncode}; resultado não será aceito.[/red]")
        return None
    if not xml_path.is_file() or xml_path.stat().st_size == 0:
        console.print("[red][!] Nmap não produziu XML válido; resultado inconclusivo.[/red]")
        return None

    console.print("[green][+] Nmap concluído.[/green]")
    console.print(f"[grey]XML salvo em: {xml_path}[/grey]")
    return xml_path
