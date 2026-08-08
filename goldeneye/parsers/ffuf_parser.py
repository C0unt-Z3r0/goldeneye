"""Parser FFUF."""
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C")
YELLOW = Style(color="#FFFF00")
CYAN = Style(color="#00CED1")
GREY = Style(color="#666666")


def display_ffuf_results(results: List[Dict]):
    if not results:
        console.print("\n[green][+] Nenhum diretorio/arquivo encontrado.[/green]")
        return
    
    console.print(f"\n[gold1]═══ RESULTADOS FFUF ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} itens[/cyan]\n")
    
    table = Table(border_style=GREY, show_header=True)
    table.add_column("Status", width=8)
    table.add_column("URL", style=CYAN, max_width=55)
    table.add_column("Tamanho")
    table.add_column("Palavras")
    
    results.sort(key=lambda x: x.get("status", 0))
    
    for r in results[:50]:
        status = r.get("status", 0)
        if status == 200: s = f"[green]{status}[/green]"
        elif status in [301, 302]: s = f"[yellow]{status}[/yellow]"
        elif status in [401, 403]: s = f"[red]{status}[/red]"
        else: s = str(status)
        
        size = r.get("size", 0)
        size_str = f"{size/1000:.1f}KB" if size>1000 else f"{size}B"
        
        table.add_row(s, r.get("url", "")[:55], size_str, str(r.get("words", 0)))
    
    console.print(table)
    if len(results) > 50:
        console.print(f"\n[grey][*] Mostrando 50 de {len(results)}.[/grey]")
