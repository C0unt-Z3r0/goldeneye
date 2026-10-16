from goldeneye.discovery import orchestrator


def test_discovery_only_probes_exactly_scoped_hostname(monkeypatch):
    probed = []
    monkeypatch.setattr(
        orchestrator,
        "resolve_target",
        lambda target: {"ips": [], "mx": [], "ns": []},
    )
    monkeypatch.setattr(orchestrator, "whois_lookup", lambda target: {})
    monkeypatch.setattr(
        orchestrator,
        "discover_subdomains",
        lambda target: [target, f"www.{target}", f"admin.{target}"],
    )

    def fake_probe(hosts):
        probed.extend(hosts)
        return []

    monkeypatch.setattr(orchestrator, "probe_hosts", fake_probe)
    monkeypatch.setattr(orchestrator, "fingerprint_urls", lambda urls: [])

    result = orchestrator.run_discovery("example.invalid")

    assert result["subdomains"] == [
        "example.invalid",
        "www.example.invalid",
        "admin.example.invalid",
    ]
    assert probed == ["example.invalid"]
