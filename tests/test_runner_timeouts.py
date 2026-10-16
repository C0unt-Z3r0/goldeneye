import subprocess

from goldeneye.runners import hydra_runner, nmap_runner, sqlmap_runner


def test_nmap_timeout_is_inconclusive(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(nmap_runner.subprocess, "run", timeout)
    assert nmap_runner.run_nmap("example.invalid", tmp_path, timeout=1) is None


def test_sqlmap_timeout_is_inconclusive(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(sqlmap_runner.subprocess, "run", timeout)
    assert sqlmap_runner.run_sqlmap("https://example.invalid/?q=1", tmp_path) is None


def test_hydra_timeout_is_inconclusive(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(hydra_runner.subprocess, "run", timeout)
    results = hydra_runner.run_hydra(
        target="example.invalid",
        port=22,
        service="ssh",
        output_dir=tmp_path,
        username="synthetic-user",
        password="synthetic-secret",
    )
    assert results == []


def test_nmap_top100_profile_uses_valid_flag(monkeypatch, tmp_path):
    from pathlib import Path
    from types import SimpleNamespace

    observed = {}

    def fake_run(cmd, **kwargs):
        observed["cmd"] = cmd
        xml_path = Path(cmd[cmd.index("-oX") + 1])
        xml_path.write_text("<nmaprun />", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(nmap_runner.subprocess, "run", fake_run)
    result = nmap_runner.run_nmap("example.invalid", tmp_path, ports="top100")

    assert result is not None
    assert "--top-ports" in observed["cmd"]
    assert observed["cmd"][observed["cmd"].index("--top-ports") + 1] == "100"
    assert "-p" not in observed["cmd"]


def test_ffuf_timeout_is_inconclusive(monkeypatch, tmp_path):
    from goldeneye.runners import ffuf_runner

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(ffuf_runner.subprocess, "run", timeout)
    assert ffuf_runner.run_ffuf("https://example.invalid", tmp_path) == []


def test_gobuster_timeout_is_inconclusive(monkeypatch, tmp_path):
    from goldeneye.runners import gobuster_runner

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(gobuster_runner.subprocess, "run", timeout)
    assert gobuster_runner.run_gobuster("https://example.invalid", tmp_path) == []


def test_nikto_timeout_is_inconclusive(monkeypatch, tmp_path):
    from goldeneye.runners import nikto_runner

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(nikto_runner.subprocess, "run", timeout)
    assert nikto_runner.run_nikto("https://example.invalid", tmp_path) == []


def test_wpscan_timeout_is_inconclusive(monkeypatch, tmp_path):
    from goldeneye.runners import wpscan_runner

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(wpscan_runner.subprocess, "run", timeout)
    assert wpscan_runner.run_wpscan("https://example.invalid", tmp_path) == []
