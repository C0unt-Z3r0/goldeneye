"""Parser TestSSL."""
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
YELLOW = Style(color="#FFFF00")
GREY = Style(color="#666666")


def display_testssl_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Configuracao TLS/SSL segura.[/green]")
        return
    
    console.print(f"\n[red]═══ PROBLEMAS TLS/SSL ═══[/red]")
    console.print(f"[cyan]Total: {len(results)} problemas[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Alvo")
    table.add_column("Vulnerabilidade", style=RED)
    table.add_column("Severidade")
    table.add_column("Detalhe", max_width=50)
    
    for r in results:
        sev = r.get("severity", "MEDIUM")
        sev_style = f"[red]{sev}[/red]" if sev == "HIGH" else f"[yellow]{sev}[/yellow]"
        
        table.add_row(
            r.get("target", ""),
            r.get("vulnerability", ""),
            sev_style,
            r.get("detail", "")[:50],
        )
    
    console.print(table)
