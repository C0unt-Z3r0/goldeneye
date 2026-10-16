"""
goldeneye/runners/hydra_runner.py
Hydra 2.0 - bruteforce online com suporte a POST e string de falha.
"""

import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()
DEFAULT_TIMEOUT_SECONDS = 3600

DEFAULT_USERS = ["admin", "root", "administrator", "user", "test"]
ROCKYOU = os.path.expanduser("~/goldeneye/assets/rockyou.txt")
BR_EDU = os.path.expanduser("~/goldeneye/assets/wordlist_br_edu.txt")
WORDLIST_BR = os.path.expanduser("~/goldeneye/assets/wordlist-br/MrP4p3r") if os.path.exists(os.path.expanduser("~/goldeneye/assets/wordlist-br/MrP4p3r")) else None


def get_wordlist() -> Optional[str]:
    """Retorna a melhor wordlist disponivel."""
    if os.path.exists(ROCKYOU):
        console.print("[grey]    Wordlist: rockyou.txt[/grey]")
        return ROCKYOU
    elif WORDLIST_BR and os.path.exists(WORDLIST_BR):
        console.print("[grey]    Wordlist: MrP4p3r (BR)[/grey]")
        return WORDLIST_BR
    return None


def run_hydra(
    target: str,
    port: int,
    service: str,
    output_dir: Path,
    username: str = None,
    password: str = None,
    userlist: List[str] = None,
    passlist: List[str] = None,
    post_params: str = None,
    fail_string: str = None,
    threads: int = 4,
) -> List[Dict]:
    """Executa Hydra em um servico."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"hydra_{target}_{port}_{service}.txt"
    
    cmd = ["hydra", "-o", str(output_file), "-I", f"-t{threads}"]
    
    # Usuario
    if username:
        cmd.extend(["-l", username])
    elif userlist:
        userfile = output_dir / "users.txt"
        with open(userfile, "w") as f:
            f.write("\n".join(userlist))
        cmd.extend(["-L", str(userfile)])
    else:
        userfile = output_dir / "users.txt"
        with open(userfile, "w") as f:
            f.write("\n".join(DEFAULT_USERS))
        cmd.extend(["-L", str(userfile)])
    
    # Senha
    if password:
        cmd.extend(["-p", password])
    elif passlist:
        passfile = output_dir / "passwords.txt"
        with open(passfile, "w") as f:
            f.write("\n".join(passlist))
        cmd.extend(["-P", str(passfile)])
    else:
        wordlist = get_wordlist()
        if wordlist:
            cmd.extend(["-P", wordlist])
        else:
            passfile = output_dir / "passwords.txt"
            with open(passfile, "w") as f:
                f.write("\n".join(["admin", "password", "123456", "admin123", "root", "test"]))
            cmd.extend(["-P", str(passfile)])
    
    # Servico e alvo
    if service in ["http-get"] and not post_params:
        console.print("[yellow][!] ALERTA: GET simples pode gerar FALSOS POSITIVOS![/yellow]")
        console.print("[yellow][!] Para resultados confiaveis, use POST com string de falha.[/yellow]")
    if service in ["http", "https"] and post_params:
        # Modo POST com parametros
        method = "http-post-form" if service in ["http", "https"] else service
        url_path = post_params.get("url", "/")
        params = post_params.get("params", "username=^USER^&password=^PASS^")
        fail = fail_string or post_params.get("fail", "Invalid")
        cmd.extend([target, method, f"{url_path}:{params}:F={fail}"])
    elif service in ["http-get", "http-post-form"]:
        cmd.extend([target, service])
    else:
        cmd.extend(["-s", str(port), target, service])
    
    console.print(f"\n[cyan][*] Hydra em {target}:{port} ({service})...[/cyan]")
    
    results = []
    try:
        output_file.unlink(missing_ok=True)
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            check=False,
        )
        if process.returncode != 0:
            console.print(f"[yellow][!] Hydra terminou com código {process.returncode}; valide o resultado antes de concluir.[/yellow]")
        lines = process.stdout.splitlines()
        for line in lines:
            line = line.strip()
            if line and "login:" in line.lower() and "password:" in line.lower():
                if fail_string and fail_string.lower() in line.lower():
                    continue
                results.append({"target": target, "port": port, "service": service, "output": line, "found": True})

        if output_file.exists() and output_file.stat().st_size > 0:
            with output_file.open(encoding="utf-8", errors="replace") as stream:
                for line in stream:
                    if "login:" in line.lower() and "password:" in line.lower():
                        if fail_string and fail_string.lower() in line.lower():
                            continue
                        results.append({"target": target, "port": port, "service": service, "output": line.strip(), "found": True})

        unique = []
        seen = set()
        for result in results:
            if result["output"] not in seen:
                seen.add(result["output"])
                unique.append(result)
        results = unique
        if results:
            console.print(f"[red][!] {len(results)} resultado(s) de credenciais reportado(s); confirme manualmente antes de classificá-los como válidos.[/red]")
        elif process.returncode == 0:
            console.print("[green][+] Hydra terminou sem reportar credenciais.[/green]")
        else:
            console.print("[yellow][!] Hydra não confirmou resultados; execução inconclusiva.[/yellow]")
    except FileNotFoundError:
        console.print("[red][!] Hydra não encontrado.[/red]")
    except subprocess.TimeoutExpired:
        console.print(f"[red][!] Hydra excedeu {DEFAULT_TIMEOUT_SECONDS}s; execução inconclusiva.[/red]")
    except OSError as exc:
        console.print(f"[red][!] Erro de I/O no Hydra: {exc}[/red]")

    return results


def run_hydra_scan(targets: List[tuple], output_dir: Path) -> List[Dict]:
    """Executa Hydra em lote com menu interativo."""
    from prompt_toolkit import prompt
    from prompt_toolkit.styles import Style as PTStyle
    
    PROMPT_STYLE = PTStyle.from_dict({"prompt": "#FFD700 bold", "": "#FFFFFF"})
    
    bruteforce_services = ["ssh", "ftp", "mysql", "mssql", "rdp", "smb", "telnet", "http", "https", "http-get"]
    
    # Mostrar servicos disponiveis
    console.print(f"\n[cyan]Servicos disponiveis para bruteforce:[/cyan]")
    valid_targets = []
    for ip, port, service in targets:
        if service.lower() in bruteforce_services:
            console.print(f"  [{len(valid_targets)+1}] {ip}:{port} ({service})")
            valid_targets.append((ip, port, service))
    
    if not valid_targets:
        console.print("[yellow][!] Nenhum servico bruteforcavel.[/yellow]")
        return []
    
    console.print(f"\n  [A] Todos")
    console.print(f"  [0] Voltar\n")
    
    choice = prompt("  Escolha: ", style=PROMPT_STYLE).strip()
    
    selected = []
    if choice.upper() == "A":
        selected = valid_targets
    elif choice == "0":
        return []
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(valid_targets):
                selected = [valid_targets[idx]]
        except ValueError:
            return []
    
    # Perguntar se quer configurar POST/string de falha para HTTP
    post_params = None
    fail_string = None
    
    has_http = any(s in ["http", "https"] for _, _, s in selected)
    if has_http:
        console.print(f"\n[cyan]Configuracao HTTP:[/cyan]")
        console.print(f"  [1] GET simples (raiz /)")
        console.print(f"  [2] POST com formulario\n")
        http_choice = prompt("  Escolha [1-2]: ", style=PROMPT_STYLE).strip()
        
        if http_choice == "2":
            url = prompt("  URL do formulario (ex: /login.php): ", style=PROMPT_STYLE).strip()
            params = prompt("  Parametros (ex: user=^USER^&pass=^PASS^): ", style=PROMPT_STYLE).strip()
            fail = prompt("  String de falha (ex: Login invalido): ", style=PROMPT_STYLE).strip()
            post_params = {"url": url or "/", "params": params or "username=^USER^&password=^PASS^", "fail": fail}
            fail_string = fail
    
    # Perguntar wordlist
    console.print(f"\n[cyan]Wordlist:[/cyan]")
    console.print(f"  [1] Rapida (BR Educacao - 70 senhas)")
    console.print(f"  [2] Rockyou (14 milhoes)")
    console.print(f"  [3] Personalizada\n")
    wl_choice = prompt("  Escolha [1-3] (ENTER=1): ", style=PROMPT_STYLE).strip()
    
    custom_wordlist = None
    if wl_choice == "2":
        custom_wordlist = ROCKYOU
    elif wl_choice == "3":
        custom_path = prompt("  Caminho da wordlist: ", style=PROMPT_STYLE).strip()
        if custom_path and os.path.exists(os.path.expanduser(custom_path)):
            custom_wordlist = os.path.expanduser(custom_path)
    else:
        custom_wordlist = BR_EDU
    
    # Perguntar threads
    threads = prompt("  Threads [4-16] (ENTER=4): ", style=PROMPT_STYLE).strip()
    try:
        threads = int(threads) if threads else 4
    except ValueError:
        threads = 4
    
    # Executar
    all_results = []
    for ip, port, service in selected:
        svc = "http-get" if service in ["http", "https"] and not post_params else service.lower()
        results = run_hydra(
            ip, int(port), svc, output_dir,
            post_params=post_params, fail_string=fail_string, threads=threads,
            passlist=open(custom_wordlist).read().splitlines() if custom_wordlist and os.path.exists(custom_wordlist) else None,
        )
        all_results.extend(results)
    
    return all_results
