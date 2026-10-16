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
