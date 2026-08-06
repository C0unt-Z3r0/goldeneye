"""
goldeneye/runners/testssl_runner.py
TestSSL - analise de configuracao TLS/SSL.
"""

import subprocess
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()


def run_testssl(target: str, port: int = 443, output_dir: Path = None) -> List[Dict]:
    """Executa TestSSL em um alvo."""
    
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"testssl_{target}_{port}.txt"
    else:
        output_file = None
    
    cmd = ["testssl", "--json-pretty", f"{target}:{port}"]
    
    console.print(f"\n[cyan][*] TestSSL em {target}:{port}...[/cyan]")
    
    # Alerta sobre possiveis falsos positivos com CDN/Proxy
    console.print("[yellow][!] Se houver CDN/Proxy (Cloudflare, etc.), resultados podem conter falsos positivos.[/yellow]")
    console.print("[grey]    Para resultado preciso, teste diretamente o IP do servidor.[/grey]")
    
    results = []
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        vulns = {
            "Heartbleed": "VULNERABLE",
            "POODLE": "VULNERABLE", 
            "FREAK": "VULNERABLE",
            "DROWN": "VULNERABLE",
            "LOGJAM": "VULNERABLE",
            "BEAST": "VULNERABLE",
            "LUCKY13": "VULNERABLE",
            "RC4": "offered",
            "TLS 1.0": "offered",
            "TLS 1.1": "offered",
            "SWEET32": "VULNERABLE",
        }
        
        for line in process.stdout:
            line_stripped = line.strip()
            
            # Verificar vulnerabilidades conhecidas
            for vuln_name, vuln_indicator in vulns.items():
                if vuln_name.lower() in line_stripped.lower() and vuln_indicator.lower() in line_stripped.lower():
                    console.print(f"[red][!] {vuln_name}: VULNERAVEL[/red]")
                    results.append({
                        "target": f"{target}:{port}",
                        "vulnerability": vuln_name,
                        "severity": "HIGH",
                        "detail": line_stripped[:100],
                    })
            
            # Ciphers fracos
            if "cipher" in line_stripped.lower() and any(x in line_stripped.lower() for x in ["null", "anon", "export", "des", "rc2", "rc4"]):
                console.print(f"[yellow][*] Cipher fraco detectado[/yellow]")
                results.append({
                    "target": f"{target}:{port}",
                    "vulnerability": "Cipher Fraco",
                    "severity": "MEDIUM",
                    "detail": line_stripped[:100],
                })
        
        process.wait()
        
        if results:
            console.print(f"[red][!] {len(results)} problemas TLS/SSL encontrados![/red]")
        else:
            console.print(f"[green][+] Configuracao TLS parece segura.[/green]")
            
    except FileNotFoundError:
        console.print("[red][!] TestSSL nao encontrado. Instale: sudo apt install testssl.sh[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return results


def run_testssl_scan(targets: List[tuple], output_dir: Path) -> List[Dict]:
    """Executa TestSSL em lote. targets = [(host, port), ...]"""
    all_results = []
    for host, port in targets:
        results = run_testssl(host, port, output_dir)
        all_results.extend(results)
    return all_results
