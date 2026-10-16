"""
goldeneye/runners/wpscan_runner.py
WPScan - Scanner WordPress.
"""

import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()
DEFAULT_TIMEOUT_SECONDS = 1800


def run_wpscan(target_url: str, output_dir: Path) -> List[Dict]:
    """Executa WPScan em uma URL."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"wpscan_{target_url.replace('://', '_').replace('/', '_')[:40]}.txt"
    
    cmd = [
        "wpscan",
        "--url", target_url,
        "--format", "json",
        "--output", str(output_file),
        "--no-update",
        "--random-user-agent",
        "--ignore-main-redirect",
    ]
    
    console.print(f"\n[cyan][*] WPScan em {target_url}...[/cyan]")
    
    results = []
    try:
        output_file.unlink(missing_ok=True)
        process = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=DEFAULT_TIMEOUT_SECONDS, check=False,
        )
        for line in process.stdout.splitlines():
            line = line.strip()
            if line:
                if "[+]" in line or "[!]" in line:
                    console.print(f"[green]  {line}[/green]")
                    results.append({"finding": line, "url": target_url})
                elif "[i]" in line:
                    console.print(f"[grey]  {line}[/grey]")
        if process.returncode != 0:
            console.print(f"[yellow][!] WPScan terminou com código {process.returncode}.[/yellow]")

        if results:
            console.print(f"[green][+] {len(results)} descobertas![/green]")
        else:
            console.print(f"[grey][*] Nenhuma descoberta critica.[/grey]")
            
    except subprocess.TimeoutExpired:
        console.print(f"[red][!] WPScan excedeu {DEFAULT_TIMEOUT_SECONDS}s; resultado inconclusivo.[/red]")
    except FileNotFoundError:
        console.print("[red][!] WPScan nao encontrado. Instale: sudo apt install wpscan[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_wpscan_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa WPScan em lote."""
    all_results = []
    for target in targets:
        results = run_wpscan(target, output_dir)
        all_results.extend(results)
    return all_results
