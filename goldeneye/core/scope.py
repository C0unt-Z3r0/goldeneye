"""Validacao de alvos contra o escopo explicitamente autorizado do projeto."""

import ipaddress
from urllib.parse import urlsplit


def normalize_host(value: str) -> str:
    """Extrai e normaliza host de URL, hostname, IP ou CIDR."""
    raw = str(value or "").strip()
    if not raw or any(ch in raw for ch in "\r\n\t"):
        raise ValueError("Alvo vazio ou contendo caracteres de controle.")

    candidate = raw if "://" in raw else f"//{raw}"
    parsed = urlsplit(candidate)
    host = parsed.hostname
    if not host:
        raise ValueError("Alvo inválido: informe hostname, IP, CIDR ou URL.")
    return host.rstrip(".").lower()


def target_in_scope(scope: str, candidate: str) -> bool:
    """Permite apenas correspondência exata com entradas explícitas de escopo.

    Entradas de escopo podem ser hostnames, IPs, CIDRs ou URLs. Subdomínios
    não são autorizados implicitamente.
    """
    try:
        candidate_host = normalize_host(candidate)
    except ValueError:
        return False

    for entry in str(scope or "").replace(",", "\n").splitlines():
        entry = entry.strip()
        if not entry:
            continue
        try:
            scope_host = normalize_host(entry)
        except ValueError:
            continue

        try:
            network = ipaddress.ip_network(scope_host, strict=False)
            address = ipaddress.ip_address(candidate_host)
            if address in network:
                return True
            continue
        except ValueError:
            pass

        if candidate_host == scope_host:
            return True

    return False
