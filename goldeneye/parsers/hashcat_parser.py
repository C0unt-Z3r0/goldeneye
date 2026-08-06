"""Parser Hashcat."""
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
RED = Style(color="#DC143C", bold=True)
GOLD = Style(color="#FFD700", bold=True)
GREY = Style(color="#666666")


def display_hashcat_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Nenhum hash quebrado.[/green]")
        return
    
    console.print(f"\n[red]═══ HASHES QUEBRADOS ═══[/red]")
    console.print(f"[cyan]Total: {len(results)} senhas recuperadas[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Hash", max_width=30)
    table.add_column("Senha", style=RED)
    
    for r in results:
        table.add_row(r.get("hash", "")[:30], r.get("password", ""))
    
    console.print(table)
