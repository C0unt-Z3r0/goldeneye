"""
goldeneye/parsers/nuclei_parser.py
Parser de JSON do Nuclei.
"""

import json
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()

GOLD = Style(color="#FFD700", bold=True)
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
YELLOW = Style(color="#FFFF00")
RED = Style(color="#DC143C", bold=True)
GREY = Style(color="#666666")


def parse_nuclei_json(json_path: Path) -> List[Dict]:
    """Parseia o JSON do Nuclei."""
    results = []
    
    if not json_path.exists():
        return results
    
    with open(json_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                results.append({
                    "template": data.get("template-id", ""),
                    "name": data.get("info", {}).get("name", ""),
                    "severity": data.get("info", {}).get("severity", ""),
                    "description": data.get("info", {}).get("description", ""),
                    "url": data.get("matched-at", data.get("host", "")),
                    "type": data.get("type", ""),
                    "host": data.get("host", ""),
                    "cve": data.get("info", {}).get("classification", {}).get("cve-id", []),
                })
            except json.JSONDecodeError:
                pass
    
    return results


def display_nuclei_results(results: List[Dict]):
    """Exibe resultados do Nuclei em tabela."""
    
    if not results:
        console.print("[green][+] Nenhuma vulnerabilidade encontrada![/green]")
        return
    
    # Agrupar por severidade
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    results.sort(key=lambda x: severity_order.get(x.get("severity", "info").lower(), 99))
    
    console.print(f"\n[gold1]═══ RESULTADOS NUCLEI ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} vulnerabilidades[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Severidade", width=10)
    table.add_column("Vulnerabilidade", style=CYAN)
    table.add_column("URL", max_width=50)
    table.add_column("CVE")
    
    for r in results:
        sev = r.get("severity", "info").lower()
        if sev == "critical":
            sev_style = f"[red bold]{sev.upper()}[/red bold]"
        elif sev == "high":
            sev_style = f"[red]{sev}[/red]"
        elif sev == "medium":
            sev_style = f"[yellow]{sev}[/yellow]"
        elif sev == "low":
            sev_style = f"[green]{sev}[/green]"
        else:
            sev_style = f"[grey]{sev}[/grey]"
        
        cves = ", ".join(r.get("cve", [])[:3]) if r.get("cve") else "-"
        
        table.add_row(
            sev_style,
            r.get("name", "")[:60],
            r.get("url", "")[:50],
            cves,
        )
    
    console.print(table)
