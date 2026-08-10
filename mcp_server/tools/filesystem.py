from pathlib import Path

from config import MAX_FILE_SIZE
from config import WORKSPACE_ROOT

from utils.path_utils import (
    resolve_path,
    is_safe_path
)


def list_files(path: str = ""):
    """
    List all files inside the given directory.
    """

    resolved = resolve_path(path)

    if not is_safe_path(resolved):
        return {
            "success": False,
            "message": "Access denied."
        }

    if not resolved.exists():
        return {
            "success": False,
            "message": "Directory not found."
        }

    if not resolved.is_dir():
        return {
            "success": False,
            "message": "Path is not a directory."
        }

    files = []

    for item in resolved.iterdir():
        files.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file"
        })

    return {
        "success": True,
        "count": len(files),
        "files": files
    }


def read_file(path: str):
    """
    Read a text file from the configured workspace.
    """

    resolved = resolve_path(path)

    if not is_safe_path(resolved):
        return {
            "success": False,
            "message": "Access denied."
        }

    if not resolved.exists():
        return {
            "success": False,
            "message": "File not found."
        }

    if resolved.is_dir():
        return {
            "success": False,
            "message": "Expected a file but received a directory."
        }

    size = resolved.stat().st_size

    if size > MAX_FILE_SIZE:
        return {
            "success": False,
            "message": "File exceeds maximum allowed size."
        }

    try:
        with open(resolved, "r", encoding="utf-8") as f:
            content = f.read()

    except UnicodeDecodeError:
        return {
            "success": False,
            "message": "Binary files are not supported."
        }

    return {
        "success": True,
        "path": str(resolved.relative_to(WORKSPACE_ROOT)),
        "size": size,
        "content": content
    }