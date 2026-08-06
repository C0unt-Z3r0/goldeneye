"""
goldeneye/parsers/cme_parser.py
Parser de resultados do CrackMapExec.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C")
GREY = Style(color="#666666")


def display_cme_results(results: List[Dict]):
    """Exibe resultados do CME."""
    if not results:
        console.print("\n[green][+] Nenhum resultado critico encontrado.[/green]")
        return
    
    console.print(f"\n[gold1]═══ RESULTADOS CRACKMAPEXEC ═══[/gold1]")
    console.print(f"[cyan]Total: {len(results)} descobertas[/cyan]\n")
    
    for r in results:
        output = r.get("output", "")
        if "Pwn3d!" in output:
            console.print(f"[red][!] {r['target']}: {output}[/red]")
        elif "[+]" in output:
            console.print(f"[green][+] {r['target']}: {output}[/green]")
        else:
            console.print(f"[grey][*] {r['target']}: {output}[/grey]")
