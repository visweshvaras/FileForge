"""
Font discovery, registration and mapping for PDF rendering.
Bulletproof fallback to guarantee ReportLab never crashes on missing fonts.
"""
import os
import glob
from typing import Dict, Optional, Set
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_REGISTERED_FONTS: Dict[str, str] = {}
_INITIALIZED = False

# Core standard 14 PDF Type 1 fonts always supported by ReportLab
CORE_PDF_FONTS: Set[str] = {
    'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique',
    'Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic',
    'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',
    'Symbol', 'ZapfDingbats'
}

def init_system_fonts():
    """Scan and register available TTF fonts with ReportLab."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    # Specific high-priority system fonts
    font_candidates = [
        # DejaVu
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", "DejaVuSans-Oblique"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf", "DejaVuSans-BoldOblique"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "DejaVuSerif"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "DejaVuSerif-Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", "DejaVuSerif-Italic"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "DejaVuSansMono"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "DejaVuSansMono-Bold"),
        # Liberation
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "LiberationSans"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "LiberationSans-Bold"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", "LiberationSans-Italic"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf", "LiberationSans-BoldItalic"),
        ("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "LiberationSerif"),
        ("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", "LiberationSerif-Bold"),
        ("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", "LiberationMono"),
        # User Windows fonts if available
        (os.path.expanduser("~/.local/share/fonts/Windows/arial.ttf"), "Arial"),
        (os.path.expanduser("~/.local/share/fonts/Windows/arialbd.ttf"), "Arial-Bold"),
        (os.path.expanduser("~/.local/share/fonts/Windows/ariali.ttf"), "Arial-Italic"),
        (os.path.expanduser("~/.local/share/fonts/Windows/arialbi.ttf"), "Arial-BoldItalic"),
        (os.path.expanduser("~/.local/share/fonts/Windows/calibri.ttf"), "Calibri"),
        (os.path.expanduser("~/.local/share/fonts/Windows/calibrib.ttf"), "Calibri-Bold"),
        (os.path.expanduser("~/.local/share/fonts/Windows/times.ttf"), "TimesNewRoman"),
        (os.path.expanduser("~/.local/share/fonts/Windows/timesbd.ttf"), "TimesNewRoman-Bold"),
    ]

    # Windows native font candidates
    win_dir = os.environ.get("WINDIR", "C:\\Windows")
    win_fonts = os.path.join(win_dir, "Fonts")
    if os.path.isdir(win_fonts):
        font_candidates.extend([
            (os.path.join(win_fonts, "arial.ttf"), "Arial"),
            (os.path.join(win_fonts, "arialbd.ttf"), "Arial-Bold"),
            (os.path.join(win_fonts, "ariali.ttf"), "Arial-Italic"),
            (os.path.join(win_fonts, "arialbi.ttf"), "Arial-BoldItalic"),
            (os.path.join(win_fonts, "calibri.ttf"), "Calibri"),
            (os.path.join(win_fonts, "calibrib.ttf"), "Calibri-Bold"),
            (os.path.join(win_fonts, "calibrii.ttf"), "Calibri-Italic"),
            (os.path.join(win_fonts, "times.ttf"), "TimesNewRoman"),
            (os.path.join(win_fonts, "timesbd.ttf"), "TimesNewRoman-Bold"),
            (os.path.join(win_fonts, "timesi.ttf"), "TimesNewRoman-Italic"),
            (os.path.join(win_fonts, "segoeui.ttf"), "SegoeUI"),
            (os.path.join(win_fonts, "segoeuib.ttf"), "SegoeUI-Bold"),
            (os.path.join(win_fonts, "consola.ttf"), "Consolas"),
            (os.path.join(win_fonts, "consolab.ttf"), "Consolas-Bold"),
        ])

    for path, font_name in font_candidates:
        if os.path.isfile(path) and font_name not in _REGISTERED_FONTS:
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                _REGISTERED_FONTS[font_name.lower()] = font_name
            except Exception:
                pass

    # Register fonts in user and system font directories
    scan_dirs = [
        os.path.expanduser("~/.local/share/fonts"),
        os.path.expanduser("~/Library/Fonts"),
    ]
    if os.path.isdir(win_fonts):
        scan_dirs.append(win_fonts)

    for s_dir in scan_dirs:
        if os.path.isdir(s_dir):
            for font_file in glob.glob(os.path.join(s_dir, "**/*.ttf"), recursive=True):
                bname = os.path.splitext(os.path.basename(font_file))[0]
                if bname.lower() not in _REGISTERED_FONTS:
                    try:
                        pdfmetrics.registerFont(TTFont(bname, font_file))
                        _REGISTERED_FONTS[bname.lower()] = bname
                    except Exception:
                        pass

    _INITIALIZED = True

def get_registered_fonts() -> Dict[str, str]:
    init_system_fonts()
    return dict(_REGISTERED_FONTS)

def is_valid_font(font_name: str) -> bool:
    """Check if font is registered or is one of ReportLab's standard 14."""
    if font_name in CORE_PDF_FONTS:
        return True
    try:
        registered = pdfmetrics.getRegisteredFontNames()
        return font_name in registered
    except Exception:
        return False

