"""
goldeneye/runners/zap_runner.py
OWASP ZAP - usando curl (confiavel no WSL).
"""

import subprocess
import time
import json
import os
from pathlib import Path
from typing import List, Dict
from rich.console import Console

console = Console()
ZAP_URL = "http://127.0.0.1:8080"


def zap_api(endpoint: str, params: dict = None) -> dict:
    """Chama API do ZAP via curl."""
    url = f"{ZAP_URL}{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "5", url],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception:
        pass
    return {}


def is_zap_running() -> bool:
    """Verifica se ZAP esta rodando."""
    r = zap_api("/JSON/core/view/version/")
    return "version" in r


def run_spider(target_url: str):
    """Spider."""
    console.print(f"[cyan][*] Spider em {target_url}...[/cyan]")
    r = zap_api("/JSON/spider/action/scan/", {"url": target_url, "maxChildren": "5", "recurse": "true"})
    spider_id = r.get("scan", "")
    if not spider_id:
        console.print("[yellow][!] Spider nao iniciou.[/yellow]")
        return
    dots = 0
    while True:
        status = zap_api("/JSON/spider/view/status/", {"scanId": spider_id})
        pct = status.get("status", "0")
        dots = (dots + 1) % 4
        console.print(f"\r[grey]  Spider: {pct}% {'.' * dots}   [/grey]", end="")
        if pct == "100":
            break
        time.sleep(1)
    console.print("\r[green]  Spider concluido!          [/green]")


def run_active_scan(target_url: str):
    """Scan ativo."""
    console.print(f"[cyan][*] Scan ativo em {target_url}...[/cyan]")
    r = zap_api("/JSON/ascan/action/scan/", {"url": target_url, "recurse": "true"})
    scan_id = r.get("scan", "")
    if not scan_id:
        console.print("[yellow][!] Scan ativo nao iniciou.[/yellow]")
        return
    dots = 0
    while True:
        status = zap_api("/JSON/ascan/view/status/", {"scanId": scan_id})
        pct = status.get("status", "0")
        dots = (dots + 1) % 4
        console.print(f"\r[grey]  Scan ativo: {pct}% {'.' * dots}   [/grey]", end="")
        if pct == "100":
            break
        time.sleep(2)
    console.print("\r[green]  Scan ativo concluido!          [/green]")


def get_alerts(target_url: str) -> List[Dict]:
    """Alertas."""
    r = zap_api("/JSON/core/view/alerts/", {"baseurl": target_url})
    return r.get("alerts", [])


def run_zap_scan(targets: List[str], output_dir: Path) -> List[Dict]:
    """Scan ZAP completo."""
    if not is_zap_running():
        console.print("[red][!] ZAP nao esta rodando.[/red]")
        console.print("[grey]  Inicie: zaproxy -daemon -host 127.0.0.1 -port 8080 &[/grey]")
        return []
    
    version = zap_api("/JSON/core/view/version/").get("version", "?")
    console.print(f"[green][+] ZAP conectado! v{version}[/green]")
    
    results = []
    for target in targets:
        console.print(f"\n[gold1][*] Alvo: {target}[/gold1]")
        run_spider(target)
        run_active_scan(target)
        alerts = get_alerts(target)
        if alerts:
            console.print(f"[green][+] {len(alerts)} vulnerabilidades![/green]")
        for alert in alerts:
            results.append({
                "name": alert.get("alert", ""),
                "severity": alert.get("risk", "Info"),
                "url": alert.get("url", ""),
                "description": alert.get("description", ""),
                "solution": alert.get("solution", ""),
                "cwe": alert.get("cweid", ""),
                "source": "OWASP ZAP",
            })
    
    if results:
        json_path = output_dir / "zap_results.json"
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green][+] Salvo: {json_path}[/green]")
    
    return results
