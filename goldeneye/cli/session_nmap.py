    def _run_nmap_scan(self):
        """Executa scan Nmap no alvo do projeto."""
        from goldeneye.cli.menu import clear_and_show_header
        from goldeneye.runners.nmap_runner import run_nmap
        from goldeneye.parsers.nmap_parser import parse_nmap_xml, display_nmap_results
        
        clear_and_show_header(f"NMAP SCAN - {self.current_project_name}")
        
        console.print(f"[cyan]Alvo: {self.current_target}[/cyan]\n")
        console.print("[gold1]Tipo de scan:[/gold1]")
        console.print("  [1] Rapido (top 1000 portas, padrao)")
        console.print("  [2] Completo (1-65535)")
        console.print("  [3] Stealth (SYN scan)")
        console.print("  [4] Personalizado (escolher portas)\n")
        
        choice = prompt("  Escolha [1-4]: ", style=PROMPT_STYLE).strip()
        
        scan_type = "quick"
        ports = None
        
        if choice == "2":
            scan_type = "full"
            console.print("[yellow][!] Scan completo pode levar horas![/yellow]")
        elif choice == "3":
            scan_type = "stealth"
        elif choice == "4":
            ports = prompt("  Portas (ex: 22,80,443,8080): ", style=PROMPT_STYLE).strip()
        
        xml_path = run_nmap(
            target=self.current_target,
            output_dir=self.current_project_path / "scans" if self.current_project_path else Path("."),
            scan_type=scan_type,
            ports=ports,
        )
        
        if xml_path and xml_path.exists():
            data = parse_nmap_xml(xml_path)
            display_nmap_results(data)
