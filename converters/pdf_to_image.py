"""
Convert PDF document pages to PNG or JPEG images.
"""
import os
import time
from typing import Dict, Any
import pymupdf

def pdf_to_images(input_pdf: str, output_path: str, dpi: int = 200, img_format: str = "png") -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"PDF file not found: {input_pdf}"}

    try:
        doc = pymupdf.open(input_pdf)
        page_count = len(doc)
        if page_count == 0:
            return {"success": False, "error": "PDF has no pages"}

        out_abs = os.path.abspath(output_path)
        base_dir = os.path.dirname(out_abs) or "."
        os.makedirs(base_dir, exist_ok=True)

        # If user picked a file like "page.png"
        base_name, ext = os.path.splitext(os.path.basename(out_abs))
        if not ext:
            ext = f".{img_format}"
            out_abs = os.path.join(base_dir, f"{base_name}{ext}")

        created_files = []
        if page_count == 1:
            page = doc[0]
            pix = page.get_pixmap(dpi=dpi)
            pix.save(out_abs)
            created_files.append(out_abs)
        else:
            # Multi-page
            for idx, page in enumerate(doc):
                pix = page.get_pixmap(dpi=dpi)
                page_file = os.path.join(base_dir, f"{base_name}_page_{idx+1}{ext}")
                pix.save(page_file)
                created_files.append(page_file)

        doc.close()
        duration = time.time() - t0
        total_size = sum(os.path.getsize(f) for f in created_files if os.path.exists(f))

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": f"{created_files[0]} (and {len(created_files)-1} more)" if len(created_files) > 1 else created_files[0],
            "count": f"{page_count} image(s) created",
            "size_bytes": total_size,
            "duration": duration,
            "created_files": created_files
        }
    except Exception as e:
        return {"success": False, "error": f"PDF to Image conversion error: {e}"}
