"""
goldeneye/runners/gobuster_runner.py
Gobuster - fuzzing de diretorios e arquivos.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

# Wordlist padrao
WORDLIST_DIR = "/usr/share/wordlists/dirb/common.txt"
WORDLIST_BIG = "/usr/share/wordlists/dirb/big.txt"


def run_gobuster(
    target_url: str,
    output_dir: Path,
    wordlist: str = None,
    mode: str = "dir",
    extensions: str = "php,html,txt,js,zip,backup,bak",
    threads: int = 20,
) -> List[Dict]:
    """Executa Gobuster em uma URL."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    slug = target_url.replace("://", "_").replace("/", "_").replace(":", "_")[:50]
    output_file = output_dir / f"gobuster_{slug}.txt"
    
    # Wordlist
    wl = wordlist or WORDLIST_DIR
    if not Path(wl).exists():
        wl = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
    if not Path(wl).exists():
        console.print("[yellow][!] Wordlist nao encontrada. Usando lista basica...[/yellow]")
        # Criar wordlist basica
        basic = output_dir / "basic_wordlist.txt"
        with open(basic, "w") as f:
            f.write("\n".join(["admin", "login", "wp-admin", "backup", "test", 
                               "dev", "api", "images", "css", "js", "includes", 
                               "uploads", "tmp", ".git", ".env", "config"]))
        wl = str(basic)
    
    cmd = [
        "gobuster", mode,
        "-u", target_url,
        "-w", wl,
        "-o", str(output_file),
        "-t", str(threads),
        "-q",
    ]
    
    if mode == "dir" and extensions:
        cmd.extend(["-x", extensions])
    
    # Lidar com servidores que redirecionam tudo (wildcard)
    cmd.extend(["--wildcard", "--exclude-length", "310"])
    
    console.print(f"\n[cyan][*] Gobuster ({mode}) em {target_url}...[/cyan]")
    console.print(f"[grey]    Wordlist: {wl}[/grey]")
    console.print(f"[grey]    Threads: {threads}[/grey]")
    
    results = []
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            line = line.strip()
            if line and "Status:" in line:
                console.print(f"[green]  {line}[/green]")
                # Parse: /path (Status: 200) [Size: 1234]
                import re
                match = re.search(r'/(\S+)\s+\(Status:\s*(\d+)\)\s*\[Size:\s*(\d+)\]', line)
                if match:
                    results.append({
                        "path": match.group(1),
                        "url": f"{target_url}/{match.group(1)}",
                        "status": int(match.group(2)),
                        "size": int(match.group(3)),
                    })
        
        process.wait()
        
        if results:
            console.print(f"[green][+] {len(results)} diretorios/arquivos encontrados![/green]")
        else:
            console.print(f"[grey][*] Nenhum resultado.[/grey]")
            
    except FileNotFoundError:
        console.print("[red][!] Gobuster nao encontrado. Instale: sudo apt install gobuster[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_gobuster_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa Gobuster em lote."""
    all_results = []
    
    for target in targets:
        results = run_gobuster(target, output_dir)
        all_results.extend(results)
    
    return all_results
