"""
Community Plugin: Plain Text & Notes to Clean PDF.
Demonstrates how easy it is to add a new tool to FileForge / OpenForge.
"""
import os
from plugins.base_tool import BaseTool
from ui.dialogs import choose_input_files, choose_save_location
from ui.terminal_menu import print_success_card, print_error_card, CYAN, BOLD, RESET
from utils.helper import open_file_or_dir
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class TextToPdfTool(BaseTool):
    id = "text_to_pdf"
    name = "Text / Code Notes to PDF"
    description = "Convert .txt, .log, or code files into a styled printable PDF"
    category = "✨ COMMUNITY EXTENSIONS"
    icon = "📝"
    author = "@OpenForge"
    version = "1.0.0"
    dependencies = ["reportlab"]

    def run(self) -> None:
        if not self.check_dependencies():
            return

        print(f"\n{CYAN}{BOLD}▶ Text / Code Notes to Clean PDF{RESET}")
        files = choose_input_files(
            title="Select Text / Code File to Convert to PDF",
            file_filters=["*.txt", "*.log", "*.py", "*.java", "*.c", "*.cpp", "*.js", "*.html", "*.md"],
            multiple=False
        )
        if not files:
            print("Operation cancelled. No file selected.")
            return

        input_path = files[0]
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        default_out = os.path.join(os.path.dirname(input_path), f"{base_name}_formatted.pdf")

        save_path = choose_save_location(
            title="Save Formatted PDF As",
            default_filename=os.path.basename(default_out),
            file_types=[("PDF Document", "*.pdf")]
        )
        if not save_path:
            print("Operation cancelled. No save location chosen.")
            return

        try:
            with open(input_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            doc = SimpleDocTemplate(
                save_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=16,
                leading=20,
                textColor=colors.HexColor('#1a365d')
            )
            body_style = ParagraphStyle(
                'CodeBody',
                fontName='Courier',
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#2d3748')
            )

            story = [
                Paragraph(f"<b>Document:</b> {os.path.basename(input_path)}", title_style),
                Spacer(1, 15),
                Preformatted(content, body_style)
            ]

            doc.build(story)

            print_success_card(
                operation="Text to PDF Conversion",
                output_path=save_path,
                details={
                    "Source": os.path.basename(input_path),
                    "Output": os.path.basename(save_path),
                    "File Size": f"{os.path.getsize(save_path)} bytes"
                }
            )

            try:
                ans = input(f"{CYAN}Open PDF now? [y/N]: {RESET}").strip().lower()
                if ans in ("y", "yes"):
                    open_file_or_dir(save_path)
            except (KeyboardInterrupt, EOFError):
                pass

        except Exception as e:
            print_error_card(operation="Text to PDF", error_message=str(e))
