"""
Convert PDF document to editable Word document (.docx).
Uses pdf2docx for accurate layout, fonts, and table preservation.
"""
import os
import time
from typing import Dict, Any

def pdf_to_word(input_pdf: str, output_docx: str) -> Dict[str, Any]:
    t0 = time.time()
    input_abs = os.path.abspath(input_pdf)
    output_abs = os.path.abspath(output_docx)

    if not os.path.isfile(input_abs):
        return {"success": False, "error": f"PDF file not found: {input_pdf}"}

    os.makedirs(os.path.dirname(output_abs) or ".", exist_ok=True)

    try:
        from pdf2docx import Converter
        cv = Converter(input_abs)
        cv.convert(output_abs, start=0, end=None)
        cv.close()

        import docx
        doc = docx.Document(output_abs)
        p_count = len(doc.paragraphs)

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": output_abs,
            "count": f"{p_count} paragraph(s)",
            "size_bytes": os.path.getsize(output_abs),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"PDF to Word conversion error: {e}"}
