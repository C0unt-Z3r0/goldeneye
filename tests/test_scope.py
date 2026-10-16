import pytest

from goldeneye.core.scope import normalize_host, target_in_scope


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("example.com", True),
        ("https://example.com/path?q=1", True),
        ("example.com:443", True),
        ("sub.example.com", False),
        ("other.example.com", False),
        ("example.invalid", False),
        ("", False),
    ],
)
def test_hostname_scope_requires_exact_match(candidate, expected):
    assert target_in_scope("example.com", candidate) is expected


def test_scope_accepts_explicit_ip_and_cidr():
    assert target_in_scope("192.0.2.10", "192.0.2.10")
    assert target_in_scope("192.0.2.0/24", "192.0.2.10")
    assert not target_in_scope("192.0.2.0/24", "198.51.100.5")


def test_normalize_host_rejects_control_characters():
    with pytest.raises(ValueError):
        normalize_host("example.com\n--script")
