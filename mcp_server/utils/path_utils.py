from pathlib import Path

from config import WORKSPACE_ROOT


def resolve_path(path: str) -> Path:
    """
    Convert a relative path into an absolute path inside the workspace.
    """

    return (WORKSPACE_ROOT / path).resolve()


def is_safe_path(path: Path) -> bool:
    """
    Returns True only if the path is inside WORKSPACE_ROOT.
    """

    try:
        path.relative_to(WORKSPACE_ROOT)
        return True
    except ValueError:
        return False