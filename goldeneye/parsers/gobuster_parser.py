"""
goldeneye/parsers/gobuster_parser.py
Parser de resultados do Gobuster.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C", bold=True)
YELLOW = Style(color="#FFFF00")
GREY = Style(color="#666666")


def display_gobuster_results(results: List[Dict]):
    """Exibe resultados do Gobuster."""
    if not results:
        console.print("\n[green][+] Nenhum diretorio/arquivo encontrado.[/green]")
        return
    
    # Agrupar por status
    console.print(f"\n[gold1]═══ RESULTADOS GOBUSTER ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} itens encontrados[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Status", width=8)
    table.add_column("Path", style=CYAN, max_width=50)
    table.add_column("Tamanho")
    
    # Ordenar: 200 primeiro, depois 301, 403, etc
    results.sort(key=lambda x: (x.get("status", 0) != 200, x.get("status", 0)))
    
    for r in results[:50]:
        status = r.get("status", 0)
        if status == 200:
            s = f"[green]{status}[/green]"
        elif status in [301, 302]:
            s = f"[yellow]{status}[/yellow]"
        elif status == 403:
            s = f"[red]{status}[/red]"
        else:
            s = str(status)
        
        size = r.get("size", 0)
        if size > 1000000:
            size_str = f"{size/1000000:.1f}MB"
        elif size > 1000:
            size_str = f"{size/1000:.1f}KB"
        else:
            size_str = f"{size}B"
        
        table.add_row(s, r.get("path", ""), size_str)
    
    console.print(table)
    
    if len(results) > 50:
        console.print(f"\n[grey][*] Mostrando 50 de {len(results)}.[/grey]")
