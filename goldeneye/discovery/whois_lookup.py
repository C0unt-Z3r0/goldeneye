"""
goldeneye/discovery/whois_lookup.py
Consulta WHOIS para obter ranges de IP e ASN.
"""

import whois
from typing import Dict, Optional
from rich.console import Console

console = Console()


def whois_lookup(domain: str) -> Dict:
    """
    Realiza consulta WHOIS no dominio.
    Retorna dict com informacoes relevantes.
    """
    result = {
        "domain": domain,
        "registrar": None,
        "creation_date": None,
        "expiration_date": None,
        "name_servers": [],
        "org": None,
        "country": None,
        "cidr": None,
        "asn": None,
    }

    try:
        w = whois.whois(domain)

        result["registrar"] = w.registrar
        result["name_servers"] = w.name_servers or []
        result["org"] = w.org
        result["country"] = w.country

        # Datas
        if w.creation_date:
            if isinstance(w.creation_date, list):
                result["creation_date"] = str(w.creation_date[0])
            else:
                result["creation_date"] = str(w.creation_date)

        if w.expiration_date:
            if isinstance(w.expiration_date, list):
                result["expiration_date"] = str(w.expiration_date[0])
            else:
                result["expiration_date"] = str(w.expiration_date)

    except Exception as e:
        console.print(f"[yellow][!] WHOIS: {e}[/yellow]")

    return result
