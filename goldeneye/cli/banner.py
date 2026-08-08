"""
goldeneye/cli/banner.py
Tela principal do Goldeneye - tema 007.
"""

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.style import Style
from rich.box import Box, DOUBLE

console = Console()

GOLD = Style(color="#FFD700", bold=True)
GOLD_DIM = Style(color="#B8960F")
RED = Style(color="#DC143C", bold=True)
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
WHITE = Style(color="#FFFFFF")
GREY = Style(color="#666666")

GOLDEN_BOX = DOUBLE


def show_banner():
    """Exibe a tela principal do Goldeneye."""
    console.clear()

    logo = Text()
    logo.append("\n")
    logo.append(" G O L D E N E Y E  v 1 . 0", style=GOLD)
    logo.append("\n")
    logo.append("Security Assessment Assistant", style=GOLD_DIM)
    logo.append("\n\n")
    logo.append('"I see everything. I miss nothing."', style=Style(color="#CCCCCC", italic=True))

    logo_panel = Panel(
        Align.center(logo),
        border_style=GOLD_DIM,
        box=DOUBLE,
        padding=(1, 4),
    )

    scope = Text()
    scope.append("""
         ┌─────────────────────────┐
         │                         │
         │     ╔═══════════════╗    │
         │     ║               ║    │
         │     ║   ┌─────────┐ ║    │
         │     ║   │  ▄▄▄▄▄▄▄ │ ║    │
         │     ║   │  █     █ │ ║    │
         │     ║   │  █  O  █ │ ║    │
         │     ║   │  █     █ │ ║    │
         │     ║   │  ▀▀▀▀▀▀▀ │ ║    │
         │     ║   └─────────┘ ║    │
         │     ║               ║    │
         │     ╚═══════════════╝    │
         │                         │
         └─────────────────────────┘
    """, style=GOLD)

    console.print(logo_panel)
    console.print(Align.center(scope))
    console.print()


def show_easter_egg(command: str):
    """Easter eggs 007."""
    if command == "martini":
        console.print('\n🍸 [bold gold1]"Shaken, not stirred."[/bold gold1]')
        console.print("    — [italic]James Bond, 007[/italic]")
        console.print("[green][+] Modo agente ativado. Tocando tema 007... 🎵[/green]\n")
        try:
            from goldeneye.cli.sound import play_theme
            play_theme()
        except Exception:
            pass

    elif command == "bond":
        panel = Panel(
            Align.center(
                "Agente: 007\n"
                "Codigo: Goldeneye\n"
                "Status: Em missao\n"
                "Licenca para pentestar: CONCEDIDA\n\n"
                "Q Branch forneceu as ferramentas.\n"
                "M aguarda o relatorio."
            ),
            title="🕵️ DOSSIER DO AGENTE",
            border_style=GOLD_DIM,
            box=GOLDEN_BOX,
        )
        console.print(panel)
