"""
goldeneye/parsers/zap_parser.py
Parser de resultados do OWASP ZAP.
"""

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


def display_zap_results(results: List[Dict]):
    """Exibe resultados do ZAP."""
    if not results:
        console.print("[green][+] Nenhuma vulnerabilidade encontrada pelo ZAP.[/green]")
        return
    
    # Ordenar por severidade
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    results.sort(key=lambda x: severity_order.get(x.get("severity", "Info"), 99))
    
    console.print(f"\n[gold1]═══ RESULTADOS OWASP ZAP ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} vulnerabilidades[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Sev", width=6)
    table.add_column("Vulnerabilidade", style=CYAN, max_width=40)
    table.add_column("URL", max_width=40)
    table.add_column("CWE")
    
    for r in results:
        sev = r.get("severity", "Info")
        if sev == "Critical":
            sev_style = "[red bold]CRIT[/red bold]"
        elif sev == "High":
            sev_style = "[red]HIGH[/red]"
        elif sev == "Medium":
            sev_style = "[yellow]MED[/yellow]"
        elif sev == "Low":
            sev_style = "[green]LOW[/green]"
        else:
            sev_style = "[grey]INFO[/grey]"
        
        table.add_row(
            sev_style,
            r.get("name", "")[:40],
            r.get("url", "")[:40],
            str(r.get("cwe", "-")),
        )
    
    console.print(table)