def resolve_font(ppt_font_name: Optional[str], is_bold: bool = False, is_italic: bool = False) -> str:
    """
    Resolve requested font to the closest registered vector font.
    GUARANTEE: Will NEVER return a font that causes ReportLab to crash.
    """
    init_system_fonts()
    name = (ppt_font_name or "").lower().strip()

    # Exact registered match lookup
    target_key = f"{name}{'-bold' if is_bold else ''}{'-italic' if is_italic else ''}"
    if target_key in _REGISTERED_FONTS and is_valid_font(_REGISTERED_FONTS[target_key]):
        return _REGISTERED_FONTS[target_key]

    if name in _REGISTERED_FONTS and is_valid_font(_REGISTERED_FONTS[name]):
        if is_bold:
            b_key = f"{name}-bold"
            if b_key in _REGISTERED_FONTS and is_valid_font(_REGISTERED_FONTS[b_key]):
                return _REGISTERED_FONTS[b_key]
        return _REGISTERED_FONTS[name]

    # Serif family
    if any(k in name for k in ['serif', 'times', 'georgia', 'cambria', 'palatino', 'garamond', 'baskerville']):
        if is_bold and 'dejavuserif-bold' in _REGISTERED_FONTS and is_valid_font('DejaVuSerif-Bold'):
            return 'DejaVuSerif-Bold'
        if is_italic and 'dejavuserif-italic' in _REGISTERED_FONTS and is_valid_font('DejaVuSerif-Italic'):
            return 'DejaVuSerif-Italic'
        if 'dejavuserif' in _REGISTERED_FONTS and is_valid_font('DejaVuSerif'):
            return 'DejaVuSerif'
        if is_bold and 'liberationserif-bold' in _REGISTERED_FONTS and is_valid_font('LiberationSerif-Bold'):
            return 'LiberationSerif-Bold'
        if 'liberationserif' in _REGISTERED_FONTS and is_valid_font('LiberationSerif'):
            return 'LiberationSerif'
        
        # Standard Core 14 Serif
        if is_bold and is_italic:
            return 'Times-BoldItalic'
        elif is_bold:
            return 'Times-Bold'
        elif is_italic:
            return 'Times-Italic'
        return 'Times-Roman'

    # Monospace family
    if any(k in name for k in ['mono', 'courier', 'consolas', 'code', 'source code', 'inconsolata', 'fira']):
        if is_bold and 'dejavusansmono-bold' in _REGISTERED_FONTS and is_valid_font('DejaVuSansMono-Bold'):
            return 'DejaVuSansMono-Bold'
        if 'dejavusansmono' in _REGISTERED_FONTS and is_valid_font('DejaVuSansMono'):
            return 'DejaVuSansMono'
        if 'liberationmono' in _REGISTERED_FONTS and is_valid_font('LiberationMono'):
            return 'LiberationMono'
        
        if is_bold and is_italic:
            return 'Courier-BoldOblique'
        elif is_bold:
            return 'Courier-Bold'
        elif is_italic:
            return 'Courier-Oblique'
        return 'Courier'

    # Sans-serif family (Default)
    if is_bold and is_italic:
        if 'arial-bolditalic' in _REGISTERED_FONTS and is_valid_font('Arial-BoldItalic'):
            return 'Arial-BoldItalic'
        if 'dejavusans-boldoblique' in _REGISTERED_FONTS and is_valid_font('DejaVuSans-BoldOblique'):
            return 'DejaVuSans-BoldOblique'
        if 'liberationsans-bolditalic' in _REGISTERED_FONTS and is_valid_font('LiberationSans-BoldItalic'):
            return 'LiberationSans-BoldItalic'
        return 'Helvetica-BoldOblique'

    if is_bold:
        if 'arial-bold' in _REGISTERED_FONTS and is_valid_font('Arial-Bold'):
            return 'Arial-Bold'
        if 'dejavusans-bold' in _REGISTERED_FONTS and is_valid_font('DejaVuSans-Bold'):
            return 'DejaVuSans-Bold'
        if 'liberationsans-bold' in _REGISTERED_FONTS and is_valid_font('LiberationSans-Bold'):
            return 'LiberationSans-Bold'
        return 'Helvetica-Bold'

    if is_italic:
        if 'arial-italic' in _REGISTERED_FONTS and is_valid_font('Arial-Italic'):
            return 'Arial-Italic'
        if 'dejavusans-oblique' in _REGISTERED_FONTS and is_valid_font('DejaVuSans-Oblique'):
            return 'DejaVuSans-Oblique'
        if 'liberationsans-italic' in _REGISTERED_FONTS and is_valid_font('LiberationSans-Italic'):
            return 'LiberationSans-Italic'
        return 'Helvetica-Oblique'

    if 'arial' in _REGISTERED_FONTS and is_valid_font('Arial'):
        return 'Arial'
    if 'dejavusans' in _REGISTERED_FONTS and is_valid_font('DejaVuSans'):
        return 'DejaVuSans'
    if 'liberationsans' in _REGISTERED_FONTS and is_valid_font('LiberationSans'):
        return 'LiberationSans'

    return 'Helvetica'
