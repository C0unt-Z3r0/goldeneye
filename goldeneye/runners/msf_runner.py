"""
goldeneye/runners/msf_runner.py
Busca exploits via searchsploit.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()


def search_exploits(query: str) -> List[Dict]:
    """Busca exploits com searchsploit."""
    
    console.print(f"\n[cyan][*] Buscando: {query}...[/cyan]")
    
    results = []
    try:
        result = subprocess.run(
            ["searchsploit", "--disable-colour", query],
            capture_output=True, text=True, timeout=10,
        )
        
        # Parsear output do searchsploit
        in_table = False
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if "---" in line and "Exploit Title" in result.stdout:
                in_table = True
                continue
            if "Shellcodes:" in line:
                break
            if in_table and line and not line.startswith("-"):
                # Formato: Titulo | Caminho
                # Tentar split por múltiplos espaços
                parts = re.split(r'\s{2,}', line)
                if len(parts) >= 2:
                    results.append({
                        "title": parts[0].strip(),
                        "path": parts[-1].strip(),
                    })
        
        if results:
            console.print(f"[green][+] {len(results)} exploits para {query}[/green]")
            
    except FileNotFoundError:
        console.print("[red][!] searchsploit nao encontrado.[/red]")
    except Exception as e:
        console.print(f"[yellow][!] Erro: {e}[/yellow]")
    
    return results


def run_msf_scan(services: List[Dict], output_dir: Path) -> List[Dict]:
    """Busca exploits para cada servico."""
    
    all_exploits = []
    queries_done = set()
    
    for svc in services:
        product = svc.get("product", "")
        service = svc.get("service", "")
        
        if product and product not in queries_done:
            queries_done.add(product)
            all_exploits.extend(search_exploits(product))
        
        if service and service not in queries_done:
            queries_done.add(service)
            all_exploits.extend(search_exploits(service))
    
    # Deduplicar
    seen = set()
    unique = []
    for e in all_exploits:
        key = e["title"]
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    return unique
