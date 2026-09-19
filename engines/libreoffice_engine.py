"""
LibreOffice / Soffice headless conversion engine.
"""
import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict, Any, Optional

from .base import BaseEngine
from utils.system import find_libreoffice_binary

class LibreOfficeEngine(BaseEngine):
    name = "libreoffice"
    description = "LibreOffice headless converter (high fidelity, supports .pptx and legacy .ppt)"

    def __init__(self, binary_path: Optional[str] = None):
        self.binary_path = binary_path or find_libreoffice_binary()

    def is_available(self) -> bool:
        return self.binary_path is not None and os.path.isfile(self.binary_path) and os.access(self.binary_path, os.X_OK)

    def convert(
        self,
        input_path: str,
        output_path: str,
        timeout: int = 120,
        **kwargs
    ) -> Dict[str, Any]:
        start_time = time.time()
        input_abs = os.path.abspath(input_path)
        output_abs = os.path.abspath(output_path)

        if not os.path.exists(input_abs):
            return {
                "success": False,
                "engine": self.name,
                "output_path": output_abs,
                "slide_count": 0,
                "duration_seconds": 0.0,
                "file_size_bytes": 0,
                "error": f"Input file not found: {input_path}"
            }

        if not self.is_available():
            return {
                "success": False,
                "engine": self.name,
                "output_path": output_abs,
                "slide_count": 0,
                "duration_seconds": 0.0,
                "file_size_bytes": 0,
                "error": "LibreOffice executable (soffice/libreoffice) is not installed or not in PATH."
            }

        out_dir = os.path.dirname(output_abs) or "."
        os.makedirs(out_dir, exist_ok=True)

        # LibreOffice converts to a file named after the input file inside outdir
        with tempfile.TemporaryDirectory(prefix="ppt2pdf_lo_") as temp_out_dir:
            cmd = [
                self.binary_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", temp_out_dir,
                input_abs
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout
                )

                if proc.returncode != 0:
                    return {
                        "success": False,
                        "engine": self.name,
                        "output_path": output_abs,
                        "slide_count": 0,
                        "duration_seconds": time.time() - start_time,
                        "file_size_bytes": 0,
                        "error": f"LibreOffice failed (code {proc.returncode}): {proc.stderr or proc.stdout}"
                    }

                # Find the produced PDF in temp_out_dir
                base_name = os.path.splitext(os.path.basename(input_abs))[0]
                expected_pdf = os.path.join(temp_out_dir, f"{base_name}.pdf")

                if not os.path.exists(expected_pdf):
                    # Check any pdf in temp_out_dir
                    pdfs = [os.path.join(temp_out_dir, f) for f in os.listdir(temp_out_dir) if f.endswith(".pdf")]
                    if pdfs:
                        expected_pdf = pdfs[0]
                    else:
                        return {
                            "success": False,
                            "engine": self.name,
                            "output_path": output_abs,
                            "slide_count": 0,
                            "duration_seconds": time.time() - start_time,
                            "file_size_bytes": 0,
                            "error": "LibreOffice ran successfully but no PDF was output."
                        }

                # Move to desired destination
                shutil.move(expected_pdf, output_abs)

                # Determine page count
                page_count = 0
                try:
                    import pypdf
                    reader = pypdf.PdfReader(output_abs)
                    page_count = len(reader.pages)
                except Exception:
                    pass

                duration = time.time() - start_time
                file_size = os.path.getsize(output_abs) if os.path.exists(output_abs) else 0

                return {
                    "success": True,
                    "engine": self.name,
                    "output_path": output_abs,
                    "slide_count": page_count,
                    "duration_seconds": round(duration, 3),
                    "file_size_bytes": file_size,
                    "error": None
                }

            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "engine": self.name,
                    "output_path": output_abs,
                    "slide_count": 0,
                    "duration_seconds": time.time() - start_time,
                    "file_size_bytes": 0,
                    "error": f"Conversion timed out after {timeout} seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "engine": self.name,
                    "output_path": output_abs,
                    "slide_count": 0,
                    "duration_seconds": time.time() - start_time,
                    "file_size_bytes": 0,
                    "error": str(e)
                }
