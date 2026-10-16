import json
from pathlib import Path

import pytest

from goldeneye.parsers.testssl_parser import parse_testssl_json


FIXTURE_PATH = Path(__file__).parents[1] / "examples" / "testssl_sample.synthetic.json"


def test_synthetic_testssl_fixture_is_valid_and_explicitly_marked():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert "DADOS TOTALMENTE SINTÉTICOS" in payload["_fixture_notice"]
    assert payload["scanResult"][0]["targetHost"] == "example.invalid"
    assert payload["scanResult"][0]["ip"] == "192.0.2.10"


def test_parser_extracts_only_actionable_synthetic_findings():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    findings = parse_testssl_json(payload)

    assert len(findings) == 1
    assert findings[0] == {
        "target": "example.invalid:443",
        "vulnerability": "cipherlist_3DES_IDEA",
        "severity": "MEDIUM",
        "detail": "Synthetic example: 3DES cipher offered; not a real scan result",
    }


def test_parser_rejects_missing_scan_result():
    with pytest.raises(ValueError, match="scanResult"):
        parse_testssl_json({"targetHost": "example.invalid"})


def test_parser_does_not_report_ok_or_info_as_problems():
    findings = parse_testssl_json({
        "targetHost": "example.invalid",
        "port": "443",
        "scanResult": [{
            "protocols": [
                {"id": "TLS1_2", "severity": "OK", "finding": "offered"},
                {"id": "TLS1_3", "severity": "INFO", "finding": "not offered"},
            ]
        }],
    })

    assert findings == []
