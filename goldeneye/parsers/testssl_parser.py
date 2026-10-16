"""Parser para resultados JSON do testssl.sh."""
from typing import Dict, List, Any

from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()
GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
YELLOW = Style(color="#FFFF00")
GREY = Style(color="#666666")

_NON_FINDING_SEVERITIES = {"OK", "INFO"}


def parse_testssl_json(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """Converte o JSON estruturado do testssl.sh em achados exibíveis.

    Aceita o formato --json-pretty, no qual scanResult contém seções
    (protocols, ciphers, pfs etc.) com itens id/severity/finding.
    Resultados OK e INFO são informativos e não são retornados como problemas.
    """
    if not isinstance(payload, dict):
        raise ValueError("O resultado testssl deve ser um objeto JSON.")

    scan_results = payload.get("scanResult")
    if not isinstance(scan_results, list):
        raise ValueError("JSON testssl inválido: 'scanResult' deve ser uma lista.")

    header_target = (
        payload.get("targetHost")
        or payload.get("target host")
        or payload.get("target")
        or ""
    )
    header_port = str(payload.get("port") or "").strip()
    parsed: List[Dict[str, str]] = []

    def visit(value: Any, target: str) -> None:
        if isinstance(value, list):
            for item in value:
                visit(item, target)
            return
        if not isinstance(value, dict):
            return

        item_target = value.get("targetHost") or value.get("target host") or target
        item_port = str(value.get("port") or header_port).strip()
        if item_target and item_port:
            display_target = f"{item_target}:{item_port}"
        else:
            display_target = str(item_target or target)

        severity = str(value.get("severity") or "").strip().upper()
        finding = value.get("finding")
        finding_id = value.get("id")
        if finding_id is not None and finding is not None and severity:
            if severity not in _NON_FINDING_SEVERITIES:
                detail = str(finding).strip()
                parsed.append({
                    "target": display_target,
                    "vulnerability": str(finding_id),
                    "severity": severity,
                    "detail": detail,
                })
            return

        for key, nested in value.items():
            if isinstance(nested, (dict, list)):
                visit(nested, display_target if display_target else target)

    for section in scan_results:
        visit(section, str(header_target))

    return parsed


def display_testssl_results(results: List[Dict]):
    if not results:
        console.print("\\n[green][+] Nenhum problema TLS/SSL identificado.[/green]")
        return

    console.print(f"\\n[red]═══ PROBLEMAS TLS/SSL ═══[/red]")
    console.print(f"[cyan]Total: {len(results)} problemas[/cyan]\\n")

    table = Table(border_style=GREY, show_header=True)
    table.add_column("Alvo")
    table.add_column("Vulnerabilidade", style=RED)
    table.add_column("Severidade")
    table.add_column("Detalhe", max_width=50)

    for result in results:
        severity = result.get("severity", "MEDIUM")
        severity_style = f"[red]{severity}[/red]" if severity in {"HIGH", "CRITICAL"} else f"[yellow]{severity}[/yellow]"
        table.add_row(
            result.get("target", ""),
            result.get("vulnerability", ""),
            severity_style,
            result.get("detail", "")[:50],
        )

    console.print(table)
