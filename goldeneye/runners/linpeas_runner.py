"""
goldeneye/runners/linpeas_runner.py
LinPEAS - enumeracao de privilegios Linux.
"""

import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()

LINPEAS_PATH = "/usr/share/peass/linpeas/linpeas.sh"


def run_linpeas(output_dir: Path, target: str = "localhost") -> List[Dict]:
    """Executa LinPEAS e retorna descobertas criticas."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"linpeas_{target}.txt"
    
    console.print(f"\n[cyan][*] LinPEAS - enumerando privilegios...[/cyan]")
    console.print(f"[yellow][!] Isso pode levar 2-5 minutos...[/yellow]")
    
    results = []
    try:
        with open(output_file, "w") as f:
            process = subprocess.Popen(
                ["bash", LINPEAS_PATH, "-q", "-o", str(output_file)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            
            indicators = [
                ("Vulnerable to", "RED", "CRITICAL"),
                ("CVE-", "RED", "CRITICAL"), 
                ("SUID", "YELLOW", "HIGH"),
                ("writable", "YELLOW", "MEDIUM"),
                ("password", "RED", "CRITICAL"),
                ("root:", "RED", "CRITICAL"),
                ("sudo", "YELLOW", "HIGH"),
                ("capabilities", "YELLOW", "MEDIUM"),
                ("cron", "YELLOW", "MEDIUM"),
                ("docker", "YELLOW", "HIGH"),
            ]
            
            for line in process.stdout:
                line_stripped = line.strip()
                for keyword, color, severity in indicators:
                    if keyword.lower() in line_stripped.lower() and len(line_stripped) > 10:
                        if "not vulnerable" not in line_stripped.lower():
                            console.print(f"[{color.lower()}]  [{severity}] {line_stripped[:120]}[/{color.lower()}]")
                            results.append({
                                "finding": line_stripped[:200],
                                "severity": severity,
                                "target": target,
                            })
                            break
            
            process.wait()
        
        if results:
            console.print(f"\n[red][!] {len(results)} descobertas de privilegios![/red]")
        else:
            console.print(f"[green][+] Nenhuma elevacao de privilegio obvia.[/green]")
            
    except FileNotFoundError:
        console.print(f"[red][!] LinPEAS nao encontrado em {LINPEAS_PATH}[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results
