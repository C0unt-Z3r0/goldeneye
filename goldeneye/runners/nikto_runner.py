"""
goldeneye/runners/nikto_runner.py
Nikto - scanner web rapido.
"""

import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()
DEFAULT_TIMEOUT_SECONDS = 1800


def run_nikto(target_url: str, output_dir: Path) -> List[Dict]:
    """Executa Nikto em uma URL."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = target_url.replace("://", "_").replace("/", "_").replace(":", "_")[:50]
    output_file = output_dir / f"nikto_{slug}.txt"
    
    cmd = ["nikto", "-h", target_url, "-o", str(output_file), "-Format", "csv"]
    
    console.print(f"\n[cyan][*] Nikto em {target_url}...[/cyan]")
    
    results = []
    try:
        output_file.unlink(missing_ok=True)
        process = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=DEFAULT_TIMEOUT_SECONDS, check=False,
        )
        for line in process.stdout.splitlines():
            line = line.strip()
            if line and "+" in line and any(
                term in line.lower()
                for term in ["vulnerab", "outdated", "interesting", "header", "directory", "file", "cookie"]
            ):
                console.print(f"[yellow]  {line}[/yellow]")
                results.append({"finding": line, "url": target_url})
        if process.returncode != 0:
            console.print(f"[yellow][!] Nikto terminou com código {process.returncode}.[/yellow]")

        if results:
            console.print(f"[green][+] {len(results)} descobertas![/green]")
        else:
            console.print(f"[grey][*] Nenhuma descoberta relevante.[/grey]")
            
    except subprocess.TimeoutExpired:
        console.print(f"[red][!] Nikto excedeu {DEFAULT_TIMEOUT_SECONDS}s; resultado inconclusivo.[/red]")
    except FileNotFoundError:
        console.print("[red][!] Nikto nao encontrado. Instale: sudo apt install nikto[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_nikto_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa Nikto em lote."""
    all_results = []
    for target in targets:
        results = run_nikto(target, output_dir)
        all_results.extend(results)
    return all_results
