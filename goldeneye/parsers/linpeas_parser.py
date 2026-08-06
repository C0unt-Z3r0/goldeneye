"""Parser LinPEAS."""
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
YELLOW = Style(color="#FFFF00")
GREY = Style(color="#666666")


def display_linpeas_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Nenhuma vulnerabilidade de privilegios.[/green]")
        return
    
    console.print(f"\n[red]═══ PRIVILEGE ESCALATION ═══[/red]")
    console.print(f"[cyan]Total: {len(results)} descobertas[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Severidade", width=10)
    table.add_column("Descoberta", max_width=80)
    
    critical = [r for r in results if r.get("severity") == "CRITICAL"]
    high = [r for r in results if r.get("severity") == "HIGH"]
    medium = [r for r in results if r.get("severity") == "MEDIUM"]
    
    for r in critical + high + medium:
        sev = r.get("severity", "MEDIUM")
        style = "[red]CRITICAL[/red]" if sev == "CRITICAL" else "[yellow]HIGH[/yellow]" if sev == "HIGH" else "[grey]MEDIUM[/grey]"
        table.add_row(style, r.get("finding", "")[:80])
    
    console.print(table)
    
    console.print(f"\n[red]● CRITICAL: {len(critical)}[/red]")
    console.print(f"[yellow]● HIGH: {len(high)}[/yellow]")
    console.print(f"[grey]● MEDIUM: {len(medium)}[/grey]")
