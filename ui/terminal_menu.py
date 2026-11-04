"""
Terminal user interface components: colors, headers, menus, and spinners.
Complete offline PDF suite + Media & Book Downloaders.
"""
import os
import sys
import time
import threading

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Enable ANSI escape sequences on Windows cmd.exe / PowerShell
if os.name == 'nt':
    os.system('')

BANNER = f"""{CYAN}{BOLD}
╔═══════════════════════════════════════════════════════════════════╗
║         🛠️  FILEFORGE  •  OPENFORGE STUDENT COLLECTIVE             ║
║         High-Performance Offline PDF & Conversion Suite           ║
╚═══════════════════════════════════════════════════════════════════╝{RESET}"""

MENU_CATEGORIES = [
    ("📄 DOCUMENT & OFFICE CONVERTERS", [
        ("1", "🖼️  Photos to PDF", "Combine JPG, PNG, WEBP into a single PDF"),
        ("2", "📄 PDF to Images", "Extract all PDF pages into crisp PNG/JPG"),
        ("3", "📝 Word to PDF", "Convert .docx/.doc to vector PDF (100% exact fidelity)"),
        ("4", "📑 PDF to Word", "Convert PDF to editable Word document (.docx)"),
        ("5", "📊 PowerPoint to PDF", "Convert .pptx/.ppt to PDF (exact boxes, fonts & shapes)"),
        ("6", "📽️ PDF to PowerPoint", "Convert PDF to PowerPoint presentation (.pptx)"),
        ("7", "📈 Excel to PDF", "Convert spreadsheets (.xlsx/.xls) to PDF tables"),
        ("8", "📉 PDF to Excel", "Extract tables & structures into Excel (.xlsx)"),
    ]),
    ("🧰 ADVANCED PDF TOOLKIT", [
        ("9", "🔀 Merge PDFs", "Combine multiple PDF files in your custom order"),
        ("10", "✂️  Split PDF", "Extract custom page ranges (e.g. 1-3, 5) or burst all pages"),
        ("11", "🗜️  Compress / Optimize", "Reduce PDF file size up to 80% while keeping high quality"),
        ("12", "🔄 Rotate PDF", "Rotate pages 90°, 180°, or 270° clockwise"),
        ("13", "🔒 Protect PDF", "Encrypt PDF with secure AES-256 password"),
        ("14", "🔓 Unlock PDF", "Remove password protection from encrypted PDF"),
        ("15", "🔢 Page Numbers / Stamp", "Add 'Page X of Y' numbering or custom watermark"),
    ]),
    ("🌐 WEB & MEDIA DOWNLOADER", [
        ("16", "🎬 Media Downloader", "Download Songs (MP3 320k+Art) or Videos (MP4 with Custom Resolutions)"),
    ]),
]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_menu(extra_categories=None):
    print(BANNER)
    all_categories = list(MENU_CATEGORIES)
    if extra_categories:
        all_categories.extend(extra_categories)

    for category_name, items in all_categories:
        print(f"\n{BOLD}{category_name}:{RESET}")
        for key, title, desc in items:
            key_num = int(key) if key.isdigit() else 99
            if key_num >= 17:
                key_col = GREEN
            elif key_num == 16:
                key_col = MAGENTA
            elif key_num >= 9:
                key_col = BLUE
            else:
                key_col = CYAN
            print(f"  {key_col}[{key:>2}]{RESET} {BOLD}{title:<28}{RESET} {DIM}• {desc}{RESET}")
    print(f"\n  {RED}[ 0]{RESET} {BOLD}{'🚪 Exit':<28}{RESET} {DIM}• Quit the application{RESET}\n")

class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None
        self.chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __enter__(self):
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def _spin(self):
        idx = 0
        while not self.stop_event.is_set():
            c = self.chars[idx % len(self.chars)]
            sys.stdout.write(f"\r{CYAN}{c}{RESET} {self.message} ")
            sys.stdout.flush()
            time.sleep(0.08)
            idx += 1

def print_success_card(result: dict):
    print(f"\n{GREEN}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
    print(f"{GREEN}{BOLD}               ✔ OPERATION SUCCESSFUL!                             {RESET}")
    print(f"{GREEN}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
    print(f"  • {BOLD}Input / Source:{RESET}    {CYAN}{result.get('input', 'N/A')}{RESET}")
    print(f"  • {BOLD}Saved To:{RESET}          {GREEN}{BOLD}{result.get('output', 'N/A')}{RESET}")
    if "count" in result:
        print(f"  • {BOLD}Details:{RESET}           {result['count']}")
    if "size_bytes" in result:
        size_kb = round(result['size_bytes'] / 1024, 1)
        if size_kb > 1024:
            print(f"  • {BOLD}File Size:{RESET}         {round(size_kb / 1024, 2)} MB")
        else:
            print(f"  • {BOLD}File Size:{RESET}         {size_kb} KB")
    if "duration" in result:
        print(f"  • {BOLD}Time Taken:{RESET}        {round(result['duration'], 2)}s")
    if "engine" in result:
        print(f"  • {BOLD}Engine Used:{RESET}       {result['engine'].upper()}")
    print(f"{GREEN}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}\n")

def print_error_card(error_msg: str):
    print(f"\n{RED}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
    print(f"{RED}{BOLD}               ✘ OPERATION FAILED                                  {RESET}")
    print(f"{RED}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}")
    print(f"  {RED}{error_msg}{RESET}")
    print(f"{RED}{BOLD}═══════════════════════════════════════════════════════════════════{RESET}\n")
