"""
goldeneye/parsers/sqlmap_parser.py
Parser de output do SQLMap.
"""

from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
GREEN = Style(color="#00FF7F")
GREY = Style(color="#666666")


def parse_sqlmap_output(output_path: Path) -> Dict:
    """Parseia output do SQLMap."""
    result = {
        "vulnerable": False,
        "params": [],
        "db_type": "",
        "payloads": [],
    }
    
    if not output_path.exists():
        return result
    
    with open(output_path) as f:
        content = f.read()
    
    if "is vulnerable" in content.lower():
        result["vulnerable"] = True
    
    # Extrair parâmetros vulneráveis
    for line in content.splitlines():
        if "parameter '" in line.lower() and "is vulnerable" in line.lower():
            # Ex: Parameter 'id' is vulnerable
            import re
            match = re.search(r"Parameter '(\w+)'", line)
            if match:
                result["params"].append(match.group(1))
    
    # Tipo de banco
    import re
    db_match = re.search(r"back-end DBMS: (\w+)", content)
    if db_match:
        result["db_type"] = db_match.group(1)
    
    return result


def display_sqlmap_results(results: List[Dict], targets: List[str]):
    """Exibe resultados do SQLMap."""
    console.print(f"\n[gold1]═══ RESULTADOS SQLMAP ═══[/gold1]")
    
    found = False
    for target in targets:
        for result in results:
            if result.get("url") == target and result.get("vulnerable"):
                found = True
                console.print(f"\n[red][!] SQL INJECTION ENCONTRADA![/red]")
                console.print(f"[red]    URL: {target}[/red]")
    
    if not found:
        console.print(f"\n[green][+] Nenhuma SQL Injection encontrada.[/green]")
