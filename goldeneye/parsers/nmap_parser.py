"""
goldeneye/parsers/nmap_parser.py
Parser de XML do Nmap para dados normalizados.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.style import Style

console = Console()

GOLD = Style(color="#FFD700", bold=True)
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
YELLOW = Style(color="#FFFF00")
RED = Style(color="#DC143C")
GREY = Style(color="#666666")


def parse_nmap_xml(xml_path: Path) -> Dict:
    """
    Parseia o XML do Nmap e retorna dados estruturados.
    """
    result = {
        "hosts": [],
        "total_hosts": 0,
        "hosts_up": 0,
        "scan_info": {},
    }
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Info do scan
        scan_info = root.find("scaninfo")
        if scan_info is not None:
            result["scan_info"] = {
                "type": scan_info.get("type", ""),
                "protocol": scan_info.get("protocol", ""),
                "services": scan_info.get("services", ""),
            }
        
        # Hosts
        for host in root.findall("host"):
            host_data = {
                "ip": "",
                "mac": "",
                "vendor": "",
                "os": "",
                "status": "",
                "ports": [],
            }
            
            # Status
            status = host.find("status")
            if status is not None:
                host_data["status"] = status.get("state", "unknown")
            
            if host_data["status"] != "up":
                continue
            
            # IP
            addr = host.find("address")
            if addr is not None:
                host_data["ip"] = addr.get("addr", "")
            
            # MAC
            for addr in host.findall("address"):
                if addr.get("addrtype") == "mac":
                    host_data["mac"] = addr.get("addr", "")
                    host_data["vendor"] = addr.get("vendor", "")
            
            # OS
            os_elem = host.find("os")
            if os_elem is not None:
                os_match = os_elem.find("osmatch")
                if os_match is not None:
                    host_data["os"] = os_match.get("name", "")
            
            # Portas
            ports = host.find("ports")
            if ports is not None:
                for port in ports.findall("port"):
                    port_data = {
                        "port": port.get("portid", ""),
                        "protocol": port.get("protocol", ""),
                        "state": "",
                        "service": "",
                        "product": "",
                        "version": "",
                    }
                    
                    state = port.find("state")
                    if state is not None:
                        port_data["state"] = state.get("state", "")
                    
                    service = port.find("service")
                    if service is not None:
                        port_data["service"] = service.get("name", "")
                        port_data["product"] = service.get("product", "")
                        port_data["version"] = service.get("version", "")
                    
                    host_data["ports"].append(port_data)
            
            result["hosts"].append(host_data)
        
        result["total_hosts"] = len(root.findall("host"))
        result["hosts_up"] = len(result["hosts"])
        
    except ET.ParseError as e:
        console.print(f"[red][!] Erro ao parsear XML: {e}[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return result


def display_nmap_results(data: Dict):
    """Exibe os resultados do Nmap em tabela formatada."""
    
    if not data["hosts"]:
        console.print("[yellow][!] Nenhum host ativo encontrado.[/yellow]")
        return
    
    console.print(f"\n[gold1]─── RESULTADOS NMAP ───[/gold1]")
    console.print(f"[cyan]Hosts ativos: {data['hosts_up']}[/cyan]\n")
    
    for host in data["hosts"]:
        # Header do host
        console.print(f"[gold1]━━━ {host['ip']}[/gold1]", end="")
        if host["os"]:
            console.print(f" [grey]({host['os']})[/grey]", end="")
        if host["mac"]:
            console.print(f" [grey]MAC: {host['mac']}[/grey]", end="")
        console.print()
        
        if not host["ports"]:
            console.print("  [grey]Nenhuma porta aberta[/grey]")
            continue
        
        # Tabela de portas
        table = Table(border_style=GREY, show_header=True)
        table.add_column("Porta", style=CYAN)
        table.add_column("Protocolo")
        table.add_column("Estado", style=GREEN)
        table.add_column("Servico", style=GOLD)
        table.add_column("Versao")
        
        for port in host["ports"]:
            state_style = GREEN if port["state"] == "open" else RED if port["state"] == "filtered" else GREY
            
            version_str = ""
            if port["product"]:
                version_str = port["product"]
            if port["version"]:
                version_str += f" {port['version']}"
            
            table.add_row(
                f"{port['port']}/{port['protocol']}",
                port["protocol"],
                f"[{state_style}]{port['state']}[/{state_style}]",
                port["service"],
                version_str if version_str else "-",
            )
        
        console.print(table)
        console.print()
