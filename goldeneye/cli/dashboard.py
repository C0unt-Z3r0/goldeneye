"""
goldeneye/cli/dashboard.py
Dashboard de Risco - Score visual no terminal.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from rich.align import Align
from rich.text import Text

console = Console()

GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
GREEN = Style(color="#00FF7F")
YELLOW = Style(color="#FFFF00")
CYAN = Style(color="#00CED1")
ORANGE = Style(color="#FF4500", bold=True)
GREY = Style(color="#666666")


def show_dashboard(project_name: str, target: str, nmap_data=None, 
                   nuclei_results=None, zap_results=None):
    """Exibe dashboard de risco."""
    
    console.clear()
    
    # HEADER
    console.print(Panel(
        Align.center(
            "GOLDENEYE DASHBOARD\n"
            f"{project_name} | {target}"
        ),
        border_style=GOLD,
        padding=(1, 2),
    ))
    
    # SCORE DE RISCO
    total_vulns = (len(nuclei_results or []) + len(zap_results or []))
    
    if total_vulns == 0:
        score = 0
        color = "green"
        level = "BAIXO"
    elif total_vulns < 5:
        score = 4
        color = "yellow"
        level = "MEDIO"
    elif total_vulns < 10:
        score = 7
        color = "#FF4500"
        level = "ALTO"
    else:
        score = 9
        color = "red"
        level = "CRITICO"
    
    bar = "█" * score + "░" * (10 - score)
    
    score_text = Text()
    score_text.append(f"RISCO: {level}\n\n", style=color)
    score_text.append(f"{bar}\n", style=color)
    score_text.append(f"{score}/10", style=color)
    
    score_panel = Panel(
        Align.center(score_text),
        border_style=color,
        padding=(1, 2),
    )
    console.print(score_panel)
    
    # ESTATISTICAS
    open_ports = 0
    if nmap_data:
        for h in nmap_data.get("hosts", []):
            for p in h.get("ports", []):
                if p["state"] == "open":
                    open_ports += 1
    
    stats = Table(show_header=False, box=None, padding=(0, 3))
    stats.add_column(style=GOLD)
    stats.add_column(style=CYAN)
    stats.add_row("Portas Abertas", str(open_ports))
    stats.add_row("Nuclei Vulns", str(len(nuclei_results or [])))
    stats.add_row("ZAP Vulns", str(len(zap_results or [])))
    stats.add_row("Total Vulns", str(total_vulns))
    
    console.print(Panel(stats, title="Estatisticas", border_style=GREY, padding=(1, 2)))
    
    # TOP VULNERABILIDADES
    if zap_results:
        console.print("\nTop Vulnerabilidades:")
        for r in (zap_results or [])[:5]:
            sev = r.get("severity", "Info")
            name = r.get("name", "N/A")[:50]
            icon = "[red]●[/red]" if "Crit" in sev or "High" in sev else "[yellow]●[/yellow]"
            console.print(f"  {icon} {name}")
    
    console.print()
