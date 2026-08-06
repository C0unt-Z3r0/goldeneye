"""
goldeneye/discovery/orchestrator.py
Orquestrador da fase de descoberta automatica.
"""

from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style

from goldeneye.discovery.dns_resolver import resolve_target
from goldeneye.discovery.whois_lookup import whois_lookup
from goldeneye.discovery.subdomains import discover_subdomains
from goldeneye.discovery.probe import probe_hosts
from goldeneye.discovery.fingerprint import fingerprint_urls

console = Console()

GOLD = Style(color="#FFD700", bold=True)
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
GREY = Style(color="#666666")


def run_discovery(target: str, project_name: str = None) -> Dict:
    """
    Executa pipeline completo de descoberta.
    Retorna dict com todos os dados coletados.
    """
    result = {
        "target": target,
        "dns": {},
        "whois": {},
        "subdomains": [],
        "hosts_alive": [],
        "fingerprints": [],
    }

    is_ip = target.replace(".", "").isdigit()

    # Step 1: DNS
    if not is_ip:
        console.print(f"\n[gold1][1/5] Resolvendo DNS...[/gold1]")
        result["dns"] = resolve_target(target)
        if result["dns"]["ips"]:
            console.print(f"  [green]{target} → {', '.join(result['dns']['ips'])}[/green]")
        if result["dns"]["mx"]:
            console.print(f"  [grey]MX: {', '.join(result['dns']['mx'][:5])}[/grey]")
        if result["dns"]["ns"]:
            console.print(f"  [grey]NS: {', '.join(result['dns']['ns'][:5])}[/grey]")

        # Step 2: WHOIS
        console.print(f"\n[gold1][2/5] Consultando WHOIS...[/gold1]")
        result["whois"] = whois_lookup(target)
        if result["whois"].get("org"):
            console.print(f"  [green]Org: {result['whois']['org']}[/green]")
        if result["whois"].get("country"):
            console.print(f"  [green]Pais: {result['whois']['country']}[/green]")

        # Step 3: Subdomains
        console.print(f"\n[gold1][3/5] Enumerando subdominios...[/gold1]")
        result["subdomains"] = discover_subdomains(target)
        console.print(f"  [green]{len(result['subdomains'])} subdominios encontrados[/green]")
        if len(result["subdomains"]) <= 10:
            for sub in result["subdomains"]:
                console.print(f"    [grey]{sub}[/grey]")

        # Step 4: Probe
        console.print(f"\n[gold1][4/5] Verificando hosts vivos...[/gold1]")
        result["hosts_alive"] = probe_hosts(result["subdomains"])
        console.print(f"  [green]{len(result['hosts_alive'])} hosts respondendo[/green]")

        # Step 5: Fingerprint
        if result["hosts_alive"]:
            console.print(f"\n[gold1][5/5] Identificando tecnologias...[/gold1]")
            urls = [h["url"] for h in result["hosts_alive"][:20]]
            result["fingerprints"] = fingerprint_urls(urls)
            console.print(f"  [green]{len(result['fingerprints'])} sites analisados[/green]")

            # Exibir tabela de tecnologias
            if result["fingerprints"]:
                console.print(f"\n[gold1]─── TECNOLOGIAS DETECTADAS ───[/gold1]")
                
                table = Table(border_style=GREY, show_header=True)
                table.add_column("URL", style=CYAN, max_width=40)
                table.add_column("IP", style=GREEN)
                table.add_column("Servidor")
                table.add_column("Tecnologias", style=GOLD)

                for fp in result["fingerprints"]:
                    plugins = fp.get("plugins", {})
                    tech_list = []
                    for name, info in plugins.items():
                        if isinstance(info, dict):
                            version = info.get("version", "")
                            if version:
                                tech_list.append(f"{name} {version}")
                            else:
                                tech_list.append(name)
                        else:
                            tech_list.append(name)

                    # Pegar IP do hosts_alive correspondente
                    ip = ""
                    for h in result["hosts_alive"]:
                        if h["url"] == fp.get("url") or h["url"] == fp.get("target"):
                            ip = h.get("ip", "")
                            break

                    # Pegar servidor web
                    server = ""
                    for h in result["hosts_alive"]:
                        if h["url"] == fp.get("url") or h["url"] == fp.get("target"):
                            server = h.get("webserver", "")
                            break

                    table.add_row(
                        fp.get("url", "")[:40],
                        ip,
                        server,
                        ", ".join(tech_list[:5]) if tech_list else "-",
                    )

                console.print(table)
    else:
        console.print(f"[cyan][*] Alvo e um IP ({target}). Pulando descoberta DNS/WHOIS/Subdominios.[/cyan]")
        result["dns"]["ips"] = [target]
        result["subdomains"] = [target]
        result["hosts_alive"] = probe_hosts([target])

    # Resumo
    console.print(f"\n[gold1]─── RESUMO DA DESCOBERTA ───[/gold1]")
    console.print(f"  [cyan]IPs unicos     :[/cyan] {len(result['dns'].get('ips', []))}")
    console.print(f"  [cyan]Subdominios    :[/cyan] {len(result['subdomains'])}")
    console.print(f"  [cyan]Hosts vivos    :[/cyan] {len(result['hosts_alive'])}")
    console.print(f"  [cyan]Tecnologias    :[/cyan] {len(result['fingerprints'])} sites analisados")

    return result
