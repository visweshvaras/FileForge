"""
System detection, dependency checking and environment diagnostics.
Cross-platform support for Windows, Linux, and macOS.
"""
import os
import shutil
import subprocess
import sys
from typing import Dict, Any, Optional

def find_libreoffice_binary() -> Optional[str]:
    """Find available LibreOffice or soffice executable across Windows, Linux, and macOS."""
    # 1. First check PATH
    names = ["soffice", "libreoffice"]
    if sys.platform == "win32":
        names = ["soffice.exe", "libreoffice.exe", "soffice", "libreoffice"]

    for name in names:
        p = shutil.which(name)
        if p and os.path.isfile(p):
            return os.path.normpath(p)

    # 2. Check standard installation paths per OS
    candidates = []
    if sys.platform == "win32":
        candidates.extend([
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "LibreOffice", "program", "soffice.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "LibreOffice", "program", "soffice.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "LibreOffice", "program", "soffice.exe"),
        ])
    elif sys.platform == "darwin":
        candidates.extend([
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        ])
    else:  # Linux / Unix
        candidates.extend([
            os.path.expanduser("~/.local/bin/soffice"),
            os.path.expanduser("~/.local/bin/libreoffice"),
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
            "/usr/local/bin/libreoffice",
            "/usr/local/bin/soffice",
            "/snap/bin/libreoffice",
            "/opt/libreoffice/program/soffice",
        ])

    for binary in candidates:
        if binary and os.path.isfile(binary):
            if sys.platform == "win32" or os.access(binary, os.X_OK):
                return os.path.normpath(binary)

    return None

def get_system_diagnostics() -> Dict[str, Any]:
    """Gather diagnostic info on available conversion engines and libraries."""
    lo_binary = find_libreoffice_binary()
    lo_version = None
    if lo_binary:
        try:
            res = subprocess.run([lo_binary, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            lo_version = res.stdout.strip()
        except Exception:
            lo_version = "Unknown version"

    # Check python-pptx
    pptx_avail = False
    try:
        import pptx
        pptx_avail = True
    except ImportError:
        pass

    # Check reportlab
    reportlab_avail = False
    try:
        import reportlab
        reportlab_avail = True
    except ImportError:
        pass

    # Check pillow
    pillow_avail = False
    try:
        import PIL
        pillow_avail = True
    except ImportError:
        pass

    # Check pdftoppm for previews
    pdftoppm_path = shutil.which("pdftoppm")

    from utils.fonts import get_registered_fonts
    registered_fonts = list(get_registered_fonts().values())

    native_ready = pptx_avail and reportlab_avail and pillow_avail

    return {
        "platform": sys.platform,
        "python_version": sys.version.split()[0],
        "libreoffice": {
            "available": lo_binary is not None,
            "path": lo_binary,
            "version": lo_version,
        },
        "native_engine": {
            "available": native_ready,
            "components": {
                "python_pptx": pptx_avail,
                "reportlab": reportlab_avail,
                "pillow": pillow_avail,
            }
        },
        "pdftoppm_available": pdftoppm_path is not None,
        "registered_fonts_count": len(registered_fonts),
        "sample_fonts": registered_fonts[:10],
        "default_engine": "libreoffice" if lo_binary else ("native" if native_ready else "none")
    }
