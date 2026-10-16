import tomllib
from pathlib import Path


def test_runtime_import_dependencies_are_declared():
    project = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    dependencies = {item.split(">=")[0].split("==")[0].lower().replace("_", "-") for item in project["dependencies"]}
    assert "ollama" in dependencies
    assert "python-docx" in dependencies
    assert "jinja2" in dependencies
