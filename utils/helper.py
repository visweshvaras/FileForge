"""
General utility functions with cross-platform support (Windows, macOS, Linux).
"""
import os
import sys
import subprocess
import shutil

def open_file_or_dir(path: str):
    """
    Open a file or directory in default system file manager / viewer.
    Supports Windows (os.startfile), macOS (open), and Linux (xdg-open).
    """
    if not path or not os.path.exists(path):
        return
    try:
        if os.name == 'nt':
            # Windows native
            os.startfile(os.path.normpath(path))
        elif sys.platform == 'darwin':
            # macOS native
            subprocess.Popen(['open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Linux / Unix
            xdg_open = shutil.which("xdg-open")
            if xdg_open:
                subprocess.Popen([xdg_open, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    if size_bytes == 0:
        return "0 Bytes"
    for unit in ['Bytes', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
