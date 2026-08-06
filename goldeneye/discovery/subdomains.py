"""
goldeneye/discovery/subdomains.py
Descoberta de subdominios usando Amass e Subfinder.
"""

import subprocess
import json
import tempfile
import os
from typing import List
from rich.console import Console

console = Console()


def run_amass(domain: str) -> List[str]:
    """Executa Amass para enumerar subdominios."""
    subdomains = []
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        cmd = ["amass", "enum", "-passive", "-d", domain, "-json", temp_path]
        console.print(f"[grey][*] Amass: descobrindo subdominios...[/grey]")
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            with open(temp_path) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "name" in data:
                            subdomains.append(data["name"])
                    except json.JSONDecodeError:
                        pass

        os.unlink(temp_path)
    except FileNotFoundError:
        console.print("[yellow][!] Amass nao encontrado. Instale: go install github.com/owasp-amass/amass/v4/...@master[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[yellow][!] Amass timeout (5min)[/yellow]")
    except Exception as e:
        console.print(f"[yellow][!] Amass erro: {e}[/yellow]")

    return list(set(subdomains))


def run_subfinder(domain: str) -> List[str]:
    """Executa Subfinder para enumerar subdominios."""
    subdomains = []
    try:
        cmd = ["subfinder", "-d", domain, "-silent"]
        console.print(f"[grey][*] Subfinder: descobrindo subdominios...[/grey]")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            subdomains = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except FileNotFoundError:
        console.print("[yellow][!] Subfinder nao encontrado. Instale: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[yellow][!] Subfinder timeout (2min)[/yellow]")
    except Exception as e:
        console.print(f"[yellow][!] Subfinder erro: {e}[/yellow]")

    return subdomains


def discover_subdomains(domain: str) -> List[str]:
    """Orquestra descoberta de subdominios."""
    all_subdomains = set()

    all_subdomains.update(run_amass(domain))
    all_subdomains.update(run_subfinder(domain))

    all_subdomains.add(domain)
    all_subdomains.add(f"www.{domain}")

    return sorted(list(all_subdomains))
