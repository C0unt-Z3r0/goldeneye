
"""
goldeneye/cli/session.py
Gerenciamento de sessao do Goldeneye.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
import re

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.completion import WordCompleter

from goldeneye.core.project_manager import ProjectManager
from goldeneye.core.models import ProjectStatus

console = Console()

GOLD = Style(color="#FFD700", bold=True)
GOLD_DIM = Style(color="#B8960F")
GREY = Style(color="#666666")
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C")

PROMPT_STYLE = PTStyle.from_dict({
    "prompt": "#FFD700 bold",
    "": "#FFFFFF",
})

PROJECT_COMMANDS = WordCompleter(
    ["1", "2", "3", "4", "5", "6", "7", "8", "0", "back", "help"],
    ignore_case=True,
)


def sanitize_target(target: str) -> str:
    target = target.strip().lower()
    target = re.sub(r'^https?://', '', target)
    target = re.sub(r'^www\.', '', target)
    target = target.split('/')[0]
    target = target.split(':')[0]
    return target


class Session:
    def __init__(self):
        self.current_project_id: Optional[int] = None
        self.current_project_name: Optional[str] = None
        self.current_project_path: Optional[Path] = None
        self.current_target: Optional[str] = None
        self.started_at = datetime.now()

    def display_status(self):
        status_text = f"SESSAO: {self.current_project_name or 'Nenhum projeto ativo'}"
        date_text = f"DATA: {datetime.now().strftime('%d/%m/%Y')}"
        time_text = f"HORA: {datetime.now().strftime('%H:%M:%S')}"
        status_panel = Panel(
            f"{status_text}    |    {date_text}    |    {time_text}",
            border_style=GREY, padding=(0, 2),
        )
        console.print(status_panel)
        console.print()

    def new_project(self):
        from goldeneye.cli.menu import new_project_form
        data = new_project_form()
        if data.get("name"):
            pm = ProjectManager()
            project = pm.get_by_name(data["name"])
            if project:
                self.current_project_id = project.id
                self.current_project_name = project.name
                self.current_project_path = Path(project.project_path) if project.project_path else None
                self.current_target = sanitize_target(project.target)
                self._offer_discovery()

    def resume_project(self):
        from goldeneye.cli.menu import resume_project_list
        project_id = resume_project_list()
        if project_id > 0:
            pm = ProjectManager()
            project = pm.get_by_id(project_id)
            if project:
                self.current_project_id = project.id
                self.current_project_name = project.name
                self.current_project_path = Path(project.project_path) if project.project_path else None
                self.current_target = sanitize_target(project.target)
                pm.update_status(project_id, ProjectStatus.IN_PROGRESS)
                console.print(f"\n[green][+] Projeto '{project.name}' carregado![/green]")
                console.print(f"[cyan][*] Cliente: {project.client}[/cyan]")
                console.print(f"[cyan][*] Alvo   : {self.current_target}[/cyan]\n")
                prompt("Pressione ENTER para continuar...", style=PROMPT_STYLE)
                self._project_menu()

    def _offer_discovery(self):
        from goldeneye.cli.menu import clear_and_show_header
        clear_and_show_header(f"PROJETO: {self.current_project_name}")
        console.print(f"[cyan]Alvo: {self.current_target}[/cyan]\n")
        console.print("[gold1]Deseja iniciar a descoberta automatica?[/gold1]")
        console.print("  [1] Sim  [2] Nao\n")
        choice = prompt("  Escolha [1-2]: ", style=PROMPT_STYLE).strip()
        if choice == "1":
            self.run_discovery()
            prompt("\nPressione ENTER para continuar...", style=PROMPT_STYLE)
        self._project_menu()

    def _project_menu(self):
        from goldeneye.cli.menu import clear_and_show_header
        while True:
            clear_and_show_header(f"PROJETO: {self.current_project_name}")
            console.print(f"[cyan]Alvo: {self.current_target}[/cyan]")
            console.print(f"[cyan]Pasta: {self.current_project_path}[/cyan]\n")
            menu = Table(show_header=False, box=None, padding=(0, 4))
            menu.add_column(style=GOLD)
            menu.add_column(style=Style(color="#FFFFFF"))
            menu.add_row("[1]", "Descoberta / Recon")
            menu.add_row("[2]", "Scan de Portas (Nmap)")
            menu.add_row("[3]", "Scan Vulns (Nuclei)")
            menu.add_row("[4]", "Scan Web (OWASP ZAP)")
            menu.add_row("[5]", "Nikto Scanner")
            menu.add_row("[6]", "Fuzzing (Gobuster)")
            menu.add_row("[7]", "Scan WordPress (WPScan)")
            menu.add_row("[8]", "SQL Injection (SQLMap)")
            menu.add_row("[9]", "Bruteforce (Hydra)")
            menu.add_row("[10]", "Enum Windows (CME)")
            menu.add_row("[11]", "Exploits (Searchsploit)")
            menu.add_row("[12]", "TestSSL/TLS")
            menu.add_row("[13]", "Analise com IA")
            menu.add_row("[14]", "Dashboard de Risco")
            menu.add_row("[15]", "Gerar Relatorios")
            menu.add_row("[16]", "Abrir Relatorios (PDF)")
            menu.add_row("[17]", "⚡ Quick Scan")
            menu.add_row("[18]", "🚀 MODO FULL AUTO")
            menu.add_row("[19]", "Verificar Falsos Positivos")
            menu.add_row("[20]", "LinPEAS (Privilegios)")
            menu.add_row("[21]", "Hashcat (Quebra Hashes)")
            menu.add_row("[22]", "🕵️  Modo Anonimo (ON/OFF)")
            menu.add_row("[23]", "FFUF Fuzzing Rapido")
            menu.add_row("[0]", "Voltar ao Menu Principal")
            menu_panel = Panel(menu, border_style=GOLD_DIM, padding=(1, 2),
                               title="FERRAMENTAS", title_align="center")
            console.print(menu_panel)
            console.print()
            choice = prompt(
                f"goldeneye [{self.current_project_name}]> ",
                style=PROMPT_STYLE, completer=PROJECT_COMMANDS,
            ).strip().lower()
            if choice in ["0", "back"]:
                break
            elif choice == "1":
                self.run_discovery()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "2":
                self._run_nmap_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "3":
                self._run_nuclei_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "4":
                self._run_zap_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "5":
                self._run_nikto_scan()
            elif choice == "6":
                self._run_gobuster_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "7":
                self._run_wpscan_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "8":
                self._run_sqlmap_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "9":
                self._run_hydra_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "10":
                self._run_cme_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "11":
                self._run_msf_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "12":
                self._run_testssl_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "13":
                self._run_ai_analysis()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "14":
                self._show_dashboard()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "15":
                self.generate_report()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "16":
                self._open_reports()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "17":
                self._run_quick_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "18":
                self._run_full_auto()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "19":
                self._check_false_positives()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "20":
                self._run_linpeas()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "21":
                self._run_hashcat()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)
            elif choice == "22":
                self.toggle_anonymous()
            elif choice == "23":
                self._run_ffuf_scan()
                prompt("\nPressione ENTER...", style=PROMPT_STYLE)

            
            else:
                console.print("\n[red][!] Opcao invalida.[/red]")
                prompt("Pressione ENTER...", style=PROMPT_STYLE)

    def _run_nmap_scan(self):
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.nmap_runner import run_nmap
        from goldeneye.parsers.nmap_parser import parse_nmap_xml, display_nmap_results
        clear_and_show_header(f"NMAP - {self.current_project_name}")
        console.print(f"[cyan]Alvo: {self.current_target}[/cyan]\n")
        console.print("[gold1]Tipo:[/gold1] [1] Rapido [2] Completo [3] Stealth [4] Personalizado\n")
        choice = prompt("  Escolha [1-4]: ", style=PROMPT_STYLE).strip()
        scan_type, ports = "quick", None
        if choice == "2": scan_type = "full"
        elif choice == "3": scan_type = "stealth"
        elif choice == "4": ports = prompt("  Portas: ", style=PROMPT_STYLE).strip()
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        xml_path = run_nmap(target=self.current_target, output_dir=scan_dir, scan_type=scan_type, ports=ports)
        if xml_path and xml_path.exists():
            data = parse_nmap_xml(xml_path)
            display_nmap_results(data)

    def _run_nuclei_scan(self):
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.nuclei_runner import run_nuclei
        from goldeneye.parsers.nuclei_parser import parse_nuclei_json, display_nuclei_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"NUCLEI - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                port = p["port"]
                svc = p.get("service", "")
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
                elif svc in ["mysql", "ftp", "ssh", "svnserve", "svn"]:
                    targets.append(f"{svc}://{ip}:{port}")
        for host in nmap_data.get("hosts", []):
            if host.get("ip"):
                targets.append(host["ip"])
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {len(targets)} URLs[/cyan]\n")
        json_path = run_nuclei(targets=targets, output_dir=scan_dir)
        if json_path and json_path.exists():
            results = parse_nuclei_json(json_path)
            display_nuclei_results(results)

    def _run_ai_analysis(self):
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        from goldeneye.analyzers.ai_analyzer import analyze_nmap_results, display_analysis
        clear_and_show_header(f"IA - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan encontrado.[/red]")
            return
        data = parse_nmap_xml(xml_files[0])
        data["target"] = self.current_target
        console.print("[cyan][*] Enviando para IA...[/cyan]\n")
        analysis = analyze_nmap_results(data)
        display_analysis(analysis, self.current_target)

    def _run_zap_scan(self):
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.zap_runner import run_zap_scan
        from goldeneye.parsers.zap_parser import display_zap_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"ZAP SCAN - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {targets}[/cyan]\n")
        console.print("[yellow][!] ZAP pode levar varios minutos...[/yellow]\n")
        confirm = prompt("Continuar? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        results = run_zap_scan(targets, scan_dir)
        display_zap_results(results)

    def _run_sqlmap_scan(self):
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.sqlmap_runner import run_sqlmap_batch
        from goldeneye.parsers.sqlmap_parser import display_sqlmap_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"SQLMAP - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        
        # Opção de adicionar URLs manuais
        console.print(f"\n[cyan]Alvos encontrados: {len(targets)}[/cyan]")
        for i, t in enumerate(targets, 1):
            console.print(f"  [{i}] {t}")
        
        console.print(f"\n  [A] Usar todos os alvos encontrados")
        console.print(f"  [M] Digitar URL manualmente")
        console.print(f"  [0] Voltar\n")
        
        choice = prompt("  Escolha: ", style=PROMPT_STYLE).strip()
        
        if choice == "0":
            return
        elif choice.upper() == "M":
            manual_url = prompt("  URL (ex: http://alvo.com/pagina.php?id=1): ", style=PROMPT_STYLE).strip()
            if manual_url:
                targets = [manual_url]
        elif choice.upper() != "A":
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(targets):
                    targets = [targets[idx]]
            except ValueError:
                pass
        
        console.print(f"\n[cyan]Alvos: {len(targets)} URLs[/cyan]")
        console.print(f"\n[gold1]Modo de Exploracao:[/gold1]")
        console.print(f"  [1] Basico (apenas detectar)")
        console.print(f"  [2] Enumerar Bancos (--dbs)")
        console.print(f"  [3] Enumerar Tabelas (--tables)")
        console.print(f"  [4] Extrair Dados (--dump)")
        console.print(f"  [5] Personalizado (digitar flags)\n")
        exp_choice = prompt("  Escolha [1-5] (ENTER=1): ", style=PROMPT_STYLE).strip()
        extra_flags = ""
        if exp_choice == "2":
            extra_flags = " --dbs"
        elif exp_choice == "3":
            db = prompt("  Nome do banco: ", style=PROMPT_STYLE).strip()
            extra_flags = f" -D {db} --tables" if db else " --tables"
        elif exp_choice == "4":
            db = prompt("  Nome do banco: ", style=PROMPT_STYLE).strip()
            table = prompt("  Nome da tabela: ", style=PROMPT_STYLE).strip()
            if db and table:
                extra_flags = f" -D {db} -T {table} --dump"
            else:
                extra_flags = " --dump"
        elif exp_choice == "5":
            extra_flags = " " + prompt("  Flags SQLMap: ", style=PROMPT_STYLE).strip()
        if extra_flags:
            for i, t in enumerate(targets):
                targets[i] = t + extra_flags
        console.print(f"\n[yellow][!] SQLMap pode levar varios minutos...[/yellow]\n")
        confirm = prompt("Continuar? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        results = run_sqlmap_batch(targets, scan_dir)
        display_sqlmap_results(results, targets)

    def _run_cme_scan(self):
        """Executa CrackMapExec nos hosts."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.cme_runner import run_cme_scan
        from goldeneye.parsers.cme_parser import display_cme_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"CME - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            if ip:
                targets.append(ip)
        if not targets:
            targets.append(self.current_target)
        console.print(f"[cyan]Alvos: {len(targets)} hosts[/cyan]\n")
        results = run_cme_scan(targets, scan_dir)
        display_cme_results(results)

    def _run_hydra_scan(self):
        """Executa Hydra nos servicos."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.hydra_runner import run_hydra_scan
        from goldeneye.parsers.hydra_parser import display_hydra_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"HYDRA - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] == "open":
                    targets.append((ip, p["port"], p.get("service", "unknown")))
        if not targets:
            console.print("[yellow][!] Nenhuma porta aberta.[/yellow]")
            return
        console.print(f"[cyan]Alvos: {len(targets)} servicos[/cyan]")
        console.print("[yellow][!] Use apenas em alvos autorizados![/yellow]\n")
        confirm = prompt("Continuar? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        results = run_hydra_scan(targets, scan_dir)
        display_hydra_results(results)

    def _run_msf_scan(self):
        """Busca exploits no Metasploit."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.msf_runner import run_msf_scan
        from goldeneye.parsers.msf_parser import display_msf_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"METASPLOIT - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        services = []
        for host in nmap_data.get("hosts", []):
            for p in host.get("ports", []):
                if p["state"] == "open":
                    services.append({
                        "service": p.get("service", ""),
                        "product": p.get("product", ""),
                        "version": p.get("version", ""),
                        "port": p["port"],
                    })
        if not services:
            console.print("[yellow][!] Nenhum servico encontrado.[/yellow]")
            return
        console.print(f"[cyan]Buscando exploits para {len(services)} servicos...[/cyan]\n")
        results = run_msf_scan(services, scan_dir)
        display_msf_results(results)

    def _run_gobuster_scan(self):
        """Executa Gobuster nas URLs."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.gobuster_runner import run_gobuster_scan
        from goldeneye.parsers.gobuster_parser import display_gobuster_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"GOBUSTER - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {len(targets)} URLs[/cyan]\n")
        results = run_gobuster_scan(targets, scan_dir)
        display_gobuster_results(results)

    def _run_full_auto(self):
        """Modo FULL AUTO TURBO - TODAS as 18 ferramentas."""
        from goldeneye.cli.menu import clear_and_show_header
        
        clear_and_show_header(f"🚀 FULL AUTO TURBO - {self.current_project_name}")
        
        console.print("[gold1]╔══════════════════════════════════════════╗[/gold1]")
        console.print("[gold1]║   MODO FULL AUTO TURBO ATIVADO         ║[/gold1]")
        console.print("[gold1]║   TODAS as 18 ferramentas em sequencia  ║[/gold1]")
        console.print("[gold1]╚══════════════════════════════════════════╝[/gold1]")
        console.print(f"\n[cyan]Alvo: {self.current_target}[/cyan]")
        console.print("[yellow][!] Isso pode levar 30-60 minutos...[/yellow]\n")
        
        confirm = prompt("Continuar? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        
        steps = [
            # FASE 1: RECON
            ("[1/12] Descoberta Automatica", self.run_discovery),
            ("[2/12] Nmap Scan", self._run_nmap_scan),
            
            # FASE 2: VULNERABILIDADES
            ("[3/12] Nuclei Scan", self._run_nuclei_scan),
            ("[4/12] OWASP ZAP Scan", self._run_zap_scan),
            ("[5/12] Nikto Scanner", self._run_nikto_scan),
            ("[6/12] Gobuster Fuzzing", self._run_gobuster_scan),
            ("[7/12] WPScan", self._run_wpscan_scan),
            
            # FASE 3: EXPLORAÇÃO
            ("[8/12] SQLMap", self._run_sqlmap_scan),
            ("[9/12] Hydra Bruteforce", self._run_hydra_scan),
            ("[10/12] CrackMapExec", self._run_cme_scan),
            ("[11/12] Searchsploit", self._run_msf_scan),
            ("[12/12] TestSSL/TLS", self._run_testssl_scan),
            
            # FASE 4: ANÁLISE & RELATÓRIOS
            ("[+] Analise com IA (Mistral)", self._run_ai_analysis),
            ("[+] Dashboard de Risco", self._show_dashboard),
            ("[+] Gerando Relatorios (PDF+DOCX+Graficos)", self.generate_report),
        ]
        
        for name, func in steps:
            console.print(f"\n[gold1]{name}[/gold1]")
            console.print("[grey]───[/grey]")
            try:
                func()
            except Exception as e:
                console.print(f"[red][!] Erro em {name}: {e}[/red]")
        
        console.print(f"\n[gold1]╔══════════════════════════════════════════╗[/gold1]")
        console.print(f"[gold1]║   FULL AUTO TURBO CONCLUIDO! 🎉        ║[/gold1]")
        console.print(f"[gold1]║   18 ferramentas executadas            ║[/gold1]")
        console.print(f"[gold1]╚══════════════════════════════════════════╝[/gold1]")
        
        self._open_reports()

    def _show_dashboard(self):
        """Exibe dashboard de risco."""
        from goldeneye.cli.dashboard import show_dashboard
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        nmap_data = None
        if scan_dir and scan_dir.exists():
            xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
            if xml_files:
                nmap_data = parse_nmap_xml(xml_files[0])
        show_dashboard(self.current_project_name, self.current_target, nmap_data)

    def _run_wpscan_scan(self):
        """Executa WPScan nas URLs."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.wpscan_runner import run_wpscan_scan
        from goldeneye.parsers.wpscan_parser import display_wpscan_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"WPSCAN - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {len(targets)} URLs[/cyan]\n")
        results = run_wpscan_scan(targets, scan_dir)
        display_wpscan_results(results)

    def _run_quick_scan(self):
        """Quick Scan - Nmap rapido + Nuclei em 1 minuto."""
        from goldeneye.cli.menu import clear_and_show_header
        clear_and_show_header(f"⚡ QUICK SCAN - {self.current_project_name}")
        console.print("[cyan]Modo rapido: Nmap (top 100) + Nuclei[/cyan]\n")
        console.print("[yellow][!] Aprox. 1-2 minutos...[/yellow]\n")
        confirm = prompt("Continuar? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        self._run_nmap_scan_quick()
        self._run_nuclei_scan()
    
    def _run_nmap_scan_quick(self):
        """Nmap rapido - top 100 portas."""
        from goldeneye.runners.nmap_runner import run_nmap
        from goldeneye.parsers.nmap_parser import parse_nmap_xml, display_nmap_results
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        xml_path = run_nmap(target=self.current_target, output_dir=scan_dir, scan_type="quick", ports="top100")
        if xml_path and xml_path.exists():
            data = parse_nmap_xml(xml_path)
            display_nmap_results(data)

    def _run_nikto_scan(self):
        """Executa Nikto nas URLs."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.nikto_runner import run_nikto_scan
        from goldeneye.parsers.nikto_parser import display_nikto_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"NIKTO - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {len(targets)} URLs[/cyan]\n")
        results = run_nikto_scan(targets, scan_dir)
        display_nikto_results(results)

    def _run_testssl_scan(self):
        """Executa TestSSL nos servicos TLS."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.testssl_runner import run_testssl_scan
        from goldeneye.parsers.testssl_parser import display_testssl_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"TESTSSL - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                if "ssl" in p.get("service", "") or p["port"] in ["443", "8443", "465", "993", "995"]:
                    targets.append((ip, int(p["port"])))
        if not targets:
            targets.append((self.current_target, 443))
        console.print(f"[cyan]Alvos TLS: {len(targets)}[/cyan]\n")
        results = run_testssl_scan(targets, scan_dir)
        display_testssl_results(results)

    def _run_hashcat(self):
        """Executa Hashcat em arquivo de hashes."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.hashcat_runner import run_hashcat, HASH_MODES
        from goldeneye.parsers.hashcat_parser import display_hashcat_results
        clear_and_show_header(f"HASHCAT - {self.current_project_name}")
        hash_path = prompt("  Arquivo de hashes: ", style=PROMPT_STYLE).strip()
        hash_file = Path(hash_path).expanduser()
        if not hash_file.exists():
            console.print("[red][!] Arquivo nao encontrado.[/red]")
            return
        console.print(f"\n[cyan]Modos de hash:[/cyan]")
        for i, (name, mode) in enumerate(HASH_MODES.items()):
            console.print(f"  [{i+1}] {name}")
        h_choice = prompt(f"  Escolha [1-{len(HASH_MODES)}]: ", style=PROMPT_STYLE).strip()
        hash_type = list(HASH_MODES.keys())[int(h_choice)-1] if h_choice.isdigit() else "MD5"
        console.print(f"\n[cyan]Ataque:[/cyan]")
        console.print(f"  [1] Wordlist")
        console.print(f"  [2] Bruteforce (6 chars)\n")
        a_choice = prompt("  Escolha [1-2]: ", style=PROMPT_STYLE).strip()
        wordlist = None
        attack_mode = 0
        if a_choice == "2":
            attack_mode = 3
        else:
            wl = prompt("  Wordlist (ENTER=rockyou): ", style=PROMPT_STYLE).strip()
            wordlist = wl or "/usr/share/wordlists/rockyou.txt.gz"
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        results = run_hashcat(hash_file, scan_dir, hash_type, wordlist, attack_mode)
        display_hashcat_results(results)

    def _run_linpeas(self):
        """Executa LinPEAS para enumeracao de privilegios."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.linpeas_runner import run_linpeas
        from goldeneye.parsers.linpeas_parser import display_linpeas_results
        clear_and_show_header(f"LINPEAS - {self.current_project_name}")
        console.print("[yellow][!] LinPEAS deve ser executado NO SERVIDOR ALVO, nao localmente.[/yellow]")
        console.print("[cyan]Esta opcao demonstra a integracao. Copie o LinPEAS para o alvo e execute.[/cyan]\n")
        confirm = prompt("Executar LinPEAS LOCALMENTE (demonstracao)? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        results = run_linpeas(scan_dir, self.current_target)
        display_linpeas_results(results)

    def _delete_project(self):
        """Apaga o projeto atual."""
        from goldeneye.core.project_manager import ProjectManager
        import shutil
        
        console.print(f"\n[red]🗑️  APAGAR PROJETO: {self.current_project_name}[/red]")
        console.print(f"[yellow][!] Esta acao e IRREVERSIVEL![/yellow]")
        console.print(f"[yellow]    Pasta: {self.current_project_path}[/yellow]\n")
        
        confirm = prompt("Digite o nome do projeto para confirmar: ", style=PROMPT_STYLE).strip()
        
        if confirm == self.current_project_name:
            pm = ProjectManager()
            pm.delete(self.current_project_id)
            
            # Apagar pasta
            if self.current_project_path and self.current_project_path.exists():
                shutil.rmtree(self.current_project_path)
            
            console.print(f"\n[red][+] Projeto '{self.current_project_name}' APAGADO![/red]\n")
            self.current_project_id = None
            self.current_project_name = None
            self.current_project_path = None
            prompt("Pressione ENTER para voltar ao menu principal...", style=PROMPT_STYLE)
            self._project_menu()
            return  # Sai do menu de projeto
        else:
            console.print(f"\n[yellow][!] Nome incorreto. Projeto NAO foi apagado.[/yellow]\n")
            prompt("Pressione ENTER...", style=PROMPT_STYLE)

    def _run_ffuf_scan(self):
        """Executa FFUF nas URLs."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.ffuf_runner import run_ffuf_scan
        from goldeneye.parsers.ffuf_parser import display_ffuf_results
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        clear_and_show_header(f"FFUF - {self.current_project_name}")
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if not scan_dir or not scan_dir.exists():
            console.print("[red][!] Execute o Nmap primeiro.[/red]")
            return
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not xml_files:
            console.print("[red][!] Nenhum scan Nmap encontrado.[/red]")
            return
        nmap_data = parse_nmap_xml(xml_files[0])
        targets = []
        for host in nmap_data.get("hosts", []):
            ip = host.get("ip", "")
            for p in host.get("ports", []):
                if p["state"] != "open": continue
                svc = p.get("service", "")
                port = p["port"]
                if svc in ["http", "https"] or port in ["80", "443", "8080", "8443"]:
                    scheme = "https" if "ssl" in svc or port == "443" else "http"
                    targets.append(f"{scheme}://{ip}:{port}")
        if not targets:
            targets.append(f"http://{self.current_target}")
        console.print(f"[cyan]Alvos: {len(targets)} URLs[/cyan]\n")
        results = run_ffuf_scan(targets, scan_dir)
        display_ffuf_results(results)

    def _check_false_positives(self):
        """Verifica falsos positivos cruzando resultados."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.analyzers.false_positive_checker import check_false_positives, display_false_positive_report
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        
        clear_and_show_header(f"VERIFICACAO DE FALSOS POSITIVOS - {self.current_project_name}")
        
        console.print("[cyan]Coletando resultados de todas as ferramentas...[/cyan]\n")
        
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        
        all_results = {
            "testssl": [],
            "hydra": [],
            "zap": [],
            "nikto": [],
            "nmap": [],
        }
        
        if scan_dir and scan_dir.exists():
            # Nmap
            xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
            if xml_files:
                all_results["nmap"] = [{"output": "nmap scan"}]
            
            # ZAP
            zap_file = scan_dir / "zap_results.json"
            if zap_file.exists():
                import json
                with open(zap_file) as f:
                    all_results["zap"] = json.load(f)
        
        results = check_false_positives(all_results)
        display_false_positive_report(results)

    def _run_hashcat(self):
        """Executa Hashcat em arquivo de hashes."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.hashcat_runner import run_hashcat, HASH_MODES
        from goldeneye.parsers.hashcat_parser import display_hashcat_results
        clear_and_show_header(f"HASHCAT - {self.current_project_name}")
        hash_path = prompt("  Arquivo de hashes: ", style=PROMPT_STYLE).strip()
        hash_file = Path(hash_path).expanduser()
        if not hash_file.exists():
            console.print("[red][!] Arquivo nao encontrado.[/red]")
            return
        console.print(f"\n[cyan]Modos de hash:[/cyan]")
        for i, (name, mode) in enumerate(HASH_MODES.items()):
            console.print(f"  [{i+1}] {name}")
        h_choice = prompt(f"  Escolha [1-{len(HASH_MODES)}]: ", style=PROMPT_STYLE).strip()
        hash_type = list(HASH_MODES.keys())[int(h_choice)-1] if h_choice.isdigit() else "MD5"
        console.print(f"\n[cyan]Ataque:[/cyan]")
        console.print(f"  [1] Wordlist")
        console.print(f"  [2] Bruteforce (6 chars)\n")
        a_choice = prompt("  Escolha [1-2]: ", style=PROMPT_STYLE).strip()
        wordlist = None
        attack_mode = 0
        if a_choice == "2":
            attack_mode = 3
        else:
            wl = prompt("  Wordlist (ENTER=rockyou): ", style=PROMPT_STYLE).strip()
            wordlist = wl or "/usr/share/wordlists/rockyou.txt.gz"
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        results = run_hashcat(hash_file, scan_dir, hash_type, wordlist, attack_mode)
        display_hashcat_results(results)

    def _run_linpeas(self):
        """Executa LinPEAS para enumeracao de privilegios."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.linpeas_runner import run_linpeas
        from goldeneye.parsers.linpeas_parser import display_linpeas_results
        clear_and_show_header(f"LINPEAS - {self.current_project_name}")
        console.print("[yellow][!] LinPEAS deve ser executado NO SERVIDOR ALVO, nao localmente.[/yellow]")
        console.print("[cyan]Esta opcao demonstra a integracao. Copie o LinPEAS para o alvo e execute.[/cyan]\n")
        confirm = prompt("Executar LinPEAS LOCALMENTE (demonstracao)? [S/n]: ", style=PROMPT_STYLE).strip().lower()
        if confirm not in ["", "s", "y", "sim"]:
            return
        scan_dir = self.current_project_path / "scans" if self.current_project_path else Path(".")
        results = run_linpeas(scan_dir, self.current_target)
        display_linpeas_results(results)

    def _delete_project(self):
        """Apaga o projeto atual."""
        from goldeneye.core.project_manager import ProjectManager
        import shutil
        
        console.print(f"\n[red]🗑️  APAGAR PROJETO: {self.current_project_name}[/red]")
        console.print(f"[yellow][!] Esta acao e IRREVERSIVEL![/yellow]")
        console.print(f"[yellow]    Pasta: {self.current_project_path}[/yellow]\n")
        
        confirm = prompt("Digite o nome do projeto para confirmar: ", style=PROMPT_STYLE).strip()
        
        if confirm == self.current_project_name:
            pm = ProjectManager()
            pm.delete(self.current_project_id)
            
            # Apagar pasta
            if self.current_project_path and self.current_project_path.exists():
                shutil.rmtree(self.current_project_path)
            
            console.print(f"\n[red][+] Projeto '{self.current_project_name}' APAGADO![/red]\n")
            self.current_project_id = None
            self.current_project_name = None
            self.current_project_path = None
            prompt("Pressione ENTER para voltar ao menu principal...", style=PROMPT_STYLE)
            self._project_menu()
            return  # Sai do menu de projeto
        else:
            console.print(f"\n[yellow][!] Nome incorreto. Projeto NAO foi apagado.[/yellow]\n")
            prompt("Pressione ENTER...", style=PROMPT_STYLE)

    def _check_false_positives(self):
        """Verifica falsos positivos."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.analyzers.false_positive_checker import check_false_positives, display_false_positive_report
        clear_and_show_header(f"FALSOS POSITIVOS - {self.current_project_name}")
        console.print("[cyan]Analisando resultados...[/cyan]\n")
        all_results = {"testssl": [], "hydra": [], "zap": [], "nikto": [], "nmap": []}
        scan_dir = self.current_project_path / "scans" if self.current_project_path else None
        if scan_dir and scan_dir.exists():
            xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True)
            if xml_files:
                all_results["nmap"] = [{"output": "nmap scan"}]
            zap_file = scan_dir / "zap_results.json"
            if zap_file.exists():
                import json
                with open(zap_file) as f:
                    all_results["zap"] = json.load(f)
        results = check_false_positives(all_results)
        display_false_positive_report(results)

    def _open_reports(self):
        import subprocess, os
        reports_dir = self.current_project_path / "reports" if self.current_project_path else None
        if not reports_dir or not reports_dir.exists():
            console.print("[yellow][!] Nenhum relatorio gerado ainda.[/yellow]")
            return
        pdfs = sorted(reports_dir.glob("*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)
        htmls = sorted(reports_dir.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not pdfs:
            console.print("[yellow][!] Nenhum PDF encontrado.[/yellow]")
            return
        all_files = list(pdfs) + list(htmls)
        console.print(f"\n[cyan]Relatorios disponiveis ({len(all_files)}):[/cyan]")
        for i, f in enumerate(all_files[:8], 1):
            size_kb = f.stat().st_size / 1024
            icon = "🌐" if f.suffix == ".html" else "📄"
            console.print(f"  [{i}] {icon} {f.name} ({size_kb:.0f} KB)")
        console.print(f"\n  [A] Abrir todos")
        console.print(f"  [0] Voltar\n")
        choice = prompt("  Escolha: ", style=PROMPT_STYLE).strip()
        if choice == "0":
            return
        public_dir = "/mnt/c/Users/Public/"
        to_open = []
        if choice.upper() == "A":
            to_open = all_files[:8]
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_files[:8]):
                    to_open = [all_files[idx]]
            except ValueError:
                return
        for f in to_open:
            dest = public_dir + f.name
            os.system(f"cp '{f}' '{dest}' 2>/dev/null")
            win_path = "C:\\Users\\Public\\" + f.name
            if f.suffix == ".html":
                # Abrir no navegador padrao
                subprocess.Popen(
                    f'cmd.exe /c start "" "{win_path}"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    f'powershell.exe -Command "Invoke-Item \'{win_path}\'"',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
        console.print(f"[green][+] Abrindo {len(to_open)} relatorio(s)...[/green]")

    def run_discovery(self):
        from goldeneye.cli.menu import discovery_screen
        discovery_screen(self.current_project_name, self.current_target)

    def generate_report(self):
        from goldeneye.cli.menu import generate_report_screen, clear_and_show_header
        from goldeneye.parsers.nmap_parser import parse_nmap_xml
        from pathlib import Path
        if not self.current_project_path:
            console.print("[red][!] Nenhum projeto ativo.[/red]")
            return
        scan_dir = self.current_project_path / "scans"
        xml_files = sorted(scan_dir.glob("nmap_*.xml"), key=lambda f: f.stat().st_mtime, reverse=True) if scan_dir.exists() else []
        hosts = []
        if xml_files:
            nmap_data = parse_nmap_xml(xml_files[0])
            for h in nmap_data.get("hosts", []):
                open_ports = [f"{p['port']}/{p['protocol']}" for p in h.get("ports", []) if p["state"] == "open"]
                hosts.append({
                    "ip": h.get("ip", ""),
                    "hostname": h.get("ip", ""),
                    "os": h.get("os", "Desconhecido"),
                    "open_ports": ", ".join(open_ports) if open_ports else "Nenhuma",
                })
        project_data = {
            "client": "Cliente",
            "project_name": self.current_project_name,
            "target": self.current_target,
            "assessment_type": "Pentest",
            "executive_summary": f"Avaliacao de seguranca realizada no alvo {self.current_target}.",
            "hosts": hosts,
            "hosts_count": len(hosts),
            "vulnerabilities": [],
            "top_risks": [],
            "recommendations": [],
            "risk_score": "7.5",
            "conclusion": "Avaliacao concluida.",
        }
        output_dir = self.current_project_path / "reports"
        generate_report_screen(project_data, output_dir)
        
        # Gerar HTML interativo
        from datetime import datetime
        from jinja2 import Environment, FileSystemLoader
        html_path = output_dir / f"relatorio_interativo_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
        try:
            env = Environment(loader=FileSystemLoader(str(Path.home() / "goldeneye" / "templates")))
            template = env.get_template("interactive_report.html")
            html = template.render(date=datetime.now().strftime("%d/%m/%Y %H:%M"))
            with open(html_path, "w") as f:
                f.write(html)
            console.print(f"[green][+] HTML interativo: {html_path}[/green]")
        except Exception as e:
            console.print(f"[yellow][!] HTML: {e}[/yellow]")
        
        # Tambem gerar DOCX
        from goldeneye.reports.docx_generator import generate_docx
        from goldeneye.reports.charts import generate_risk_chart, generate_score_gauge
        docx_path = output_dir / f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        generate_docx(project_data, docx_path)
        
        # Graficos
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        generate_risk_chart(charts_dir / "risk_pie.png")
        generate_score_gauge(charts_dir / "score_gauge.png", float(project_data.get("risk_score", 7.5)))

    def settings(self):
        from goldeneye.cli.menu import settings_screen
        settings_screen()

    def about(self):
        from goldeneye.cli.menu import about_screen
        about_screen()

    def invalid_option(self):
        console.print("\n[red][!] Opcao invalida.[/red]\n")

    def toggle_anonymous(self):
        """Ativa/desativa modo anonimo."""
        import os
        if os.environ.get("GOLDENEYE_ANON"):
            del os.environ["GOLDENEYE_ANON"]
            console.print("\n[green][+] Modo anonimo DESATIVADO[/green]\n")
        else:
            os.environ["GOLDENEYE_ANON"] = "1"
            console.print("\n[yellow][🕵️] Modo anonimo ATIVADO[/yellow]")
            console.print("[grey]  - User-Agent aleatorio em todas as ferramentas[/grey]")
            console.print("[grey]  - Sem fingerprint de OS[/grey]")
            console.print("[grey]  - Headers minimizados[/grey]\n")
        prompt("Pressione ENTER...", style=PROMPT_STYLE)

    def delete_projects(self):
        """Apagar projetos - menu principal."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.core.project_manager import ProjectManager
        import shutil
        
        clear_and_show_header("🗑️  APAGAR PROJETOS")
        
        pm = ProjectManager()
        projects = pm.list_all()
        
        if not projects:
            console.print("[grey][*] Nenhum projeto salvo.[/grey]\n")
            prompt("Pressione ENTER para voltar...", style=PROMPT_STYLE)
            return
        
        console.print(f"\n[cyan]Projetos salvos ({len(projects)}):[/cyan]\n")
        for i, p in enumerate(projects, 1):
            console.print(f"  [{i}] {p.name} | {p.client} | {p.target}")
        
        console.print(f"\n  [A] APAGAR TODOS")
        console.print(f"  [0] Voltar\n")
        
        choice = prompt("  Escolha: ", style=PROMPT_STYLE).strip()
        
        if choice == "0":
            return
        elif choice.upper() == "A":
            console.print(f"\n[red][!] APAGAR TODOS os {len(projects)} projetos![/red]")
            confirm = prompt("Digite 'APAGAR TUDO' para confirmar: ", style=PROMPT_STYLE).strip()
            if confirm == "APAGAR TUDO":
                for p in projects:
                    pm.delete(p.id)
                    if p.project_path:
                        path = Path(p.project_path) if not isinstance(p.project_path, Path) else p.project_path
                        if path.exists():
                            shutil.rmtree(path)
                console.print(f"\n[red][+] {len(projects)} projetos apagados![/red]\n")
            else:
                console.print(f"\n[yellow][!] Cancelado.[/yellow]\n")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    p = projects[idx]
                    console.print(f"\n[red]Apagar: {p.name}?[/red]")
                    confirm = prompt("Digite 'SIM' para confirmar: ", style=PROMPT_STYLE).strip()
                    if confirm.upper() == "SIM":
                        pm.delete(p.id)
                        if p.project_path:
                            path = Path(p.project_path) if not isinstance(p.project_path, Path) else p.project_path
                            if path.exists():
                                shutil.rmtree(path)
                        console.print(f"\n[red][+] '{p.name}' apagado![/red]\n")
                    else:
                        console.print(f"\n[yellow][!] Cancelado.[/yellow]\n")
            except ValueError:
                pass
        
        prompt("Pressione ENTER para voltar...", style=PROMPT_STYLE)

    def goodbye(self):
        console.clear()
        console.print("\n[gold1]Goldeneye encerrado.[/gold1]")
        console.print('[grey]"We will meet again, Mr. Bond."[/grey]\n')
