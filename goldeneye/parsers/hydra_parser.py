"""
goldeneye/parsers/hydra_parser.py
Parser de resultados do Hydra.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
GREEN = Style(color="#00FF7F")
GREY = Style(color="#666666")


def display_hydra_results(results: List[Dict]):
    """Exibe resultados do Hydra."""
    console.print(f"\n[gold1]═══ RESULTADOS HYDRA ═══[/gold1]")
    
    if not results:
        console.print(f"\n[green][+] Nenhuma credencial encontrada.[/green]")
        return
    
    found = [r for r in results if r.get("found")]
    
    if found:
        console.print(f"\n[red][!] {len(found)} CREDENCIAIS ENCONTRADAS![/red]\n")
        for r in found:
            console.print(f"[red]  [CRITICO] {r['target']}:{r['port']} ({r['service']})[/red]")
            console.print(f"[red]  {r['output']}[/red]\n")
    else:
        console.print(f"\n[green][+] Nenhuma credencial encontrada.[/green]")
