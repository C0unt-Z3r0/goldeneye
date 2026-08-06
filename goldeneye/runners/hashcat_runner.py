"""
goldeneye/runners/hashcat_runner.py
Hashcat - quebra de hashes offline.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

# Modos de hash comuns
HASH_MODES = {
    "MD5": "0",
    "SHA1": "100",
    "SHA256": "1400",
    "SHA512": "1700",
    "NTLM": "1000",
    "MySQL": "300",
    "MySQL5": "200",
    "bcrypt": "3200",
    "SHA256crypt": "7400",
    "SHA512crypt": "1800",
    "WPA2": "22000",
}


def run_hashcat(
    hash_file: Path,
    output_dir: Path,
    hash_type: str = "auto",
    wordlist: str = None,
    attack_mode: int = 0,
) -> List[Dict]:
    """Executa Hashcat em um arquivo de hashes."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"hashcat_cracked_{hash_file.stem}.txt"
    
    cmd = ["hashcat", "-m", HASH_MODES.get(hash_type, "0"), "-a", str(attack_mode),
           str(hash_file), "-o", str(output_file), "--potfile-disable"]
    
    if wordlist and attack_mode == 0:
        cmd.extend([wordlist])
    elif attack_mode == 3:
        cmd.extend(["?a?a?a?a?a?a"])  # Bruteforce 6 chars
    
    console.print(f"\n[cyan][*] Hashcat ({hash_type})...[/cyan]")
    
    results = []
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            line = line.strip()
            if "Cracked" in line or "Recovered" in line:
                console.print(f"[red][!] {line}[/red]")
            elif "Progress" in line:
                console.print(f"[grey]  {line}[/grey]")
        
        process.wait()
        
        if output_file.exists() and output_file.stat().st_size > 0:
            with open(output_file) as f:
                cracked = f.read().strip().splitlines()
            results = [{"hash": h.split(":")[0] if ":" in h else h[:20],
                        "password": h.split(":")[1] if ":" in h else "cracked",
                        "target": str(hash_file)} for h in cracked if h]
            console.print(f"[red][!] {len(results)} hashes quebrados![/red]")
        else:
            console.print(f"[grey][*] Nenhum hash quebrado.[/grey]")
            
    except FileNotFoundError:
        console.print("[red][!] Hashcat nao encontrado.[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results
