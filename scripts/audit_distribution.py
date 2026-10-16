#!/usr/bin/env python3
"""Audit Python distribution archives for known exposed target data and stale modules."""

from __future__ import annotations

import argparse
import sys
import tarfile
import zipfile
from pathlib import Path

SENSITIVE_MARKERS = (
    b"example.com",
    b"192.0.2.10",
)
REQUIRED_MODULES = (
    "goldeneye/parsers/testssl_parser.py",
    "goldeneye/runners/testssl_runner.py",
)


def read_archive(path: Path) -> dict[str, bytes]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return {
                name: archive.read(name)
                for name in archive.namelist()
                if not name.endswith("/")
            }
    if path.name.endswith(".tar.gz") or path.suffixes[-2:] == [".tar", ".gz"]:
        with tarfile.open(path, "r:gz") as archive:
            files = {}
            for member in archive.getmembers():
                if member.isfile():
                    stream = archive.extractfile(member)
                    if stream is not None:
                        files[member.name] = stream.read()
            return files
    raise ValueError(f"Formato de pacote não suportado: {path}")


def module_match(archive_name: str, module_path: str) -> bool:
    return archive_name == module_path or archive_name.endswith("/" + module_path)


def audit(path: Path, strict: bool) -> bool:
    if not path.is_file():
        print(f"[ERRO] Pacote não encontrado: {path}")
        return False

    try:
        files = read_archive(path)
    except (OSError, tarfile.TarError, zipfile.BadZipFile, ValueError) as exc:
        print(f"[ERRO] Não foi possível ler {path}: {exc}")
        return False

    print(f"\nPacote: {path} ({len(files)} arquivos)")
    for name in sorted(files):
        print(f"  {name}")

    content_hits = [
        (name, marker.decode("ascii"))
        for name, data in files.items()
        for marker in SENSITIVE_MARKERS
        if marker in data
    ]
    if content_hits:
        for name, marker in content_hits:
            print(f"[ALERTA] Marcador potencialmente sensível {marker!r} em {name}")
    else:
        print("[OK] Nenhum dos marcadores de exposição conhecidos foi encontrado.")

    if strict:
        failed = bool(content_hits)
        for module in REQUIRED_MODULES:
            matches = [name for name in files if module_match(name, module)]
            if not matches:
                print(f"[ERRO] Módulo obrigatório ausente: {module}")
                failed = True
                continue
            source = Path(module).read_bytes()
            if not any(files[name] == source for name in matches):
                print(f"[ERRO] Conteúdo empacotado está desatualizado: {module}")
                failed = True
            else:
                print(f"[OK] Conteúdo empacotado corresponde ao repositório: {module}")
        return not failed

    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="falha por marcadores ou módulos desatualizados")
    parser.add_argument("archives", nargs="+", type=Path)
    args = parser.parse_args()
    results = [audit(path, args.strict) for path in args.archives]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
