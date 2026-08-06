"""
goldeneye/analyzers/false_positive_checker.py
Verificador automatico de falsos positivos.
Cruza resultados de todas as ferramentas.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style

console = Console()

GOLD = Style(color="#FFD700", bold=True)
RED = Style(color="#DC143C", bold=True)
GREEN = Style(color="#00FF7F")
YELLOW = Style(color="#FFFF00")
ORANGE = Style(color="#FF4500", bold=True)
GREY = Style(color="#666666")
CYAN = Style(color="#00CED1")

# Vulnerabilidades conhecidas por gerar falsos positivos
KNOWN_FALSE_POSITIVES = {
    "heartbleed": ["CDN", "proxy", "cloudflare", "akamai", "cloudfront"],
    "poodle": ["CDN", "proxy", "cloudflare", "akamai"],
    "freak": ["CDN", "proxy", "cloudflare"],
    "drown": ["CDN", "proxy", "cloudflare"],
    "beast": ["CDN", "proxy", "cloudflare"],
    "sweet32": ["CDN", "proxy", "cloudflare"],
    "logjam": ["CDN", "proxy"],
    "lucky13": ["cbc ciphers", "obsolete"],
    "tls 1.0": ["CDN", "proxy"],
    "tls 1.1": ["CDN", "proxy"],
    "null cipher": ["CDN", "proxy", "cloudflare"],
    "anonymous cipher": ["CDN", "proxy", "cloudflare"],
    "export cipher": ["CDN", "proxy", "cloudflare"],
}


def check_false_positives(all_results: Dict[str, List[Dict]]) -> Dict:
    """
    Analisa todos os resultados e classifica confiabilidade.
    
    all_results = {
        "nmap": [...],
        "nuclei": [...],
        "zap": [...],
        "nikto": [...],
        "testssl": [...],
        "wpscan": [...],
        "gobuster": [...],
        "sqlmap": [...],
        "hydra": [...],
        "searchsploit": [...],
    }
    """
    
    findings = []
    
    # 1. Verificar TestSSL (maior fonte de falsos positivos)
    testssl_results = all_results.get("testssl", [])
    nmap_results = all_results.get("nmap", [])
    
    # Detectar CDN nos resultados do Nmap
    has_cdn = False
    for r in nmap_results:
        if isinstance(r, dict):
            output = str(r).lower()
        else:
            output = str(r).lower()
        if any(x in output for x in ["cloudflare", "akamai", "cloudfront", "cdn", "proxy"]):
            has_cdn = True
            break
    
    for r in testssl_results:
        vuln_name = r.get("vulnerability", "").lower()
        
        # Verificar se é conhecido falso positivo
        is_known_fp = False
        reason = ""
        for known_vuln, indicators in KNOWN_FALSE_POSITIVES.items():
            if known_vuln in vuln_name:
                is_known_fp = True
                if has_cdn:
                    reason = f"CDN/Proxy detectado - {known_vuln} frequentemente e falso positivo com CDN"
                else:
                    reason = f"Verificar manualmente - {known_vuln} pode ser falso positivo"
                break
        
        confidence = "BAIXA" if (is_known_fp and has_cdn) else "MEDIA" if is_known_fp else "ALTA"
        
        findings.append({
            "tool": "TestSSL",
            "finding": r.get("vulnerability", ""),
            "confidence": confidence,
            "reason": reason or "Confirmado por teste direto",
            "recommendation": "Testar diretamente no IP (bypass CDN)" if has_cdn else "Investigar manualmente",
        })
    
    # 2. Verificar Hydra (HTTP GET falsos positivos)
    hydra_results = all_results.get("hydra", [])
    for r in hydra_results:
        output = r.get("output", "")
        if "http-get" in output.lower() and "misc: /" in output.lower():
            findings.append({
                "tool": "Hydra",
                "finding": "Credenciais HTTP GET",
                "confidence": "BAIXA",
                "reason": "HTTP GET na raiz / gera falsos positivos. Usar POST com string de falha.",
                "recommendation": "Refazer teste com POST + string de falha",
            })
    
    # 3. Cruzar resultados entre ferramentas
    zap_vulns = [r.get("name", "") for r in all_results.get("zap", [])]
    nikto_vulns = [r.get("finding", "") for r in all_results.get("nikto", [])]
    
    # Vulnerabilidades reportadas por 2+ ferramentas = mais confiaveis
    for z in zap_vulns:
        for n in nikto_vulns:
            # Verificar similaridade basica
            z_words = set(z.lower().split())
            n_words = set(n.lower().split())
            common = z_words & n_words
            if len(common) >= 3:  # 3+ palavras em comum
                findings.append({
                    "tool": "ZAP + Nikto",
                    "finding": z[:60],
                    "confidence": "ALTA",
                    "reason": "Reportado por 2 ferramentas independentes",
                    "recommendation": "Provavelmente REAL - priorizar correcao",
                })
    
    return findings


def display_false_positive_report(findings: List[Dict]):
    """Exibe relatorio de confiabilidade."""
    
    if not findings:
        console.print("\n[green][+] Nenhum falso positivo detectado.[/green]")
        return
    
    # Classificar por confianca
    high = [f for f in findings if f["confidence"] == "ALTA"]
    medium = [f for f in findings if f["confidence"] == "MEDIA"]
    low = [f for f in findings if f["confidence"] == "BAIXA"]
    
    console.print(f"\n[gold1]═══ ANALISE DE CONFIABILIDADE ═══[/gold1]")
    console.print(f"[cyan]Total: {len(findings)} descobertas analisadas[/cyan]\n")
    
    # Resumo
    summary = Table(show_header=False, box=None, padding=(0, 3))
    summary.add_column(style=GREEN)
    summary.add_column()
    summary.add_row(f"[green]● ALTA confianca:[/green]", f"{len(high)} (provavelmente reais)")
    summary.add_row(f"[yellow]● MEDIA confianca:[/yellow]", f"{len(medium)} (verificar)")
    summary.add_row(f"[red]● BAIXA confianca:[/red]", f"{len(low)} (provaveis falsos positivos)")
    
    console.print(Panel(summary, title="Resumo", border_style=GREY, padding=(1, 2)))
    
    # Detalhes
    if low:
        console.print(f"\n[red]🔴 PROVAVEIS FALSOS POSITIVOS:[/red]")
        for f in low:
            console.print(f"  [red]● {f['finding']}[/red]")
            console.print(f"    [grey]Ferramenta: {f['tool']} | {f['reason']}[/grey]")
            console.print(f"    [grey]Acao: {f['recommendation']}[/grey]\n")
    
    if high:
        console.print(f"\n[green]🟢 ALTA CONFIABILIDADE (Reais):[/green]")
        for f in high:
            console.print(f"  [green]● {f['finding']}[/green]")
            console.print(f"    [grey]{f['reason']}[/grey]\n")
    
    console.print(f"[grey]───[/grey]")
    console.print(f"[cyan]Conclusao:[/cyan] {len(high)} vulnerabilidades reais, {len(low)} provaveis falsos positivos.")
    console.print(f"[cyan]Precisao estimada:[/cyan] {len(high)/max(len(findings),1)*100:.0f}%")
