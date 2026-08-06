"""
goldeneye/reports/pdf_generator.py
Gerador de relatorios PDF a partir de templates HTML.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from rich.console import Console

console = Console()

TEMPLATES_DIR = Path.home() / "goldeneye" / "templates"


def generate_technical_pdf(
    project_data: Dict,
    output_path: Path,
) -> Optional[Path]:
    """Gera relatorio tecnico em PDF."""
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template("technical_report.html")
        
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
        
    except Exception as e:
        console.print(f"[red][!] Erro ao gerar PDF técnico: {e}[/red]")
        return None


def generate_executive_pdf(
    project_data: Dict,
    output_path: Path,
) -> Optional[Path]:
    """Gera relatorio executivo em PDF."""
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template("executive_report.html")
        
        vulns = project_data.get("vulnerabilities", [])
        critical_count = sum(1 for v in vulns if v.get("severity", "").lower() == "crítico")
        
        html = template.render(
            client=project_data.get("client", "N/A"),
            target=project_data.get("target", "N/A"),
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            assessment_type=project_data.get("assessment_type", "N/A"),
            risk_score=project_data.get("risk_score", "7.5"),
            executive_summary=project_data.get("executive_summary", "Relatório gerado pelo Goldeneye."),
            hosts_count=project_data.get("hosts_count", 0),
            vulns_count=len(vulns),
            critical_count=critical_count,
            top_risks=project_data.get("top_risks", []),
            recommendations=project_data.get("recommendations", []),
        )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html).write_pdf(str(output_path))
        
        console.print(f"[green][+] PDF executivo gerado: {output_path}[/green]")
        return output_path
        
    except Exception as e:
        console.print(f"[red][!] Erro ao gerar PDF executivo: {e}[/red]")
        return None


def generate_reports(project_data: Dict, output_dir: Path) -> tuple:
    """Gera ambos os relatorios."""
    tech_path = output_dir / f"relatorio_tecnico_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    exec_path = output_dir / f"relatorio_executivo_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    tech = generate_technical_pdf(project_data, tech_path)
    exec_ = generate_executive_pdf(project_data, exec_path)
    
    return tech, exec_
