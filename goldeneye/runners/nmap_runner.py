"""
goldeneye/runners/nmap_runner.py
Executor do Nmap com barra de progresso.
"""

import subprocess
import re
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()


def run_nmap(
    target: str,
    output_dir: Path,
    scan_type: str = "quick",
    ports: Optional[str] = None,
) -> Optional[Path]:
    """
    Executa Nmap no alvo e salva o XML.
    
    Args:
        target: IP ou range (ex: 192.168.1.0/24)
        output_dir: diretorio para salvar o XML
        scan_type: "quick" (top 1000), "full" (1-65535), "stealth" (SYN scan)
        ports: ports personalizadas (ex: "22,80,443,8080")
    
    Returns:
        Path do arquivo XML gerado, ou None se falhar
    """
    
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = target.replace("/", "_").replace(".", "_")
    xml_path = output_dir / f"nmap_{scan_type}_{slug}.xml"
    
    cmd = ["nmap"]
    
    # Tipo de scan
    if scan_type == "quick":
        cmd.extend(["-sV", "-sC", "-O", "--top-ports", "1000"])
    elif scan_type == "full":
        cmd.extend(["-sV", "-sC", "-O", "-p", "1-65535"])
    elif scan_type == "stealth":
        import os
    if os.environ.get("GOLDENEYE_ANON"):
        cmd.extend(["-sS", "-sV", "--top-ports", "1000", "--randomize-hosts", "-T2"])
    else:
        cmd.extend(["-sS", "-sV", "-O", "--top-ports", "1000"])
    
    # Portas personalizadas
    if ports:
        cmd.extend(["-p", ports])
    
    # Output XML
    cmd.extend(["-oX", str(xml_path)])
    
    # Alvo
    cmd.append(target)
    
    console.print(f"\n[gold1][*] Executando Nmap ({scan_type}) em {target}...[/gold1]")
    console.print(f"[grey]    Comando: {' '.join(cmd)}[/grey]\n")
    
    try:
        # Executar com barra de progresso simulada
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            
            task = progress.add_task(f"[cyan]Scanning {target}...", total=100)
            
            # Iniciar o processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            # Atualizar barra enquanto o processo roda
            # O Nmap imprime porcentagens no stdout
            while process.poll() is None:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Tentar extrair porcentagem do Nmap
                match = re.search(r'About (\d+\.?\d*)% done', line)
                if match:
                    pct = float(match.group(1))
                    progress.update(task, completed=pct)
                elif "Starting Nmap" in line:
                    progress.update(task, description=f"[cyan]Iniciando scan...")
                elif "Nmap done" in line:
                    progress.update(task, completed=100, description="[green]Scan concluido!")
            
            # Garantir 100%
            progress.update(task, completed=100, description="[green]Scan concluido!")
        
        # Verificar resultado
        if xml_path.exists() and xml_path.stat().st_size > 0:
            console.print(f"\n[green][+] Nmap concluido![/green]")
            console.print(f"[grey]    XML salvo em: {xml_path}[/grey]")
            return xml_path
        else:
            console.print(f"\n[red][!] Nmap nao gerou output.[/red]")
            return None
            
    except FileNotFoundError:
        console.print("[red][!] Nmap nao encontrado. Instale: sudo apt install nmap[/red]")
        return None
    except Exception as e:
        console.print(f"[red][!] Erro ao executar Nmap: {e}[/red]")
        return None
