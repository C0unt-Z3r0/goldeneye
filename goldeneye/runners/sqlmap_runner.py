"""
goldeneye/runners/sqlmap_runner.py
Executor do SQLMap - deteccao de SQL Injection.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()


def run_sqlmap(
    target_url: str,
    output_dir: Path,
    crawl_depth: int = 2,
    risk: int = 1,
    level: int = 1,
) -> Optional[Path]:
    """
    Executa SQLMap em uma URL.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Slug para nome do arquivo
    slug = target_url.replace("://", "_").replace("/", "_").replace(":", "_").replace(".", "_")[:50]
    output_path = output_dir / f"sqlmap_{slug}.txt"
    
    cmd = [
        "sqlmap",
        "-u", target_url,
        "--batch",
        "--random-agent",
        f"--crawl={crawl_depth}",
        f"--risk={risk}",
        f"--level={level}",
        "--output-dir", str(output_dir),
        "--threads", "4",
    ]
    
    console.print(f"\n[cyan][*] SQLMap em {target_url}...[/cyan]")
    console.print(f"[grey]    Risk={risk} Level={level} Crawl={crawl_depth}[/grey]")
    
    try:
        with open(output_path, "w") as f:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            
            for line in process.stdout:
                f.write(line)
                # Mostrar progresso
                if "identified the following" in line.lower():
                    console.print(f"[yellow][!] {line.strip()}[/yellow]")
                elif "vulnerable" in line.lower() and "parameter" in line.lower():
                    console.print(f"[red][!] {line.strip()}[/red]")
            
            process.wait()
        
        if output_path.exists() and output_path.stat().st_size > 0:
            # Verificar se encontrou algo
            with open(output_path) as f:
                content = f.read()
                if "is vulnerable" in content.lower() or "identified" in content.lower():
                    console.print(f"[green][+] SQLMap encontrou vulnerabilidades![/green]")
                else:
                    console.print(f"[green][+] SQLMap concluido - sem vulnerabilidades.[/green]")
            return output_path
        
    except FileNotFoundError:
        console.print("[red][!] SQLMap nao encontrado. Instale: sudo apt install sqlmap[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro SQLMap: {e}[/red]")
    
    return None


def run_sqlmap_batch(
    targets: List[str],
    output_dir: Path,
) -> List[Dict]:
    """Executa SQLMap em lote."""
    results = []
    
    for target in targets:
        output = run_sqlmap(target, output_dir)
        if output:
            # Parse simples do output
            with open(output) as f:
                content = f.read()
            
            if "is vulnerable" in content.lower():
                results.append({
                    "url": target,
                    "vulnerable": True,
                    "output_file": str(output),
                })
    
    return results
