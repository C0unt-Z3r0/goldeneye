"""
goldeneye/runners/nuclei_runner.py
Executor do Nuclei - scanner de vulnerabilidades baseado em templates.
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()


def run_nuclei(
    targets: List[str],
    output_dir: Path,
    severity: str = "critical,high,medium",
    tags: Optional[str] = None,
) -> Optional[Path]:
    """
    Executa Nuclei nos alvos.
    
    Args:
        targets: lista de URLs ou IPs
        output_dir: diretorio para salvar JSON
        severity: critical,high,medium,low,info
        tags: ex: cve,mysql,apache,exposure
    """
    if not targets:
        console.print("[yellow][!] Sem alvos para scan.[/yellow]")
        return None
    
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "nuclei_results.json"
    
    # Salvar targets em arquivo
    targets_path = output_dir / "nuclei_targets.txt"
    with open(targets_path, "w") as f:
        f.write("\n".join(targets))
    
    cmd = [
        "/usr/local/bin/nuclei",
        "-l", str(targets_path),
        "-json",
        "-o", str(json_path),
        "-severity", severity,
        "-silent",
        "-timeout", "10",
        "-retries", "1",
    ]
    
    if tags:
        cmd.extend(["-tags", tags])
    
    console.print(f"\n[cyan][*] Executando Nuclei em {len(targets)} alvos...[/cyan]")
    console.print(f"[grey]    Severidade: {severity}[/grey]")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if json_path.exists() and json_path.stat().st_size > 0:
            with open(json_path) as f:
                count = sum(1 for _ in f)
            console.print(f"[green][+] Nuclei concluido! {count} vulnerabilidades encontradas.[/green]")
            return json_path
        else:
            console.print("[green][+] Nuclei concluido! Nenhuma vulnerabilidade encontrada.[/green]")
            return json_path
            
    except FileNotFoundError:
        console.print("[red][!] Nuclei nao encontrado. Instale: go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest[/red]")
        return None
    except subprocess.TimeoutExpired:
        console.print("[yellow][!] Nuclei timeout (10min)[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red][!] Erro Nuclei: {e}[/red]")
        return None
