"""Helper utilities for TraceGuard AI"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary from JSON file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data: Dict[str, Any], file_path: str, indent: int = 2):
    """
    Write dictionary to JSON file.

    Args:
        data: Dictionary to write
        file_path: Output file path
        indent: JSON indentation level
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)


def get_data_files(data_dir: str, extension: str = None) -> Dict[str, List[str]]:
    """
    Recursively find all data files organized by category.

    Args:
        data_dir: Base data directory
        extension: File extension filter (e.g., '.evtx')

    Returns:
        Dictionary with categories as keys and file lists as values
    """
    data_files = {}
    data_path = Path(data_dir)

    if not data_path.exists():
        return data_files

    for category_dir in data_path.iterdir():
        if category_dir.is_dir():
            files = []
            for file_path in category_dir.rglob("*"):
                if file_path.is_file():
                    if extension is None or file_path.suffix.lower() == extension.lower():
                        files.append(str(file_path))
            if files:
                data_files[category_dir.name] = sorted(files)

    return data_files


def ensure_directory(path: str):
    """Ensure a directory exists, creating if necessary"""
    Path(path).mkdir(parents=True, exist_ok=True)
