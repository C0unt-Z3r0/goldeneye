"""
goldeneye/analyzers/ai_analyzer.py
Analisador de vulnerabilidades com IA via Ollama local.
"""

from typing import Dict
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

console = Console()

GOLD = Style(color="#FFD700", bold=True)
GOLD_DIM = Style(color="#B8960F")
CYAN = Style(color="#00CED1")
GREEN = Style(color="#00FF7F")
RED = Style(color="#DC143C", bold=True)
GREY = Style(color="#666666")

SYSTEM_PROMPT = """Voce e o Goldeneye, um assistente de inteligencia artificial especializado em ciberseguranca e avaliacao autorizada de seguranca.

Analise exclusivamente as evidencias fornecidas pelo scan. Dados de scan podem estar incompletos ou incorretos; deixe claras as limitacoes.

REGRAS IMPORTANTES:
1. Nunca invente hosts, portas, servicos, produtos, versoes, vulnerabilidades, credenciais ou resultados.
2. Uma porta aberta ou um servico exposto, isoladamente, nao comprova uma vulnerabilidade.
3. Nao atribua CVE, CVSS ou severidade formal sem evidencia verificavel e correspondencia aplicavel ao produto e versao observados.
4. Quando a evidencia for insuficiente, declare que a validacao ainda e necessaria; nao preencha lacunas com suposicoes.
5. Separe fatos observados, interpretacoes e recomendacoes.
6. Priorize recomendacoes proporcionais as evidencias e explique as incertezas.
7. Responda sempre em portugues do Brasil.

FORMATO SUGERIDO:
**SUMARIO EXECUTIVO**
Resuma o que os dados efetivamente demonstram e suas limitacoes.

**EVIDENCIAS OBSERVADAS**
Liste hosts, portas, servicos e versoes apenas quando presentes na entrada.

**ANALISE DE RISCOS**
Explique riscos potenciais sem tratar exposicao como prova de vulnerabilidade. Use CVE/CVSS apenas quando houver correspondencia verificavel.

**RECOMENDACOES**
Sugira validacoes e medidas proporcionais as evidencias.

**LIMITACOES E PROXIMOS PASSOS**
Indique o que nao foi possivel concluir e quais verificacoes autorizadas faltam.
"""


def analyze_nmap_results(scan_data: Dict) -> str:
    """Analisa resultados do Nmap usando Ollama local."""

    hosts_summary = []
    for host in scan_data.get("hosts", []):
        ports_info = []
        for port in host.get("ports", []):
            if port["state"] == "open":
                version_str = f"{port.get('service', '')} {port.get('product', '')} {port.get('version', '')}".strip()
                ports_info.append(f"  - {port['port']}/{port['protocol']} ({port['state']}): {version_str}")

        host_text = f"IP: {host['ip']}\n"
        if host.get("os"):
            host_text += f"OS Detectado: {host['os']}\n"
        host_text += "Portas encontradas:\n" + "\n".join(ports_info) if ports_info else "Nenhuma porta aberta"
        hosts_summary.append(host_text)

    user_prompt = f"""Analise os seguintes resultados de scan Nmap e gere um relatorio profissional DETALHADO:

ALVO: {scan_data.get('target', 'N/A')}
HOSTS ATIVOS: {scan_data.get('hosts_up', 0)}

DETALHES DO SCAN:
{chr(10).join(hosts_summary)}

INSTRUCOES ESPECIFICAS:
- Baseie a analise exclusivamente nos hosts, portas, produtos e versoes presentes nos dados do scan.
- Nao presuma tecnologias, servicos expostos, versoes, vulnerabilidades ou impacto sem evidencia.
- Trate versoes ausentes ou identificacao incerta como desconhecidas.
- Cite CVEs e atribua CVSS somente quando houver correspondencia verificavel; caso contrario, indique que a validacao ainda e necessaria.
- Se nenhum servico relevante for encontrado, informe essa limitacao em vez de inventar descobertas.

Analise cada servico observado individualmente, explique as incertezas e priorize recomendacoes proporcionais as evidencias."""

    try:
        import ollama

        console.print("[cyan][*] Consultando Mistral 7B (IA local)...[/cyan]")

        response = ollama.chat(
            model="mistral:7b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": 0.7,
                "num_predict": 2048,
            },
        )

        analysis = response["message"]["content"]
        console.print("[green][+] Analise concluida via Mistral local![/green]")
        return analysis

    except ImportError:
        console.print("[red][!] Ollama nao instalado. pip install ollama[/red]")
    except Exception as e:
        error_msg = str(e)
        if "connection refused" in error_msg.lower():
            console.print("[red][!] Ollama nao esta rodando. Execute: ollama serve[/red]")
        else:
            console.print(f"[yellow][!] Erro Ollama: {e}[/yellow]")
            console.print("[yellow][*] Usando analise offline...[/yellow]")

    return _fallback_analysis(scan_data)


