"""
goldeneye/runners/ffuf_runner.py
FFUF - Fuzzing web ultra-rapido.
"""

import subprocess, json
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()
WORDLIST = "/usr/share/wordlists/dirb/common.txt"


def run_ffuf(
    target_url: str,
    output_dir: Path,
    wordlist: str = None,
    extensions: str = "php,html,txt,js,zip,backup",
    threads: int = 40,
    match_codes: str = "200,204,301,302,307,401,403,405",
) -> List[Dict]:
    """Executa FFUF em uma URL."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = target_url.replace("://", "_").replace("/", "_").replace(":", "_")[:40]
    output_file = output_dir / f"ffuf_{slug}.json"
    
    wl = wordlist or WORDLIST
    if not Path(wl).exists():
        wl = "/usr/share/seclists/Discovery/Web-Content/common.txt"
    
    cmd = [
        "ffuf", "-u", f"{target_url}/FUZZ",
        "-w", wl,
        "-o", str(output_file), "-of", "json",
        "-t", str(threads),
        "-mc", match_codes,
        "-e", f".{extensions}" if extensions else "",
        "-s",
    ]
    
    console.print(f"\n[cyan][*] FFUF em {target_url}/...[/cyan]")
    console.print(f"[grey]    Wordlist: {wl} | Threads: {threads}[/grey]")
    
    results = []
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            line = line.strip()
            if line:
                console.print(f"[green]  {line}[/green]")
        process.wait()
        
        if output_file.exists() and output_file.stat().st_size > 0:
            with open(output_file) as f:
                data = json.load(f)
                for r in data.get("results", []):
                    results.append({
                        "url": r.get("url", ""),
                        "status": r.get("status", 0),
                        "size": r.get("length", 0),
                        "words": r.get("words", 0),
                        "lines": r.get("lines", 0),
                    })
        
        if results:
            console.print(f"[green][+] {len(results)} diretorios/arquivos encontrados![/green]")
        else:
            console.print(f"[grey][*] Nenhum resultado.[/grey]")
            
    except FileNotFoundError:
        console.print("[red][!] FFUF nao encontrado. Instale: sudo apt install ffuf[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_ffuf_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa FFUF em lote."""
    all_results = []
    for target in targets:
        results = run_ffuf(target, output_dir)
        all_results.extend(results)
    return all_results
