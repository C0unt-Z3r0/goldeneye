"""
goldeneye/cli/main.py
Entry point principal do Goldeneye Security Assessment Assistant.
"""

import typer
from goldeneye.cli.banner import show_banner
from goldeneye.cli.menu import main_menu
from goldeneye.cli.session import Session

app = typer.Typer(
    name="goldeneye",
    help="Goldeneye - Security Assessment Assistant",
    add_completion=False,
    invoke_without_command=True,
)


@app.callback()
def main():
    """Inicia o Goldeneye no modo interativo."""
    session = Session()

    show_banner()
    session.display_status()

    while True:
        try:
            choice = main_menu()

            if choice == "0":
                session.goodbye()
                break
            elif choice == "1":
                session.new_project()
            elif choice == "2":
                session.resume_project()
            elif choice == "3":
                session.generate_report()
            elif choice == "4":
                session.settings()
            elif choice == "5":
                session.about()
            else:
                session.invalid_option()

        except KeyboardInterrupt:
            session.goodbye()
            break
        except EOFError:
            session.goodbye()
            break


if __name__ == "__main__":
    app()
