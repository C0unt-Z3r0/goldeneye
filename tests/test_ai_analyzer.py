from goldeneye.analyzers.ai_analyzer import _fallback_analysis


def test_fallback_does_not_invent_findings_for_empty_scan():
    report = _fallback_analysis({"target": "example.invalid", "hosts": [], "hosts_up": 0})

    assert "0 host(s)" in report
    assert "Nenhuma CVE foi inferida." in report
    assert "MySQL/MariaDB" not in report
    assert "CVE-2019-16905" not in report
    assert "8.5" not in report


def test_fallback_only_describes_services_present_in_scan():
    report = _fallback_analysis({
        "target": "example.invalid",
        "hosts": [{
            "ip": "192.0.2.10",
            "ports": [
                {
                    "port": "22",
                    "protocol": "tcp",
                    "state": "open",
                    "service": "ssh",
                    "product": "OpenSSH",
                    "version": "9.9",
                }
            ],
        }],
    })

    assert "192.0.2.10" in report
    assert "22/tcp: ssh — OpenSSH 9.9" in report
    assert "MySQL/MariaDB" not in report
    assert "CVE-2019-16905" not in report
    assert "8.5" not in report
    assert "nao comprovam" in report