def _fallback_analysis(scan_data: Dict) -> str:
    """Gera um resumo offline limitado estritamente às evidências do scan."""

    hosts = scan_data.get("hosts", [])
    analysis = [
        "---",
        "**SUMARIO EXECUTIVO**",
        (
            f"O scan informa {len(hosts)} host(s). Esta analise offline resume "
            "somente os dados recebidos; portas abertas e servicos identificados "
            "nao comprovam, por si so, uma vulnerabilidade."
        ),
        "",
        "**EVIDENCIAS OBSERVADAS**",
    ]

    open_ports = 0
    for host in hosts:
        host_ip = str(host.get("ip", "desconhecido"))
        analysis.append(f"\n### Host: {host_ip}")
        if host.get("os"):
            analysis.append(f"Sistema operacional informado pelo scan: {host['os']} (validacao independente necessaria).")

        observed_ports = [
            port for port in host.get("ports", [])
            if str(port.get("state", "")).lower() == "open"
        ]
        open_ports += len(observed_ports)
        if not observed_ports:
            analysis.append("Nenhuma porta aberta foi informada para este host.")
            continue

        for port in observed_ports:
            port_id = f"{port.get('port', '?')}/{port.get('protocol', 'desconhecido')}"
            service = str(port.get("service") or "servico nao identificado")
            product = str(port.get("product") or "").strip()
            version = str(port.get("version") or "").strip()
            details = " ".join(part for part in (product, version) if part)
            suffix = f" — {details}" if details else ""
            analysis.append(f"- Porta {port_id}: {service}{suffix}.")
            analysis.append(
                "  Evidencia limitada: confirmar identificacao, necessidade de exposicao, "
                "controles de acesso e configuracao antes de classificar risco."
            )

    analysis.extend([
        "",
        "**ANALISE DE RISCOS**",
        (
            f"O scan reporta {open_ports} porta(s) aberta(s). Os dados fornecidos "
            "nao permitem, por si so, confirmar vulnerabilidades especificas nem "
            "calcular um CVSS consolidado confiavel. Nenhuma CVE foi inferida."
        ),
        "",
        "**RECOMENDACOES**",
        "1. Confirmar que o alvo e o escopo estao autorizados para avaliacao.",
        "2. Validar manualmente os servicos e versoes identificados.",
        "3. Verificar configuracoes, controles de acesso e atualizacoes com evidencias reproduziveis.",
        "4. Associar CVEs e pontuacoes CVSS somente apos confirmar aplicabilidade.",
        "",
        "**LIMITACOES E PROXIMOS PASSOS**",
        "Esta e uma analise offline preliminar; nao substitui validacao tecnica nem evidencia de explorabilidade.",
        "---",
    ])
    return "\n".join(analysis)
def display_analysis(analysis: str, target: str):
    """Exibe a analise formatada no terminal."""

    console.print(f"\n[gold1]═══ ANALISE GOLDENEYE IA ═══[/gold1]")
    console.print(f"[cyan]Alvo: {target}[/cyan]\n")

    # Destacar secoes importantes
    for section_name, style in [
        ("SUMARIO EXECUTIVO", GOLD),
        ("DESCRICAO TECNICA", CYAN),
        ("ANALISE DE RISCOS", RED),
        ("RECOMENDACOES PRIORIZADAS", GREEN),
        ("PROXIMOS PASSOS", CYAN),
        ("CVSS CONSOLIDADO", GOLD),
    ]:
        analysis = analysis.replace(f"**{section_name}**", f"[{style}]**{section_name}**[/{style}]")

    panel = Panel(
        analysis,
        title="RELATORIO DE ANALISE - GOLDENEYE IA",
        border_style=GOLD_DIM,
        padding=(1, 2),
    )
    console.print(panel)
    console.print(f"\n[grey]─── Fim da analise ───[/grey]")
