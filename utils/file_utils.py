# utils/file_utils.py
import os

def ensure_directory(path: str) -> None:
    """Ensures that the directory exists; if not, creates it.

    Args:
        path (str): Directory path.
    """
    os.makedirs(path, exist_ok=True)

def get_abs_path(relative_path: str) -> str:
    """Returns the absolute path for the given relative path.

    Args:
        relative_path (str): Relative path.

    Returns:
        str: Absolute path.
    """
    return os.path.abspath(relative_path)
