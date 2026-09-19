"""
Convert PowerPoint presentations (.pptx, .ppt) to PDF.
Integrates our high-fidelity Native Vector Engine and LibreOffice.
"""
import os
import sys
import time
from typing import Dict, Any

try:
    from engines.native_engine import NativeEngine
    from engines.libreoffice_engine import LibreOfficeEngine
except ImportError:
    from file_converters.engines.native_engine import NativeEngine
    from file_converters.engines.libreoffice_engine import LibreOfficeEngine

_native = NativeEngine()
_lo = LibreOfficeEngine()

def ppt_to_pdf(input_ppt: str, output_pdf: str, engine: str = "auto") -> Dict[str, Any]:
    t0 = time.time()
    input_abs = os.path.abspath(input_ppt)
    output_abs = os.path.abspath(output_pdf)

    chosen = engine
    if chosen == "auto":
        ext = os.path.splitext(input_abs)[1].lower()
        if ext == ".ppt" or _lo.is_available():
            chosen = "libreoffice"
        else:
            chosen = "native"

    if chosen == "libreoffice":
        if _lo.is_available():
            res = _lo.convert(input_abs, output_abs)
        else:
            if input_abs.lower().endswith(".ppt"):
                return {
                    "success": False,
                    "error": "Legacy .ppt files require LibreOffice (sudo apt install -y libreoffice-impress-nogui)."
                }
            res = _native.convert(input_abs, output_abs)
    else:
        res = _native.convert(input_abs, output_abs)

    if res.get("success"):
        return {
            "success": True,
            "input": os.path.basename(input_ppt),
            "output": res["output_path"],
            "count": f"{res['slide_count']} slide(s)",
            "size_bytes": res["file_size_bytes"],
            "duration": res["duration_seconds"],
            "engine": res["engine"]
        }
    else:
        return {
            "success": False,
            "error": res.get("error", "PowerPoint conversion failed")
        }
