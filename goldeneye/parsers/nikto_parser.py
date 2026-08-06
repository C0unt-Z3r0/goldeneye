"""Parser Nikto."""
from typing import List, Dict
from rich.console import Console
from rich.style import Style

console = Console()
RED = Style(color="#DC143C", bold=True)
YELLOW = Style(color="#FFFF00")
GREEN = Style(color="#00FF7F")
GREY = Style(color="#666666")


def display_nikto_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Nenhuma descoberta Nikto.[/green]")
        return
    
    console.print(f"\n[yellow]═══ RESULTADOS NIKTO ═══[/yellow]")
    console.print(f"[cyan]Total: {len(results)} descobertas[/cyan]\n")
    
    for r in results:
        finding = r.get("finding", "")
        if "vulnerab" in finding.lower() or "outdated" in finding.lower():
            console.print(f"[red]  ● {finding}[/red]")
        elif "interesting" in finding.lower() or "header" in finding.lower():
            console.print(f"[yellow]  ● {finding}[/yellow]")
        else:
            console.print(f"[grey]  ● {finding}[/grey]")
