"""
Convert Word documents (.docx, .doc) to PDF with full fidelity.
Supports inline photos, math equations, tables with shading, headings, and styles.
"""
import html
import io
import os
import shutil
import subprocess
import time
from typing import Dict, Any, List

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import Color, HexColor

try:
    from utils.system import find_libreoffice_binary
    from utils.fonts import resolve_font, init_system_fonts
except ImportError:
    from file_converters.utils.system import find_libreoffice_binary
    from file_converters.utils.fonts import resolve_font, init_system_fonts

def clean_hex_color(hex_str: str) -> str:
    if not hex_str or hex_str.lower() in ("auto", "none"):
        return None
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 6:
        try:
            int(hex_clean, 16)
            return f"#{hex_clean}"
        except ValueError:
            pass
    return None

def extract_math_text(element) -> str:
    """Extract readable text from Office Math ML (<m:oMath>)."""
    math_nodes = element.xpath('.//*[local-name()="oMath"]')
    if not math_nodes:
        return ""
    extracted = []
    for m in math_nodes:
        txts = m.xpath('.//*[local-name()="t"]')
        s = "".join([t.text for t in txts if t.text])
        if s:
            extracted.append(s)
    return " ".join(extracted)

def word_to_pdf(input_docx: str, output_pdf: str) -> Dict[str, Any]:
    t0 = time.time()
    input_abs = os.path.abspath(input_docx)
    output_abs = os.path.abspath(output_pdf)

    if not os.path.isfile(input_abs):
        return {"success": False, "error": f"File not found: {input_docx}"}

    os.makedirs(os.path.dirname(output_abs) or ".", exist_ok=True)
    lo_bin = find_libreoffice_binary()

    # 1. Try LibreOffice if installed
    if lo_bin:
        try:
            import tempfile
            with tempfile.TemporaryDirectory(prefix="word2pdf_") as temp_dir:
                cmd = [lo_bin, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_abs]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
                if res.returncode == 0:
                    base = os.path.splitext(os.path.basename(input_abs))[0]
                    cand = os.path.join(temp_dir, f"{base}.pdf")
                    if os.path.exists(cand):
                        shutil.move(cand, output_abs)
                        import pypdf
                        p_count = len(pypdf.PdfReader(output_abs).pages)
                        return {
                            "success": True,
                            "input": os.path.basename(input_docx),
                            "output": output_abs,
                            "count": f"{p_count} page(s)",
                            "size_bytes": os.path.getsize(output_abs),
                            "duration": time.time() - t0,
                            "engine": "libreoffice"
                        }
        except Exception:
            pass

    # 2. Pure Python Vector Engine
    ext = os.path.splitext(input_abs)[1].lower()
    if ext == ".doc":
        return {
            "success": False,
            "error": "Legacy .doc format requires LibreOffice. Run: sudo apt install -y libreoffice-writer-nogui"
        }

    try:
        import docx
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.table import CT_Tbl
        from docx.text.paragraph import Paragraph as DocxParagraph
        from docx.table import Table as DocxTable
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        init_system_fonts()
        doc = docx.Document(input_abs)

        page_w, page_h = letter
        margin = 54.0  # 0.75 inch margins
        printable_w = page_w - (margin * 2)  # 504 pt
        printable_h = page_h - (margin * 2)

        pdf_doc = SimpleDocTemplate(
            output_abs,
            pagesize=letter,
            leftMargin=margin,
            rightMargin=margin,
            topMargin=margin,
            bottomMargin=margin
        )

        story = []

        def get_image_part(rId):
            try:
                if hasattr(doc.part, 'related_parts') and rId in doc.part.related_parts:
                    return doc.part.related_parts[rId]
                if hasattr(doc.part, 'rels') and rId in doc.part.rels:
                    return doc.part.rels[rId].target_part
            except Exception:
                pass
            return None

        # Iterate through document body elements in SEQUENTIAL order
        for child in doc.element.body:
            # 1. Paragraph element
            if isinstance(child, CT_P):
                p = DocxParagraph(child, doc)
                raw_text = p.text.strip()
                math_text = extract_math_text(p._element)

                # Check for inline/anchored pictures in paragraph
                blips = p._element.xpath('.//*[local-name()="blip"]')
                for b in blips:
                    rId = b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if rId:
                        part = get_image_part(rId)
                        if part and part.blob:
                            try:
                                pil_img = PILImage.open(io.BytesIO(part.blob))
                                img_w, img_h = pil_img.size
                                # Scale to fit printable page width while preserving aspect ratio
                                max_img_w = min(printable_w, 480.0)
                                max_img_h = min(printable_h * 0.6, 420.0)
                                scale = min(max_img_w / img_w, max_img_h / img_h, 1.0)
                                target_w = img_w * scale
                                target_h = img_h * scale

                                img_flowable = RLImage(io.BytesIO(part.blob), width=target_w, height=target_h)
                                story.append(img_flowable)
                                story.append(Spacer(1, 6))
                            except Exception:
                                pass

                # If no text and no math, add spacer if empty paragraph
                if not raw_text and not math_text:
                    if not blips:
                        story.append(Spacer(1, 4))
                    continue

                # Paragraph Alignment
                align = TA_LEFT
                if p.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                    align = TA_CENTER
                elif p.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                    align = TA_RIGHT
                elif p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                    align = TA_JUSTIFY

                # Styling hierarchy
                style_name = (p.style.name if p.style else "").lower()
                font_size = 10.5
                leading = 14.0
                is_heading = False
                is_bold_para = False
                p_color = HexColor("#0F172A")

                if "title" in style_name:
                    font_size = 22.0
                    leading = 26.0
                    is_heading = True
                    p_color = HexColor("#1E3A8A")
                elif "subtitle" in style_name:
                    font_size = 13.0
                    leading = 16.0
                    is_heading = True
                    p_color = HexColor("#475569")
                elif "heading 1" in style_name:
                    font_size = 16.0
                    leading = 20.0
                    is_heading = True
                    p_color = HexColor("#1E40AF")
                elif "heading 2" in style_name:
                    font_size = 13.5
                    leading = 17.0
                    is_heading = True
                    p_color = HexColor("#1E3A8A")
                elif "heading 3" in style_name:
                    font_size = 12.0
                    leading = 15.0
                    is_heading = True
                    p_color = HexColor("#334155")
                elif "heading" in style_name:
                    font_size = 11.5
                    leading = 14.5
                    is_heading = True
                elif "list" in style_name or "bullet" in style_name:
                    font_size = 10.5
                    leading = 13.5

                # Build HTML content from runs
                run_html = []
                for r in p.runs:
                    txt = r.text
                    if not txt:
                        continue

                    # Safe HTML entity escaping
                    escaped_txt = html.escape(txt).replace('\n', '<br/>')

                    r_bold = r.bold or is_heading
                    r_italic = r.italic
                    r_underline = r.underline
                    r_strike = getattr(r.font, 'strike', False)
                    r_super = getattr(r.font, 'superscript', False)
                    r_sub = getattr(r.font, 'subscript', False)

                    part = escaped_txt
                    if r_bold:
                        part = f"<b>{part}</b>"
                    if r_italic:
                        part = f"<i>{part}</i>"
                    if r_underline:
                        part = f"<u>{part}</u>"
                    if r_strike:
                        part = f"<s>{part}</s>"
                    if r_super:
                        part = f"<sup>{part}</sup>"
                    if r_sub:
                        part = f"<sub>{part}</sub>"

                    # Colors
                    r_color = None
                    try:
                        if r.font.color and r.font.color.rgb:
                            r_color = f"#{r.font.color.rgb}"
                    except Exception:
                        pass

                    if r_color:
                        part = f'<font color="{r_color}">{part}</font>'

                    run_html.append(part)

                # Append math text if present
                if math_text:
                    escaped_math = html.escape(math_text)
                    run_html.append(f'<font color="#0369A1" face="Courier"><b>{escaped_math}</b></font>')

                bullet_prefix = ""
                if "bullet" in style_name or "list" in style_name:
                    bullet_prefix = "• &nbsp;"

                full_p_html = bullet_prefix + "".join(run_html)
                if not full_p_html.strip():
                    continue

                font_family = resolve_font(
                    p.style.font.name if (p.style and p.style.font and p.style.font.name) else "Helvetica",
                    is_bold=is_heading
                )

                p_style = ParagraphStyle(
                    name=f"PStyle_{id(p)}",
                    fontName=font_family,
                    fontSize=font_size,
                    leading=leading,
                    alignment=align,
                    textColor=p_color
                )
                story.append(Paragraph(full_p_html, p_style))
                story.append(Spacer(1, 4 if is_heading else 3))

            # 2. Table element
            elif isinstance(child, CT_Tbl):
                tbl = DocxTable(child, doc)
                if not tbl.rows:
                    continue

                num_cols = len(tbl.columns) if tbl.columns else 1
                col_width = printable_w / max(1, num_cols)

                table_data = []
                style_commands = [
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
                    ('BOX', (0, 0), (-1, -1), 1.0, HexColor("#64748B")),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]

                for r_idx, row in enumerate(tbl.rows):
                    row_data = []
                    is_header_row = (r_idx == 0)

                    for c_idx, cell in enumerate(row.cells):
                        # Extract cell background shading
                        shd_nodes = cell._tc.xpath('.//*[local-name()="shd"]/@*[local-name()="fill"]')
                        cell_bg = None
                        if shd_nodes:
                            cell_bg = clean_hex_color(shd_nodes[0])

                        if cell_bg:
                            try:
                                style_commands.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), HexColor(cell_bg)))
                            except Exception:
                                pass
                        elif is_header_row:
                            style_commands.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), HexColor("#F1F5F9")))

                        # Cell text and math
                        cell_text = cell.text.strip()
                        cell_math = extract_math_text(cell._tc)
                        escaped_cell = html.escape(cell_text).replace('\n', '<br/>')
                        if cell_math:
                            escaped_cell += f'<br/><font color="#0369A1" face="Courier">{html.escape(cell_math)}</font>'

                        # Check if cell has images
                        cell_blips = cell._tc.xpath('.//*[local-name()="blip"]')
                        for cb in cell_blips:
                            c_rId = cb.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            c_part = get_image_part(c_rId)
                            if c_part and c_part.blob:
                                try:
                                    c_pil = PILImage.open(io.BytesIO(c_part.blob))
                                    w_scale = min(col_width - 8, 120.0) / c_pil.size[0]
                                    target_w = c_pil.size[0] * w_scale
                                    target_h = c_pil.size[1] * w_scale
                                    # RLImage inside table cell
                                    cell_img = RLImage(io.BytesIO(c_part.blob), width=target_w, height=target_h)
                                    row_data.append(cell_img)
                                    continue
                                except Exception:
                                    pass

                        font_family = resolve_font("Helvetica", is_bold=is_header_row)
                        cell_style = ParagraphStyle(
                            name=f"TCell_{id(cell)}",
                            fontName=font_family,
                            fontSize=8.5 if is_header_row else 8.0,
                            leading=10.5,
                            textColor=HexColor("#0F172A")
                        )
                        p_cell = Paragraph(f"<b>{escaped_cell}</b>" if is_header_row else escaped_cell, cell_style)
                        row_data.append(p_cell)

                    table_data.append(row_data)

                if table_data:
                    # Determine column widths
                    actual_cols = max(len(r) for r in table_data)
                    col_widths = [printable_w / actual_cols] * actual_cols

                    t = Table(table_data, colWidths=col_widths, splitByRow=1)
                    t.setStyle(TableStyle(style_commands))
                    story.append(t)
                    story.append(Spacer(1, 8))

        if not story:
            return {"success": False, "error": "Word document is empty or could not be parsed"}

        pdf_doc.build(story)
        import pypdf
        p_count = len(pypdf.PdfReader(output_abs).pages)

        return {
            "success": True,
            "input": os.path.basename(input_docx),
            "output": output_abs,
            "count": f"{p_count} page(s)",
            "size_bytes": os.path.getsize(output_abs),
            "duration": time.time() - t0,
            "engine": "native-python-pro"
        }

    except Exception as e:
        return {"success": False, "error": f"Word to PDF conversion error: {e}"}
