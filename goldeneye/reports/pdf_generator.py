"""
goldeneye/reports/pdf_generator.py
Gerador de relatorios PDF a partir de templates HTML.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from rich.console import Console

console = Console()
TEMPLATES_DIR = Path.home() / "goldeneye" / "templates"


def _template_environment() -> Environment:
    """Cria ambiente Jinja com escape HTML habilitado para templates HTML."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml"),
            default_for_string=True,
        ),
    )


def generate_technical_pdf(project_data: Dict, output_path: Path) -> Optional[Path]:
    """Gera relatorio tecnico em PDF."""
    try:
        template = _template_environment().get_template("technical_report.html")
        html = template.render(
            client=project_data.get("client", "N/A"),
            project_name=project_data.get("project_name", "N/A"),
            target=project_data.get("target", "N/A"),
            assessment_type=project_data.get("assessment_type", "N/A"),
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            executive_summary=project_data.get("executive_summary", "Relatório gerado pelo Goldeneye."),
            hosts=project_data.get("hosts", []),
            vulnerabilities=project_data.get("vulnerabilities", []),
            recommendations=project_data.get("recommendations", []),
            conclusion=project_data.get("conclusion", "Avaliação concluída."),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html).write_pdf(str(output_path))
        console.print(f"[green][+] PDF técnico gerado: {output_path}[/green]")
        return output_path
    except Exception as exc:
        console.print(f"[red][!] Erro ao gerar PDF técnico: {exc}[/red]")
        return None


def generate_executive_pdf(project_data: Dict, output_path: Path) -> Optional[Path]:
    """Gera relatorio executivo em PDF."""
    try:
        template = _template_environment().get_template("executive_report.html")
        vulnerabilities = project_data.get("vulnerabilities", [])
        critical_count = sum(
            1 for vuln in vulnerabilities
            if str(vuln.get("severity", "")).lower() in {"crítico", "critico", "critical"}
        )
        html = template.render(
            client=project_data.get("client", "N/A"),
            target=project_data.get("target", "N/A"),
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            assessment_type=project_data.get("assessment_type", "N/A"),
            risk_score=project_data.get("risk_score", "N/A"),
            executive_summary=project_data.get("executive_summary", "Relatório gerado pelo Goldeneye."),
            hosts_count=project_data.get("hosts_count", 0),
            vulns_count=len(vulnerabilities),
            critical_count=critical_count,
            top_risks=project_data.get("top_risks", []),
            recommendations=project_data.get("recommendations", []),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html).write_pdf(str(output_path))
        console.print(f"[green][+] PDF executivo gerado: {output_path}[/green]")
        return output_path
    except Exception as exc:
        console.print(f"[red][!] Erro ao gerar PDF executivo: {exc}[/red]")
        return None


def generate_reports(project_data: Dict, output_dir: Path) -> tuple:
    """Gera ambos os relatorios."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    tech_path = output_dir / f"relatorio_tecnico_{timestamp}.pdf"
    exec_path = output_dir / f"relatorio_executivo_{timestamp}.pdf"
    return generate_technical_pdf(project_data, tech_path), generate_executive_pdf(project_data, exec_path)
