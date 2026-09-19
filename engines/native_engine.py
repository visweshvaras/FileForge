"""
Pure-Python PPTX to PDF Conversion Engine.
High-fidelity vector engine with bulletproof handling of photos, fonts, styles, shapes, and tables.
"""
import html
import io
import os
import time
from typing import Dict, Any, Optional

from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader

from .base import BaseEngine
try:
    from utils.fonts import resolve_font, is_valid_font, init_system_fonts
except ImportError:
    from file_converters.utils.fonts import resolve_font, is_valid_font, init_system_fonts

class NativeEngine(BaseEngine):
    name = "native"
    description = "Pure Python vector engine (zero system dependencies, high photo & style fidelity)"

    def is_available(self) -> bool:
        try:
            import pptx
            import reportlab
            import PIL
            return True
        except ImportError:
            return False

    def convert(
        self,
        input_path: str,
        output_path: str,
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

        ext = os.path.splitext(input_abs)[1].lower()
        if ext == ".ppt":
            return {
                "success": False,
                "engine": self.name,
                "output_path": output_abs,
                "slide_count": 0,
                "duration_seconds": 0.0,
                "file_size_bytes": 0,
                "error": "Legacy .ppt requires LibreOffice (run: sudo apt install -y libreoffice-impress-nogui)."
            }

        try:
            from pptx import Presentation
            from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
            from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

            init_system_fonts()
            prs = Presentation(input_abs)
            slide_w = float(prs.slide_width.pt)
            slide_h = float(prs.slide_height.pt)

            os.makedirs(os.path.dirname(output_abs) or ".", exist_ok=True)
            c = canvas.Canvas(output_abs, pagesize=(slide_w, slide_h))

            try:
                cp = prs.core_properties
                if cp.title:
                    c.setTitle(cp.title)
                if cp.author:
                    c.setAuthor(cp.author)
                if cp.subject:
                    c.setSubject(cp.subject)
            except Exception:
                pass
            c.setCreator("Universal File Converter Pro (Native Engine)")

            def get_color(color_obj, default=None):
                if color_obj is None:
                    return default
                try:
                    if hasattr(color_obj, 'rgb') and color_obj.rgb is not None:
                        rgb = color_obj.rgb
                        return Color(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
                except Exception:
                    pass
                return default

            def get_shape_fill(shape):
                try:
                    fill = shape.fill
                    if fill.type == 1:  # SOLID
                        return get_color(fill.fore_color)
                except Exception:
                    pass
                return None

            def get_shape_line(shape):
                try:
                    line = shape.line
                    if line and line.fill and line.fill.type is not None:
                        width = line.width.pt if line.width else 1.0
                        color = get_color(line.color, Color(0, 0, 0))
                        return width, color
                except Exception:
                    pass
                return None, None

            def extract_blip_bytes(element, slide_part):
                """Find any embedded blip image in element."""
                try:
                    blips = element.xpath('.//*[local-name()="blip"]')
                    for b in blips:
                        rId = b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        if rId:
                            part = slide_part.related_part(rId)
                            if part and part.blob:
                                return part.blob
                except Exception:
                    pass
                return None

            def render_table(shape, offset_x=0, offset_y=0):
                tbl = shape.table
                left = (shape.left.pt if shape.left else 0) + offset_x
                top = (shape.top.pt if shape.top else 0) + offset_y
                w = shape.width.pt if shape.width else 0

                col_widths = [col.width.pt for col in tbl.columns]
                data = []
                style_commands = [
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, Color(0.7, 0.7, 0.7)),
                    ('BOX', (0, 0), (-1, -1), 1.0, Color(0.2, 0.2, 0.2)),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ]

                for row_idx, row in enumerate(tbl.rows):
                    row_data = []
                    for col_idx, cell in enumerate(row.cells):
                        cell_fill = get_shape_fill(cell)
                        if cell_fill:
                            style_commands.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), cell_fill))

                        is_header = (row_idx == 0)
                        escaped_txt = html.escape(cell.text).replace('\x0b', '<br/>').replace('\n', '<br/>')

                        font_name = resolve_font("Helvetica", is_bold=is_header)
                        font_size = 9.5 if is_header else 8.5

                        text_color = '#000000'
                        if cell_fill:
                            lum = cell_fill.red * 0.299 + cell_fill.green * 0.587 + cell_fill.blue * 0.114
                            if lum < 0.5:
                                text_color = '#FFFFFF'

                        p_style = ParagraphStyle(
                            name=f'TCell_{id(shape)}_{row_idx}_{col_idx}',
                            fontName=font_name,
                            fontSize=font_size,
                            leading=font_size * 1.25,
                            textColor=HexColor(text_color)
                        )
                        row_data.append(Paragraph(f'<b>{escaped_txt}</b>' if is_header else escaped_txt, p_style))
                    data.append(row_data)

                t = Table(data, colWidths=col_widths)
                t.setStyle(TableStyle(style_commands))
                t_w, t_h = t.wrap(w, slide_h)
                y = slide_h - top - t_h
                t.drawOn(c, left, y)

            def render_shape(shape, slide_part, offset_x=0, offset_y=0):
                left = (shape.left.pt if shape.left else 0) + offset_x
                top = (shape.top.pt if shape.top else 0) + offset_y
                w = shape.width.pt if shape.width else 0
                h = shape.height.pt if shape.height else 0
                y = slide_h - top - h

                # 1. Group shapes (recursively handle nested children)
                if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                    for sub_shape in shape.shapes:
                        render_shape(sub_shape, slide_part, offset_x=left, offset_y=top)
                    return

                # 2. Tables
                if shape.has_table:
                    render_table(shape, offset_x, offset_y)
                    return

                # 3. Geometric Shape Fills & Borders
                fill_color = get_shape_fill(shape)
                line_w, line_color = get_shape_line(shape)
                do_fill = 1 if fill_color else 0
                do_stroke = 1 if (line_w and line_color) else 0

                if do_fill:
                    c.setFillColor(fill_color)
                if do_stroke:
                    c.setStrokeColor(line_color)
                    c.setLineWidth(line_w)

                if do_fill or do_stroke:
                    shape_type = getattr(shape, 'auto_shape_type', None)
                    if shape_type == MSO_SHAPE.ROUNDED_RECTANGLE:
                        radius = min(w, h) * 0.18
                        c.roundRect(left, y, w, h, radius, fill=do_fill, stroke=do_stroke)
                    elif shape_type == MSO_SHAPE.OVAL:
                        c.ellipse(left, y, left + w, y + h, fill=do_fill, stroke=do_stroke)
                    elif shape_type == MSO_SHAPE.LINE:
                        c.line(left, y + h, left + w, y)
                    else:
                        c.rect(left, y, w, h, fill=do_fill, stroke=do_stroke)

                # 4. Photos / Pictures (Standard or Picture-fill / Blip)
                img_bytes = None
                try:
                    if shape.shape_type == MSO_SHAPE_TYPE.PICTURE or hasattr(shape, 'image'):
                        img_bytes = shape.image.blob
                    else:
                        img_bytes = extract_blip_bytes(shape._element, slide_part)
                except Exception:
                    pass

                if img_bytes:
                    try:
                        img_reader = ImageReader(io.BytesIO(img_bytes))
                        c.drawImage(img_reader, left, y, w, h, mask='auto', preserveAspectRatio=True)
                    except Exception:
                        pass

                # 5. Text Frames
                if shape.has_text_frame and shape.text_frame.text.strip():
                    tf = shape.text_frame
                    pad_x = 4.0
                    pad_y = 2.0
                    box_w = max(10.0, w - pad_x * 2)
                    box_h = max(10.0, h - pad_y * 2)

                    paragraphs_to_draw = []
                    for p in tf.paragraphs:
                        if not p.text.strip():
                            continue

                        align = TA_LEFT
                        if p.alignment == PP_ALIGN.CENTER:
                            align = TA_CENTER
                        elif p.alignment == PP_ALIGN.RIGHT:
                            align = TA_RIGHT
                        elif p.alignment == PP_ALIGN.JUSTIFY:
                            align = TA_JUSTIFY

                        bullet_prefix = ""
                        if p.level and p.level > 0:
                            bullet_prefix = "&nbsp;&nbsp;" * p.level + "• "

                        p_font_name = p.font.name if p.font.name else None
                        base_size = p.font.size.pt if p.font.size else 11.0

                        run_html = []
                        for r in p.runs:
                            txt = r.text
                            if not txt:
                                continue

                            escaped_txt = html.escape(txt).replace('\x0b', '<br/>').replace('\n', '<br/>')

                            r_bold = r.font.bold or (p.font.bold if hasattr(p.font, 'bold') else False)
                            r_italic = r.font.italic or (p.font.italic if hasattr(p.font, 'italic') else False)
                            r_size = r.font.size.pt if r.font.size else base_size

                            r_color = None
                            try:
                                if r.font.color and r.font.color.rgb:
                                    r_color = f'#{r.font.color.rgb}'
                            except Exception:
                                pass
                            if not r_color:
                                try:
                                    if p.font.color and p.font.color.rgb:
                                        r_color = f'#{p.font.color.rgb}'
                                except Exception:
                                    pass

                            if not r_color and fill_color:
                                lum = fill_color.red * 0.299 + fill_color.green * 0.587 + fill_color.blue * 0.114
                                r_color = '#FFFFFF' if lum < 0.5 else '#000000'

                            chunk = escaped_txt
                            if r_bold:
                                chunk = f'<b>{chunk}</b>'
                            if r_italic:
                                chunk = f'<i>{chunk}</i>'
                            if getattr(r.font, 'underline', False):
                                chunk = f'<u>{chunk}</u>'
                            if r_color:
                                chunk = f'<font color="{r_color}">{chunk}</font>'
                            if r_size:
                                chunk = f'<font size="{r_size:.1f}">{chunk}</font>'

                            run_html.append(chunk)

                        full_html = bullet_prefix + "".join(run_html)
                        font_resolved = resolve_font(p_font_name, is_bold=bool(p.font.bold))

                        style = ParagraphStyle(
                            name=f'PStyle_{id(p)}',
                            fontName=font_resolved,
                            fontSize=base_size,
                            leading=base_size * 1.22,
                            alignment=align,
                            textColor=Color(0, 0, 0)
                        )
                        para = Paragraph(full_html, style)
                        paragraphs_to_draw.append(para)

                    if paragraphs_to_draw:
                        total_needed_h = 0
                        measured = []
                        for para in paragraphs_to_draw:
                            p_w, p_h = para.wrap(box_w, 2000)
                            measured.append((para, p_h))
                            total_needed_h += p_h

                        # Auto-fit scale down if overflowing shape
                        if total_needed_h > box_h and box_h > 15:
                            scale_factor = min(1.0, max(0.65, box_h / total_needed_h))
                            if scale_factor < 0.95:
                                total_needed_h = 0
                                new_measured = []
                                for para in paragraphs_to_draw:
                                    para.style.fontSize *= scale_factor
                                    para.style.leading *= scale_factor
                                    p_w, p_h = para.wrap(box_w, 2000)
                                    new_measured.append((para, p_h))
                                    total_needed_h += p_h
                                measured = new_measured

                        # Vertical alignment
                        valign_anchor = getattr(tf, 'vertical_anchor', None)
                        if valign_anchor == MSO_ANCHOR.MIDDLE or (len(paragraphs_to_draw) == 1 and h < 45):
                            start_y = y + (h + total_needed_h) / 2
                        elif valign_anchor == MSO_ANCHOR.BOTTOM:
                            start_y = y + total_needed_h + pad_y
                        else:
                            start_y = y + h - pad_y

                        curr_y = start_y
                        draw_x = left + pad_x
                        for para, p_h in measured:
                            curr_y -= p_h
                            para.drawOn(c, draw_x, curr_y)

            # Process all slides
            slide_count = len(prs.slides)
            for slide in prs.slides:
                bg_drawn = False
                # 1. Slide Background image
                bg_blob = extract_blip_bytes(slide.background._element, slide.part)
                if bg_blob:
                    try:
                        bg_reader = ImageReader(io.BytesIO(bg_blob))
                        c.drawImage(bg_reader, 0, 0, slide_w, slide_h)
                        bg_drawn = True
                    except Exception:
                        pass

                # 2. Solid color background
                if not bg_drawn:
                    try:
                        bg = slide.background
                        if bg and bg.fill and bg.fill.type == 1:
                            bg_col = get_color(bg.fill.fore_color)
                            if bg_col:
                                c.setFillColor(bg_col)
                                c.rect(0, 0, slide_w, slide_h, fill=1, stroke=0)
                                bg_drawn = True
                    except Exception:
                        pass

                if not bg_drawn:
                    c.setFillColor(Color(1, 1, 1))
                    c.rect(0, 0, slide_w, slide_h, fill=1, stroke=0)

                # Render all shapes
                for shape in slide.shapes:
                    try:
                        render_shape(shape, slide.part)
                    except Exception:
                        pass

                c.showPage()

            c.save()

            duration = time.time() - start_time
            file_size = os.path.getsize(output_abs) if os.path.exists(output_abs) else 0

            return {
                "success": True,
                "engine": self.name,
                "output_path": output_abs,
                "slide_count": slide_count,
                "duration_seconds": round(duration, 3),
                "file_size_bytes": file_size,
                "error": None
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
