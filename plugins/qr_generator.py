"""
Community Plugin: Link to QR Code Generator (Image & PDF).
Enables generating high-resolution QR codes in Image or PDF formats.
"""
import os
from plugins.base_tool import BaseTool
from ui.dialogs import choose_save_location
from ui.terminal_menu import (
    print_success_card,
    print_error_card,
    CYAN,
    GREEN,
    YELLOW,
    BOLD,
    DIM,
    RESET
)
from utils.helper import open_file_or_dir
from converters.qr_generator import generate_qr_image, generate_qr_pdf


class QrCodeTool(BaseTool):
    id = "qr_generator"
    name = "Link to QR Code Generator"
    description = "Generate QR codes as Image (PNG/JPG) or printable PDF document"
    category = "✨ COMMUNITY EXTENSIONS"
    icon = "🔳"
    author = "@OpenForge"
    version = "1.0.0"
    dependencies = ["qrcode", "reportlab", "PIL"]

    def run(self) -> None:
        if not self.check_dependencies():
            return

        print(f"\n{CYAN}{BOLD}▶ {self.icon} {self.name}{RESET}")
        print(f"{DIM}Convert any website link, text, or information into a clean QR code.{RESET}\n")

        # 1. Get Link / Data from User
        try:
            data = input(f"{BOLD}🔗 Enter Link or Text to encode: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return

        if not data:
            print(f"\n{YELLOW}⚠️  No link or text entered. Operation cancelled.{RESET}")
            return

        # 2. Select Output Format (Image or PDF)
        print(f"\n{BOLD}Choose QR Code Output Format:{RESET}")
        print(f"  {CYAN}[1]{RESET} 🖼️  Image (PNG / JPG - High Resolution for screens & web)")
        print(f"  {GREEN}[2]{RESET} 📄 PDF Document (Clean, printable page with title & link label)")

        try:
            format_choice = input(f"\n{BOLD}Select format [1-2, default: 1]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return

        is_pdf = format_choice == "2"

        # 3. Choose Save Location via native file picker
        if is_pdf:
            default_name = "qrcode.pdf"
            filters = ["*.pdf"]
            title = "Save QR Code as PDF Document"
        else:
            default_name = "qrcode.png"
            filters = ["*.png", "*.jpg", "*.jpeg"]
            title = "Save QR Code as Image"

        save_path = choose_save_location(
            title=title,
            default_filename=default_name,
            file_filters=filters
        )

        if not save_path:
            print("Operation cancelled. No save location chosen.")
            return

        # 4. Generate the QR Code
        try:
            if is_pdf:
                # Ask optional title for PDF
                pdf_title = "Scan to Open Link" if data.startswith(("http://", "https://")) else "Scan QR Code"
                generate_qr_pdf(
                    data=data,
                    output_path=save_path,
                    title=pdf_title,
                    show_text=True
                )
                fmt_label = "PDF Document"
            else:
                generate_qr_image(
                    data=data,
                    output_path=save_path
                )
                fmt_label = "Image (" + ("JPG" if save_path.lower().endswith((".jpg", ".jpeg")) else "PNG") + ")"

            file_size = f"{os.path.getsize(save_path):,} bytes"

            print_success_card(
                operation="QR Code Generation",
                output_path=save_path,
                details={
                    "Encoded Content": data if len(data) <= 50 else (data[:47] + "..."),
                    "Format": fmt_label,
                    "Saved Location": save_path,
                    "File Size": file_size
                }
            )

            # 5. Prompt to open file
            try:
                ans = input(f"{CYAN}Open output file now? [y/N]: {RESET}").strip().lower()
                if ans in ("y", "yes"):
                    open_file_or_dir(save_path)
            except (KeyboardInterrupt, EOFError):
                pass

        except Exception as e:
            print_error_card(operation="QR Code Generation", error_message=str(e))
