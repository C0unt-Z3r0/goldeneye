"""
goldeneye/discovery/fingerprint.py
Fingerprinting de tecnologias usando WhatWeb.
"""

import subprocess
import json
from typing import List, Dict
from rich.console import Console

console = Console()


def fingerprint_urls(urls: List[str]) -> List[Dict]:
    """
    Identifica tecnologias em URLs usando WhatWeb.
    Retorna lista de dicts com url, technologies.
    """
    results = []

    for url in urls:
        try:
            cmd = ["whatweb", "--log-json=/dev/stdout", url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.splitlines():
                    try:
                        data = json.loads(line)
                        results.append({
                            "url": url,
                            "target": data.get("target", url),
                            "plugins": data.get("plugins", {}),
                        })
                    except json.JSONDecodeError:
                        pass
        except FileNotFoundError:
            console.print("[yellow][!] WhatWeb nao encontrado. Instale: sudo apt install whatweb[/yellow]")
            break
        except subprocess.TimeoutExpired:
            console.print(f"[yellow][!] WhatWeb timeout: {url}[/yellow]")
        except Exception as e:
            console.print(f"[yellow][!] WhatWeb erro em {url}: {e}[/yellow]")

    return results
