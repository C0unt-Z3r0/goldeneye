import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from goldeneye.runners import testssl_runner


FIXTURE_PATH = Path(__file__).parents[1] / "examples" / "testssl_sample.synthetic.json"


def test_runner_uses_structured_json_file_and_parser(monkeypatch, tmp_path):
    fixture_payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    observed = {}

    def fake_run(cmd, **kwargs):
        observed["cmd"] = cmd
        observed["kwargs"] = kwargs
        json_path = Path(cmd[cmd.index("--jsonfile-pretty") + 1])
        json_path.write_text(json.dumps(fixture_payload), encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(testssl_runner.subprocess, "run", fake_run)

    findings = testssl_runner.run_testssl("example.invalid", 443, tmp_path)

    assert observed["cmd"][:3] == [
        "testssl",
        "--jsonfile-pretty",
        str(tmp_path / "testssl_example.invalid_443.json"),
    ]
    assert observed["kwargs"]["timeout"] == testssl_runner.DEFAULT_TIMEOUT_SECONDS
    assert len(findings) == 1
    assert findings[0]["vulnerability"] == "cipherlist_3DES_IDEA"
    assert findings[0]["severity"] == "MEDIUM"


def test_runner_does_not_claim_safe_when_json_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        testssl_runner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    findings = testssl_runner.run_testssl("example.invalid", 443, tmp_path)

    assert findings == []


def test_runner_handles_timeout_without_claiming_safe(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr(testssl_runner.subprocess, "run", fake_run)

    findings = testssl_runner.run_testssl("example.invalid", 443, tmp_path)

    assert findings == []
