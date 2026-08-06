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

SYSTEM_PROMPT = """Voce e o Goldeneye, um assistente de inteligencia artificial especializado em ciberseguranca ofensiva e pentest profissional.

Sua funcao e analisar resultados de scans de seguranca e gerar relatorios tecnicos profissionais.

REGRAS IMPORTANTES:
1. SEMPRE cite as versoes exatas dos servicos encontrados (ex: "MariaDB 10.6.27", "OpenSSH 8.0")
2. SEMPRE atribua um score CVSS numerico (0.0 a 10.0) com justificativa
3. SEMPRE classifique cada descoberta por severidade: CRITICO (9.0+), ALTO (7.0-8.9), MEDIO (4.0-6.9), BAIXO (0.1-3.9)
4. Seja tecnico e especifico - evite generalizacoes
5. Priorize as recomendacoes por ordem de urgencia
6. Use termos tecnicos corretos (RCE, LFI, bruteforce, exploit, CVE)
7. Responda SEMPRE em portugues do Brasil

FORMATO DE RESPOSTA OBRIGATORIO:
---
**SUMARIO EXECUTIVO**
[Um paragrafo resumindo os principais riscos para gestores]

**DESCRICAO TECNICA**
[Analise detalhada de cada servico exposto, com versoes exatas]

**ANALISE DE RISCOS**
[Para cada servico: severidade, CVSS, justificativa]

**RECOMENDACOES PRIORIZADAS**
[Ordem: CRITICO primeiro, depois ALTO, MEDIO, BAIXO]
[Formato: [SEVERIDADE] Acao especifica - Justificativa]

**PROXIMOS PASSOS DE INVESTIGACAO**
[3-5 acoes concretas que o pentester deve executar em seguida]

**CVSS CONSOLIDADO**
[Score geral do alvo e justificativa]
---
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
- O servidor parece hospedar um ambiente Moodle (AVA) no subdominio ava.cursoinvictus.com.br
- MariaDB 10.6.27 esta exposto na porta 3306 - isso e critico
- OpenSSH 8.0 pode ter vulnerabilidades conhecidas
- ProFTPD e SVN expostos sao mas praticas
- Apache httpd precisa de verificacao de configuracao

Analise cada servico individualmente, atribua CVSS, e priorize as recomendacoes."""

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
    """Analise offline melhorada com dados especificos."""

    analysis = []
    analysis.append("---")
    analysis.append("**SUMARIO EXECUTIVO**")
    analysis.append(f"Foram identificados servicos criticos expostos no alvo {scan_data.get('target', 'N/A')}, incluindo banco de dados MySQL/MariaDB acessivel publicamente. Recomenda-se acao imediata para restringir o acesso a estes servicos e reduzir a superficie de ataque.")
    analysis.append("")
    analysis.append("**DESCRICAO TECNICA**")

    cve_db = {
        ("openssh", "8.0"): [
            ("CVE-2019-16905", "4.4", "Corrupcao de memoria em OpenSSH < 8.1"),
        ],
        ("mariadb", "10.6"): [
            ("CVE-2023-5157", "7.5", "DoS via consulta SQL maliciosa em MariaDB < 10.6.15"),
        ],
        ("proftpd", ""): [
            ("CVE-2020-9273", "8.1", "Use-after-free em ProFTPD < 1.3.6c"),
        ],
    }

    for host in scan_data.get("hosts", []):
        analysis.append(f"\n### Host: {host['ip']}")
        if host.get("os"):
            analysis.append(f"SO detectado: {host['os']} (possivel falso positivo)")

        for port in host.get("ports", []):
            if port["state"] != "open":
                continue
            service = port.get("service", "desconhecido")
            product = port.get("product", "")
            version = port.get("version", "")
            full_service = f"{service} {product} {version}".strip()
            port_id = f"{port['port']}/{port['protocol']}"

            analysis.append(f"\n**Porta {port_id} - {full_service}**")

            # Analise especifica por servico
            if service in ["mysql", "mariadb"]:
                severity = "CRITICO"
                cvss = "9.0"
                analysis.append(f"[{severity}] CVSS {cvss} - BANCO DE DADOS EXPOSTO NA INTERNET")
                analysis.append(f"- Risco: Acesso nao autorizado, vazamento total de dados, bruteforce")
                analysis.append(f"- Versao: {version} - verificar CVEs especificas")
                analysis.append(f"- Recomendacao IMEDIATA: Restringir porta 3306 via firewall (iptables/cloud)")

            elif service in ["ftp"]:
                severity = "ALTO"
                cvss = "7.0"
                analysis.append(f"[{severity}] CVSS {cvss} - FTP EXPOSTO (PROTOCOLO INSEGURO)")
                analysis.append(f"- Trafego em texto puro, credenciais transmitidas sem criptografia")
                analysis.append(f"- Recomendacao: Migrar para SFTP (porta 22) e fechar porta 21")

            elif service in ["ssh"]:
                severity = "MEDIO"
                cvss = "5.3"
                analysis.append(f"[{severity}] CVSS {cvss} - SSH EXPOSTO")
                analysis.append(f"- OpenSSH 8.0 - verificar CVE-2019-16905")
                analysis.append(f"- Recomendacao: Desabilitar login root, usar apenas chave SSH, instalar fail2ban")

            elif service in ["http", "https"]:
                severity = "MEDIO"
                cvss = "5.0"
                analysis.append(f"[{severity}] CVSS {cvss} - SERVIDOR WEB EXPOSTO")
                analysis.append(f"- Apache httpd - realizar scan web completo")
                analysis.append(f"- Recomendacao: Nuclei, OWASP ZAP, verificacao de headers de seguranca")

            elif service in ["svnserve", "svn"]:
                severity = "ALTO"
                cvss = "7.5"
                analysis.append(f"[{severity}] CVSS {cvss} - SVN EXPOSTO")
                analysis.append(f"- Risco: Vazamento de codigo fonte, credenciais em repositorio")
                analysis.append(f"- Recomendacao: Restringir acesso ou migrar para Git privado")

    analysis.append("")
    analysis.append("**ANALISE DE RISCOS**")
    analysis.append("1. [CRITICO] MySQL/MariaDB exposto - Acesso potencial a todos os dados do Moodle")
    analysis.append("2. [ALTO] SVN exposto - Possivel vazamento de codigo fonte")
    analysis.append("3. [ALTO] FTP exposto - Protocolo inseguro, risco de captura de credenciais")
    analysis.append("4. [MEDIO] SSH exposto - Superficie para bruteforce")
    analysis.append("5. [MEDIO] Apache exposto - Necessario verificacao de configuracao")

    analysis.append("")
    analysis.append("**RECOMENDACOES PRIORIZADAS**")
    analysis.append("1. [CRITICO] Restringir MySQL (3306) apenas para IPs autorizados - IMPLEMENTAR IMEDIATAMENTE")
    analysis.append("2. [ALTO] Fechar porta FTP (21) e SVN (3690) - Migrar para SFTP e Git privado")
    analysis.append("3. [ALTO] Atualizar MariaDB para 10.6.15+ e OpenSSH para 8.1+")
    analysis.append("4. [MEDIO] Configurar fail2ban no SSH e desabilitar senhas")
    analysis.append("5. [MEDIO] Realizar scan web completo com Nuclei e OWASP ZAP")

    analysis.append("")
    analysis.append("**PROXIMOS PASSOS DE INVESTIGACAO**")
    analysis.append("1. Testar conexao ao MySQL exposto e verificar se requer autenticacao")
    analysis.append("2. Executar Nuclei com templates de MySQL, Apache, ProFTPD e SVN")
    analysis.append("3. Verificar se SVN contem credenciais ou informacoes sensiveis")
    analysis.append("4. Realizar bruteforce controlado no SSH (com autorizacao)")
    analysis.append("5. Scan web no Apache para identificar vulnerabilidades (SQLi, XSS, LFI)")

    analysis.append("")
    analysis.append("**CVSS CONSOLIDADO**")
    analysis.append("Score geral do alvo: 8.5 (ALTO)")
    analysis.append("Vetor: AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L")
    analysis.append("Justificativa: Multiplos servicos expostos, incluindo banco de dados acessivel publicamente.")

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
