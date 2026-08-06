"""
goldeneye/utils/config.py
Carregamento de configuracao do Goldeneye.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel
from loguru import logger


class PathsConfig(BaseModel):
    projects_dir: str = "~/goldeneye/projects"
    templates_dir: str = "~/goldeneye/templates"
    config_dir: str = "~/goldeneye/config"
    logs_dir: str = "~/goldeneye/logs"


class UIConfig(BaseModel):
    theme: str = "goldeneye"
    show_progress_bars: bool = True
    date_format: str = "%d/%m/%Y"
    time_format: str = "%H:%M:%S"


class AIConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096


class ReportsConfig(BaseModel):
    default_type: str = "both"
    format: str = "pdf"
    include_evidence: bool = True
    include_graphs: bool = True


class GoldeneyeConfig(BaseModel):
    paths: PathsConfig = PathsConfig()
    ui: UIConfig = UIConfig()
    ai: AIConfig = AIConfig()
    reports: ReportsConfig = ReportsConfig()
    tools: dict = {}


class Config:
    """Gerenciador de configuracao do Goldeneye."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".goldeneye" / "config.yaml"
        self.data = self._load()

    def _load(self) -> GoldeneyeConfig:
        """Carrega configuracao do arquivo YAML."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                raw = yaml.safe_load(f)
            logger.info(f"Config carregada: {self.config_path}")
            return GoldeneyeConfig(**raw.get("goldeneye", {}))

        logger.warning(f"Config nao encontrada em {self.config_path}. Usando defaults.")
        return GoldeneyeConfig()

    def save(self):
        """Salva configuracao atual."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump({"goldeneye": self.data.model_dump()}, f)
        logger.info(f"Config salva em {self.config_path}")
