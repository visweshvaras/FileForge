"""
Complete offline PDF manipulation tools:
Merge, Split, Compress/Optimize, Rotate, Protect, Unlock, Watermark & Page Numbers.
Powered by PyMuPDF (fitz).
"""
import os
import time
from typing import List, Dict, Any, Optional
import pymupdf

def merge_pdfs(input_pdfs: List[str], output_pdf: str) -> Dict[str, Any]:
    t0 = time.time()
    if not input_pdfs or len(input_pdfs) < 2:
        return {"success": False, "error": "Please provide at least 2 PDF files to merge."}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        merged = pymupdf.open()
        total_pages = 0
        for pdf_path in input_pdfs:
            if not os.path.isfile(pdf_path):
                continue
            doc = pymupdf.open(pdf_path)
            total_pages += len(doc)
            merged.insert_pdf(doc)
            doc.close()

        merged.save(output_pdf)
        merged.close()

        return {
            "success": True,
            "input": f"{len(input_pdfs)} PDF files",
            "output": os.path.abspath(output_pdf),
            "count": f"{total_pages} pages merged",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Merge failed: {e}"}

def parse_page_range(range_str: str, max_pages: int) -> List[int]:
    """Parse string like '1-3, 5, 8-10' into 1-based page numbers."""
    pages = []
    parts = range_str.split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            sub = p.split("-")
            start = int(sub[0].strip())
            end = int(sub[1].strip())
            for i in range(max(1, start), min(max_pages, end) + 1):
                if i not in pages:
                    pages.append(i)
        elif p.isdigit():
            val = int(p)
            if 1 <= val <= max_pages and val not in pages:
                pages.append(val)
    return pages

def split_pdf(input_pdf: str, output_path: str, page_range_str: Optional[str] = None) -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        max_pages = len(doc)

        if page_range_str:
            target_pages = parse_page_range(page_range_str, max_pages)
            if not target_pages:
                return {"success": False, "error": f"Invalid page range: '{page_range_str}'. Document has {max_pages} pages."}

            new_doc = pymupdf.open()
            for p_num in target_pages:
                new_doc.insert_pdf(doc, from_page=p_num-1, to_page=p_num-1)

            new_doc.save(output_path)
            new_doc.close()
            doc.close()

            return {
                "success": True,
                "input": os.path.basename(input_pdf),
                "output": os.path.abspath(output_path),
                "count": f"Extracted {len(target_pages)} pages ({page_range_str})",
                "size_bytes": os.path.getsize(output_path),
                "duration": time.time() - t0
            }
        else:
            # Split all pages into separate PDFs
            base_dir = os.path.dirname(os.path.abspath(output_path)) or "."
            base_name = os.path.splitext(os.path.basename(output_path))[0]
            created = []

            for idx in range(max_pages):
                single_doc = pymupdf.open()
                single_doc.insert_pdf(doc, from_page=idx, to_page=idx)
                single_file = os.path.join(base_dir, f"{base_name}_page_{idx+1}.pdf")
                single_doc.save(single_file)
                single_doc.close()
                created.append(single_file)

            doc.close()
            return {
                "success": True,
                "input": os.path.basename(input_pdf),
                "output": f"{created[0]} (+ {len(created)-1} more)",
                "count": f"Split into {len(created)} individual PDF pages",
                "size_bytes": sum(os.path.getsize(f) for f in created),
                "duration": time.time() - t0
            }

    except Exception as e:
        return {"success": False, "error": f"Split failed: {e}"}

def compress_pdf(input_pdf: str, output_pdf: str) -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}

    orig_size = os.path.getsize(input_pdf)
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        # Deep compression: garbage collection level 4, deflate streams, clean fonts & duplicate objects
        doc.save(
            output_pdf,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True
        )
        doc.close()

        new_size = os.path.getsize(output_pdf)
        ratio = round((1.0 - (new_size / max(1, orig_size))) * 100, 1)
        savings_text = f"{ratio}% saved" if ratio > 0 else "optimized structure"

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": os.path.abspath(output_pdf),
            "count": f"Compressed ({savings_text})",
            "size_bytes": new_size,
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Compress failed: {e}"}

def rotate_pdf(input_pdf: str, output_pdf: str, angle: int = 90) -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        for page in doc:
            page.set_rotation((page.rotation + angle) % 360)

        doc.save(output_pdf)
        doc.close()

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": os.path.abspath(output_pdf),
            "count": f"Rotated all pages {angle}°",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Rotate failed: {e}"}

def protect_pdf(input_pdf: str, output_pdf: str, password: str) -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}
    if not password:
        return {"success": False, "error": "Password cannot be empty"}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        perm = int(
            pymupdf.PDF_PERM_ACCESSIBILITY
            | pymupdf.PDF_PERM_PRINT
            | pymupdf.PDF_PERM_COPY
        )
        doc.save(
            output_pdf,
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw=password,
            user_pw=password,
            permissions=perm
        )
        doc.close()

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": os.path.abspath(output_pdf),
            "count": "AES-256 Encrypted",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Encryption failed: {e}"}

def unlock_pdf(input_pdf: str, output_pdf: str, password: str = "") -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        if doc.is_encrypted:
            authenticated = doc.authenticate(password)
            if not authenticated:
                doc.close()
                return {"success": False, "error": "Incorrect password. Could not decrypt PDF."}

        # Saving without encryption parameters strips encryption
        doc.save(output_pdf)
        doc.close()

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": os.path.abspath(output_pdf),
            "count": "Password Removed",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Decryption failed: {e}"}

def watermark_pdf(
    input_pdf: str,
    output_pdf: str,
    watermark_text: str = "CONFIDENTIAL",
    mode: str = "watermark"  # 'watermark' (diagonal center) or 'page_numbers' (bottom center)
) -> Dict[str, Any]:
    t0 = time.time()
    if not os.path.isfile(input_pdf):
        return {"success": False, "error": f"File not found: {input_pdf}"}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_pdf)
        total = len(doc)

        for idx, page in enumerate(doc):
            w = page.rect.width
            h = page.rect.height

            if mode == "page_numbers":
                num_text = f"Page {idx+1} of {total}"
                fontsize = 10
                tl = pymupdf.get_text_length(num_text, fontname="helv", fontsize=fontsize)
                point = pymupdf.Point(w / 2 - tl / 2, h - 25)
                page.insert_text(point, num_text, fontname="helv", fontsize=fontsize, color=(0.4, 0.4, 0.4))
            else:
                # Diagonal watermark across center (-45 degrees)
                fontsize = 48
                tl = pymupdf.get_text_length(watermark_text, fontname="helv", fontsize=fontsize)
                center = pymupdf.Point(w / 2, h / 2)
                origin = pymupdf.Point(w / 2 - tl / 2, h / 2)
                matrix = pymupdf.Matrix(-45)
                page.insert_text(
                    origin,
                    watermark_text,
                    fontname="helv",
                    fontsize=fontsize,
                    color=(0.75, 0.75, 0.75),
                    morph=(center, matrix)
                )

        doc.save(output_pdf)
        doc.close()

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": os.path.abspath(output_pdf),
            "count": f"Applied to {total} pages",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": time.time() - t0
        }
    except Exception as e:
        return {"success": False, "error": f"Watermark failed: {e}"}
