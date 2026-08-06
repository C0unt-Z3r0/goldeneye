"""
goldeneye/runners/cme_runner.py
CrackMapExec - enumeracao Windows/AD.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()


def run_cme(
    target: str,
    output_dir: Path,
    module: str = "smb",
    username: str = "",
    password: str = "",
) -> List[Dict]:
    """Executa CrackMapExec no alvo."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"cme_{target.replace('.', '_')}.txt"
    
    cmd = ["crackmapexec", module, target]
    
    if username:
        cmd.extend(["-u", username])
    if password:
        cmd.extend(["-p", password])
    
    console.print(f"\n[cyan][*] CrackMapExec ({module}) em {target}...[/cyan]")
    
    results = []
    try:
        with open(output_file, "w") as f:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                f.write(line)
                line = line.strip()
                if line:
                    console.print(f"[grey]  {line[:100]}[/grey]")
                    if "Pwn3d!" in line or "[+]" in line:
                        results.append({"target": target, "output": line, "success": True})
            process.wait()
        
        if results:
            console.print(f"[green][+] {len(results)} resultados![/green]")
        else:
            console.print(f"[grey][*] Sem resultados significativos.[/grey]")
            
    except FileNotFoundError:
        console.print("[red][!] CrackMapExec nao encontrado. Instale: sudo apt install crackmapexec[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_cme_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa CME em lote."""
    all_results = []
    for target in targets:
        # SMB Enum
        results = run_cme(target, output_dir, "smb")
        all_results.extend(results)
        
        # Se SMB respondeu, tentar RDP
        if any("445" in r.get("output", "") for r in results):
            run_cme(target, output_dir, "rdp")
        
        # WinRM
        run_cme(target, output_dir, "winrm")
    
    return all_results
