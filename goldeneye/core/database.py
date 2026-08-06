"""
goldeneye/core/database.py
Conexao com SQLite e gerenciamento do banco de dados.
"""

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DB_DIR = Path.home() / ".goldeneye"
DB_PATH = DB_DIR / "goldeneye.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Session:
    """Retorna uma sessao do banco de dados."""
    return SessionLocal()


def init_db():
    """Cria todas as tabelas no banco."""
    from goldeneye.core.models import Base
    Base.metadata.create_all(bind=engine)
