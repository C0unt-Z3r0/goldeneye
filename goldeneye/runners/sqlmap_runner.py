"""
goldeneye/runners/sqlmap_runner.py
Executor do SQLMap - deteccao de SQL Injection.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console

console = Console()


def run_sqlmap(
    target_url: str,
    output_dir: Path,
    crawl_depth: int = 2,
    risk: int = 3,
    level: int = 3,
    extra_args: str = "",
) -> Optional[Path]:
    """Executa SQLMap em uma URL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = target_url.replace("://", "_").replace("/", "_").replace(":", "_").replace(".", "_")[:50]
    output_path = output_dir / f"sqlmap_{slug}.txt"
    
    cmd = [
        "sqlmap", "-u", target_url,
        f"--crawl={crawl_depth}", "--batch", "--level", str(level), "--risk", str(risk),
        "--output-dir", str(output_dir), "--threads", "4",
    ]
    
    if extra_args:
        for arg in extra_args.split():
            if arg:
                cmd.append(arg)
    
    console.print(f"\n[cyan][*] SQLMap em {target_url}...[/cyan]")
    console.print(f"[grey]    Risk={risk} Level={level} Crawl={crawl_depth}[/grey]")
    
    try:
        with open(output_path, "w") as f:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                f.write(line)
                if "available databases" in line.lower():
                    console.print(f"[red][!] Bancos de dados encontrados![/red]")
                elif "is vulnerable" in line.lower():
                    console.print(f"[red][!] {line.strip()}[/red]")
            process.wait()
        
        if output_path.exists() and output_path.stat().st_size > 0:
            console.print(f"[green][+] SQLMap concluido.[/green]")
            return output_path
    except FileNotFoundError:
        console.print("[red][!] SQLMap nao encontrado.[/red]")
    except Exception as e:
        console.print(f"[red][!] Erro: {e}[/red]")
    
    return None


def run_sqlmap_batch(targets: List[str], output_dir: Path) -> List[Dict]:
    """Executa SQLMap em lote."""
    results = []
    
    for target in targets:
        extra = ""
        clean = target
        if " --" in target:
            parts = target.split(" --", 1)
            clean = parts[0]
            extra = " --" + parts[1]
        
        output = run_sqlmap(clean, output_dir, extra_args=extra)
        
        if output and output.exists():
            with open(output) as f:
                content = f.read()
            
            result = {"url": clean, "vulnerable": False, "output_file": str(output), "databases": []}
            
            if "is vulnerable" in content.lower():
                result["vulnerable"] = True
            
            # Extrair bancos de dados
            db_section = re.search(r"available databases", content)
            if db_section:
                result["vulnerable"] = True
                start = db_section.end()
                dbs = re.findall(r'\[\*\]\s*\[?([a-zA-Z_]\w*)\]?', content[start:start+1000])
                dbs = [d for d in dbs if d not in ['ending', 'WARNING', 'INFO', 'ERROR']]
                result["databases"] = dbs
                result["db_count"] = len(dbs)
                console.print(f"[red][!] {len(dbs)} bancos encontrados:[/red]")
                for db in dbs:
                    console.print(f"    [red][*] {db}[/red]")
            
            # Extrair tabelas
            tables_section = re.search(r"Database: (\w+)", content)
            tables_count = re.search(r"\[(\d+) tables?\]", content)
            if tables_section and tables_count:
                db_name = tables_section.group(1)
                table_count = tables_count.group(1)
                console.print(f"[red][!] {table_count} tabelas em {db_name}:[/red]")
                result["tables"] = table_count
            
            # Extrair dados dump
            dump_section = re.search(r"Table: (\w+)", content)
            dump_count = re.search(r"\[(\d+) entr", content)
            if dump_section and dump_count:
                table_name = dump_section.group(1)
                entry_count = dump_count.group(1)
                console.print(f"[red][!] {entry_count} registros extraidos da tabela {table_name}![/red]")
                result["dumped"] = True
                result["entries"] = entry_count
            
            results.append(result)
    
    return results
