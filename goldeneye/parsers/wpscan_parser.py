"""Parser WPScan."""
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C", bold=True)
GREY = Style(color="#666666")


def display_wpscan_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Nenhuma descoberta WPScan.[/green]")
        return
    
    console.print(f"\n[gold1]═══ RESULTADOS WPSCAN ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} descobertas[/cyan]\n")
    
    for r in results:
        finding = r.get("finding", "")
        if "[!]" in finding:
            console.print(f"[red]{finding}[/red]")
        elif "[+]" in finding:
            console.print(f"[green]{finding}[/green]")
        else:
            console.print(f"[grey]{finding}[/grey]")
