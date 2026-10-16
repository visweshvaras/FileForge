"""
QR Code Generator: Converts links or text into high-resolution Images (PNG/JPG) or printable PDFs.
"""
import os
import io
import html
from typing import Optional
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_qr_image(
    data: str,
    output_path: str,
    format: str = "PNG",
    box_size: int = 12,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white"
) -> str:
    """
    Generate a high-resolution QR code image.

    Args:
        data: The URL, link, or text to encode.
        output_path: Target image file path.
        format: Image format (PNG, JPEG, etc.).
        box_size: Pixel size of each QR box.
        border: Thickness of border in boxes.
        fill_color: Color of the QR modules.
        back_color: Background color.

    Returns:
        Absolute path to the saved image file.
    """
    if not data or not data.strip():
        raise ValueError("Cannot generate QR code: Data string is empty.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(data.strip())
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # If saving as JPG, convert RGBA to RGB
    if output_path.lower().endswith((".jpg", ".jpeg")):
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_path, format="JPEG", quality=95)
    else:
        img.save(output_path, format=format)

    return os.path.abspath(output_path)


def generate_qr_pdf(
    data: str,
    output_path: str,
    title: Optional[str] = "Scan QR Code",
    show_text: bool = True,
    box_size: int = 10,
    border: int = 4
) -> str:
    """
    Generate a print-ready vector PDF document containing the QR code and link caption.

    Args:
        data: The URL, link, or text to encode.
        output_path: Target PDF file path.
        title: Header title printed above the QR code.
        show_text: Whether to print the URL / text caption below the QR code.
        box_size: Size of QR modules in buffer.
        border: Border margin in boxes.

    Returns:
        Absolute path to the saved PDF file.
    """
    if not data or not data.strip():
        raise ValueError("Cannot generate QR code: Data string is empty.")

    clean_data = data.strip()

    # Generate QR image into memory buffer
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(clean_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Build PDF with ReportLab
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'QRTitle',
        parent=styles['Heading1'],
        alignment=1,  # Center
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1a365d')
    )

    caption_style = ParagraphStyle(
        'QRCaption',
        parent=styles['Normal'],
        alignment=1,  # Center
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4a5568'),
        wordWrap='CJK'
    )

    story = [
        Spacer(1, 40)
    ]

    if title:
        safe_title = html.escape(title)
        story.append(Paragraph(f"<b>{safe_title}</b>", title_style))
        story.append(Spacer(1, 25))

    # Center QR Code image (280x280 pt)
    qr_display_size = 280
    story.append(RLImage(img_buffer, width=qr_display_size, height=qr_display_size))

    if show_text:
        story.append(Spacer(1, 25))
        safe_text = html.escape(clean_data)
        story.append(Paragraph(safe_text, caption_style))

    doc.build(story)
    return os.path.abspath(output_path)
