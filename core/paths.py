from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return PROJECT_ROOT


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def asset_path(src: str | None) -> Path | None:
    if not src:
        return None

    path = Path(src)
    if path.is_absolute():
        return path

    normalized_parts = path.parts[1:] if path.parts and path.parts[0] == "assets" else path.parts
    return resource_path("assets", *normalized_parts)


def portable_root() -> Path:
    override = os.getenv("CDD_PORTABLE_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return PROJECT_ROOT


def writable_results_dir() -> Path:
    override = os.getenv("CDD_RESULTS_DIR")
    if override:
        return Path(override).expanduser().resolve()

    portable_results = portable_root() / "results"
    try:
        portable_results.mkdir(parents=True, exist_ok=True)
        probe = portable_results / ".write_test"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
        return portable_results
    except OSError:
        local_app_data = Path(
            os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        )
        return local_app_data / "EvaluacionCDD" / "results"
