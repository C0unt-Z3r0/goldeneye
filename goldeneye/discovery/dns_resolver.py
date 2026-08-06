"""
goldeneye/discovery/dns_resolver.py
Resolucao DNS do alvo.
"""

import socket
import dns.resolver
from typing import List, Dict
from rich.console import Console

console = Console()


def resolve_target(target: str) -> Dict:
    """
    Resolve um dominio para IPs e coleta registros DNS basicos.
    Retorna dict com ips, mx, ns, txt.
    """
    result = {
        "target": target,
        "ips": [],
        "mx": [],
        "ns": [],
        "txt": [],
    }

    # Resolver IPs (A e AAAA)
    try:
        answers_a = dns.resolver.resolve(target, "A")
        for answer in answers_a:
            result["ips"].append(str(answer))
    except Exception:
        pass

    try:
        answers_aaaa = dns.resolver.resolve(target, "AAAA")
        for answer in answers_aaaa:
            result["ips"].append(str(answer))
    except Exception:
        pass

    # MX
    try:
        answers_mx = dns.resolver.resolve(target, "MX")
        for answer in answers_mx:
            result["mx"].append(str(answer.exchange))
    except Exception:
        pass

    # NS
    try:
        answers_ns = dns.resolver.resolve(target, "NS")
        for answer in answers_ns:
            result["ns"].append(str(answer))
    except Exception:
        pass

    # TXT
    try:
        answers_txt = dns.resolver.resolve(target, "TXT")
        for answer in answers_txt:
            result["txt"].append(str(answer))
    except Exception:
        pass

    return result
