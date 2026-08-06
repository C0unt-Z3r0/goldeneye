"""
goldeneye/parsers/msf_parser.py
Parser de resultados do searchsploit.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
CYAN = Style(color="#00CED1")
RED = Style(color="#DC143C", bold=True)
GREEN = Style(color="#00FF7F")
GREY = Style(color="#666666")


def display_msf_results(results: List[Dict]):
    """Exibe exploits encontrados."""
    if not results:
        console.print("\n[green][+] Nenhum exploit encontrado.[/green]")
        return
    
    console.print(f"\n[gold1]═══ EXPLOITS ENCONTRADOS ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} exploits[/cyan]\n")
    
    # Mostrar top 40
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Titulo", style=GOLD, max_width=60)
    table.add_column("Path", style=CYAN, max_width=30)
    
    for r in results[:40]:
        title = r.get("title", "N/A")
        path = r.get("path", "N/A")
        table.add_row(title, path)
    
    console.print(table)
    console.print(f"\n[grey][*] Mostrando top 40 de {len(results)} resultados.[/grey]")
