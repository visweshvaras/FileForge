#!/usr/bin/env python3
"""
Universal File Converter & Media Suite - Interactive Terminal Application.
"""
import os
import sys

# Ensure project modules are importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from ui.terminal_menu import (
    clear_screen,
    display_menu,
    Spinner,
    print_success_card,
    print_error_card,
    CYAN,
    GREEN,
    YELLOW,
    MAGENTA,
    BLUE,
    BOLD,
    DIM,
    RESET
)
from ui.dialogs import choose_input_files, choose_save_location, choose_directory
from utils.helper import open_file_or_dir
from plugins import registry
from converters import (
    images_to_pdf,
    pdf_to_images,
    word_to_pdf,
    pdf_to_word,
    ppt_to_pdf,
    pdf_to_ppt,
    excel_to_pdf,
    pdf_to_excel,
    download_media,
    get_media_info,
    get_available_resolutions,
    merge_pdfs,
    split_pdf,
    compress_pdf,
    rotate_pdf,
    protect_pdf,
    unlock_pdf,
    watermark_pdf
)

def run_photo_to_pdf():
    print(f"\n{CYAN}{BOLD}▶ Converting Photos / Images to Combined PDF{RESET}")
    files = choose_input_files(
        title="Select Images to Combine into PDF (Hold Ctrl/Shift for multiple)",
        file_filters=["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.tiff"],
        multiple=True
    )
    if not files:
        print(f"{YELLOW}No images selected. Returning to menu.{RESET}")
        return

    print(f"Selected {len(files)} image(s):")
    for f in files[:5]:
        print(f"  • {os.path.basename(f)}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")

    default_name = f"combined_{os.path.splitext(os.path.basename(files[0]))[0]}.pdf"
    save_path = choose_save_location(
        title="Choose where to save your combined PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Combining images into PDF..."):
        res = images_to_pdf(files, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_pdf_to_images():
    print(f"\n{CYAN}{BOLD}▶ Converting PDF to Images{RESET}")
    files = choose_input_files(
        title="Select PDF File to Extract Images From",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_pdf = files[0]
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]
    default_name = f"{base_name}.png"

    save_path = choose_save_location(
        title="Choose filename prefix or destination for images",
        default_filename=default_name,
        file_filters=["*.png", "*.jpg"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Extracting PDF pages into high-res images..."):
        res = pdf_to_images(input_pdf, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(os.path.dirname(save_path))
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_word_to_pdf():
    print(f"\n{CYAN}{BOLD}▶ Converting Word Document to PDF (Full Fidelity with Photos & Styles){RESET}")
    files = choose_input_files(
        title="Select Word Document (.docx / .doc)",
        file_filters=["*.docx", "*.doc"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.pdf"

    save_path = choose_save_location(
        title="Choose where to save your PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Converting '{os.path.basename(input_file)}' (extracting photos & tables)..."):
        res = word_to_pdf(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_pdf_to_word():
    print(f"\n{CYAN}{BOLD}▶ Converting PDF to Word Document (.docx){RESET}")
    files = choose_input_files(
        title="Select PDF Document to Convert to Word",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.docx"

    save_path = choose_save_location(
        title="Choose where to save your Word document",
        default_filename=default_name,
        file_filters=["*.docx"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Reconstructing layout & tables into Word docx..."):
        res = pdf_to_word(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_ppt_to_pdf():
    print(f"\n{CYAN}{BOLD}▶ Converting PowerPoint to PDF (Vector Shapes, Fonts & Photos){RESET}")
    files = choose_input_files(
        title="Select PowerPoint Presentation (.pptx / .ppt)",
        file_filters=["*.pptx", "*.ppt"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.pdf"

    save_path = choose_save_location(
        title="Choose where to save your PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Rendering vector presentation into PDF..."):
        res = ppt_to_pdf(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_pdf_to_ppt():
    print(f"\n{CYAN}{BOLD}▶ Converting PDF to PowerPoint (.pptx){RESET}")
    files = choose_input_files(
        title="Select PDF File to Convert to PowerPoint Slides",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.pptx"

    save_path = choose_save_location(
        title="Choose where to save your PowerPoint presentation",
        default_filename=default_name,
        file_filters=["*.pptx"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Creating PowerPoint slides from PDF pages..."):
        res = pdf_to_ppt(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_excel_to_pdf():
    print(f"\n{CYAN}{BOLD}▶ Converting Excel Spreadsheet to PDF{RESET}")
    files = choose_input_files(
        title="Select Excel Spreadsheet (.xlsx / .xls)",
        file_filters=["*.xlsx", "*.xls"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.pdf"

    save_path = choose_save_location(
        title="Choose where to save your PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Formatting spreadsheet tables into PDF..."):
        res = excel_to_pdf(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_pdf_to_excel():
    print(f"\n{CYAN}{BOLD}▶ Converting PDF to Excel (.xlsx){RESET}")
    files = choose_input_files(
        title="Select PDF File to Extract Tables to Excel",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}.xlsx"

    save_path = choose_save_location(
        title="Choose where to save your Excel workbook",
        default_filename=default_name,
        file_filters=["*.xlsx"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Extracting tables and structures into Excel workbook..."):
        res = pdf_to_excel(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_merge_pdf():
    print(f"\n{BLUE}{BOLD}▶ Merge Multiple PDFs into One{RESET}")
    files = choose_input_files(
        title="Select 2 or more PDFs to merge (Ctrl/Shift for multiple)",
        file_filters=["*.pdf"],
        multiple=True
    )
    if not files or len(files) < 2:
        print(f"{YELLOW}At least 2 PDF files are required to merge. Returning to menu.{RESET}")
        return

    print(f"Selected {len(files)} PDFs in order:")
    for idx, f in enumerate(files, 1):
        print(f"  {idx}. {os.path.basename(f)}")

    default_name = f"merged_{os.path.splitext(os.path.basename(files[0]))[0]}.pdf"
    save_path = choose_save_location(
        title="Choose where to save the merged PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Merging {len(files)} PDFs..."):
        res = merge_pdfs(files, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_split_pdf():
    print(f"\n{BLUE}{BOLD}▶ Split PDF / Extract Pages{RESET}")
    files = choose_input_files(
        title="Select PDF File to Split",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    print(f"\n{BOLD}Choose Split Mode:{RESET}")
    print(f"  {CYAN}[1]{RESET} Extract custom page range (e.g. '1-3', '1, 3, 5-8')")
    print(f"  {CYAN}[2]{RESET} Burst all pages into separate individual PDFs")

    mode_choice = input(f"\n{BOLD}Select mode [1/2, default: 1]: {RESET}").strip()
    if mode_choice == "2":
        save_path = choose_save_location(
            title="Choose destination or base name for split pages",
            default_filename=f"{base_name}.pdf",
            file_filters=["*.pdf"]
        )
        if not save_path:
            print(f"{YELLOW}Save location cancelled.{RESET}")
            return
        with Spinner("Splitting all pages..."):
            res = split_pdf(input_file, save_path, page_range_str=None)
        if res.get("success"):
            print_success_card(res)
            prompt_open(os.path.dirname(save_path))
        else:
            print_error_card(res.get("error", "Unknown error"))
    else:
        page_range = input(f"{BOLD}Enter page range (e.g. 1-3 or 1, 3, 5): {RESET}").strip()
        if not page_range:
            print(f"{YELLOW}No page range specified. Returning to menu.{RESET}")
            return
        save_path = choose_save_location(
            title="Choose where to save extracted pages",
            default_filename=f"{base_name}_pages_{page_range.replace(' ', '').replace(',', '_')}.pdf",
            file_filters=["*.pdf"]
        )
        if not save_path:
            print(f"{YELLOW}Save location cancelled.{RESET}")
            return
        with Spinner(f"Extracting pages {page_range}..."):
            res = split_pdf(input_file, save_path, page_range_str=page_range)
        if res.get("success"):
            print_success_card(res)
            prompt_open(save_path)
        else:
            print_error_card(res.get("error", "Unknown error"))

def run_compress_pdf():
    print(f"\n{BLUE}{BOLD}▶ Compress / Optimize PDF{RESET}")
    files = choose_input_files(
        title="Select PDF File to Compress",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    default_name = f"{base_name}_compressed.pdf"

    save_path = choose_save_location(
        title="Choose where to save compressed PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Compressing fonts, images & stream objects..."):
        res = compress_pdf(input_file, save_path)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_rotate_pdf():
    print(f"\n{BLUE}{BOLD}▶ Rotate PDF Pages{RESET}")
    files = choose_input_files(
        title="Select PDF File to Rotate",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    print(f"\n{BOLD}Select rotation angle:{RESET}")
    print(f"  {CYAN}[1]{RESET} 90° clockwise")
    print(f"  {CYAN}[2]{RESET} 180° flip")
    print(f"  {CYAN}[3]{RESET} 270° clockwise (90° counter-clockwise)")

    angle_in = input(f"\n{BOLD}Choose angle [1-3, default: 1]: {RESET}").strip()
    angle_map = {"1": 90, "2": 180, "3": 270}
    angle = angle_map.get(angle_in, 90)

    save_path = choose_save_location(
        title="Choose where to save rotated PDF",
        default_filename=f"{base_name}_rotated.pdf",
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner(f"Rotating pages by {angle}°..."):
        res = rotate_pdf(input_file, save_path, angle=angle)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_protect_pdf():
    print(f"\n{BLUE}{BOLD}▶ Protect PDF with AES-256 Encryption{RESET}")
    files = choose_input_files(
        title="Select PDF File to Encrypt",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    password = input(f"{BOLD}🔑 Enter password to encrypt PDF: {RESET}").strip()
    if not password:
        print(f"{YELLOW}Password cannot be empty. Returning to menu.{RESET}")
        return

    save_path = choose_save_location(
        title="Choose where to save protected PDF",
        default_filename=f"{base_name}_protected.pdf",
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Encrypting PDF with AES-256..."):
        res = protect_pdf(input_file, save_path, password=password)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_unlock_pdf():
    print(f"\n{BLUE}{BOLD}▶ Unlock / Remove Password from Encrypted PDF{RESET}")
    files = choose_input_files(
        title="Select Encrypted PDF File to Unlock",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    password = input(f"{BOLD}🔓 Enter PDF password (leave blank if none): {RESET}").strip()

    save_path = choose_save_location(
        title="Choose where to save unlocked PDF",
        default_filename=f"{base_name}_unlocked.pdf",
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Decrypting and stripping restrictions..."):
        res = unlock_pdf(input_file, save_path, password=password)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_watermark_pdf():
    print(f"\n{BLUE}{BOLD}▶ Add Page Numbers or Watermark Stamp{RESET}")
    files = choose_input_files(
        title="Select PDF File to Stamp / Number",
        file_filters=["*.pdf"],
        multiple=False
    )
    if not files:
        print(f"{YELLOW}No file selected. Returning to menu.{RESET}")
        return

    input_file = files[0]
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    print(f"\n{BOLD}Choose Stamp Type:{RESET}")
    print(f"  {CYAN}[1]{RESET} 🔢 Add Page Numbers ('Page X of Y' centered at footer)")
    print(f"  {CYAN}[2]{RESET} 🏷️  Add Diagonal Watermark (e.g. 'CONFIDENTIAL', 'DRAFT')")

    stamp_choice = input(f"\n{BOLD}Select stamp type [1/2, default: 1]: {RESET}").strip()
    if stamp_choice == "2":
        wm_text = input(f"{BOLD}Enter watermark text [default: CONFIDENTIAL]: {RESET}").strip()
        if not wm_text:
            wm_text = "CONFIDENTIAL"
        mode = "watermark"
        default_name = f"{base_name}_watermarked.pdf"
    else:
        wm_text = ""
        mode = "page_numbers"
        default_name = f"{base_name}_numbered.pdf"

    save_path = choose_save_location(
        title="Choose where to save stamped PDF",
        default_filename=default_name,
        file_filters=["*.pdf"]
    )
    if not save_path:
        print(f"{YELLOW}Save location cancelled.{RESET}")
        return

    with Spinner("Applying watermark / page stamps..."):
        res = watermark_pdf(input_file, save_path, watermark_text=wm_text, mode=mode)

    if res.get("success"):
        print_success_card(res)
        prompt_open(save_path)
    else:
        print_error_card(res.get("error", "Unknown error"))

def run_media_downloader():
    print(f"\n{MAGENTA}{BOLD}▶ Media & Song Downloader (yt-dlp + ffmpeg){RESET}")
    url = input(f"{BOLD}🔗 Enter Video / Song link or URL: {RESET}").strip()
    if not url:
        print(f"{YELLOW}No URL entered. Returning to menu.{RESET}")
        return

    # Fetch title & metadata
    print(f"{DIM}Fetching media information...{RESET}")
    info = get_media_info(url)
    if info:
        print(f"{CYAN}Title:{RESET} {BOLD}{info['title']}{RESET} ({info.get('uploader', 'Unknown')})")

    # Format selection
    print(f"\n{BOLD}Choose download type:{RESET}")
    print(f"  {CYAN}[1]{RESET} 🎵 Song / Audio (MP3 - Best Quality 320kbps + Album Thumbnail)")
    print(f"  {CYAN}[2]{RESET} 📹 Video (MP4 - Select Custom Resolution: 4K, 1440p, 1080p, 720p, etc.)")
    print(f"  {CYAN}[3]{RESET} 🎶 Original Audio stream (M4A/FLAC/OPUS)")
    
    fmt_choice = input(f"\n{BOLD}Select type [1-3, default: 1]: {RESET}").strip()
    
    chosen_res = None
    if fmt_choice == "2":
        mode = "video"
        with Spinner("Detecting available resolutions for this video..."):
            resolutions = get_available_resolutions(url)
        
        if resolutions:
            print(f"\n{BOLD}Available resolutions for this video:{RESET}")
            print(f"  {CYAN}[ 1]{RESET} 🌟 Best Available (Auto-detect highest quality)")
            for idx, r in enumerate(resolutions, start=2):
                fps_info = f" @ {r['fps']}fps" if r['fps'] > 30 else ""
                print(f"  {CYAN}[{idx:>2}]{RESET} {r['label']}{fps_info}")
            
            res_in = input(f"\n{BOLD}Select resolution [1-{len(resolutions)+1}, default: 1]: {RESET}").strip()
            try:
                sel_idx = int(res_in)
                if sel_idx <= 1 or sel_idx > len(resolutions) + 1:
                    chosen_res = None  # Best Available
                else:
                    chosen_res = resolutions[sel_idx - 2]["height"]
            except ValueError:
                chosen_res = None
        else:
            print(f"\n{BOLD}Choose Resolution Target:{RESET}")
            print(f"  {CYAN}[1]{RESET} 🌟 Best Available (Highest Quality 4K / 1080p)")
            print(f"  {CYAN}[2]{RESET} 📺 1080p (Full HD)")
            print(f"  {CYAN}[3]{RESET} 📱 720p (HD)")
            print(f"  {CYAN}[4]{RESET} 📀 480p (Standard Definition)")
            print(f"  {CYAN}[5]{RESET} 💾 360p (Data Saver)")
            res_in = input(f"\n{BOLD}Select resolution [1-5, default: 1]: {RESET}").strip()
            fallback_map = {"1": None, "2": 1080, "3": 720, "4": 480, "5": 360}
            chosen_res = fallback_map.get(res_in, None)
    elif fmt_choice == "3":
        mode = "original_audio"
    else:
        mode = "mp3"

    # Destination folder
    save_dir = choose_directory(
        title="Select Folder to Save Downloaded Media",
        default_dir=os.path.expanduser("~/Downloads" if os.path.exists(os.path.expanduser("~/Downloads")) else "~/Documents")
    )
    if not save_dir:
        print(f"{YELLOW}Download folder cancelled.{RESET}")
        return

    res = download_media(url, save_dir, download_mode=mode, resolution=chosen_res)
    if res.get("success"):
        print_success_card(res)
        prompt_open(res.get("output", save_dir))
    else:
        print_error_card(res.get("error", "Download failed"))

def prompt_open(path: str):
    """Prompt user whether to open the generated file or directory."""
    try:
        ans = input(f"{CYAN}Open file/folder now? [y/N]: {RESET}").strip().lower()
        if ans in ("y", "yes"):
            open_file_or_dir(path)
    except (KeyboardInterrupt, EOFError):
        pass

def main():
    while True:
        try:
            extra_categories = registry.build_menu_categories(start_number=17)
            display_menu(extra_categories=extra_categories)
            max_opt = 16 + len(registry.plugins)
            choice = input(f"{BOLD}👉 Enter option number [0-{max_opt}]: {RESET}").strip()

            if choice == "1":
                run_photo_to_pdf()
            elif choice == "2":
                run_pdf_to_images()
            elif choice == "3":
                run_word_to_pdf()
            elif choice == "4":
                run_pdf_to_word()
            elif choice == "5":
                run_ppt_to_pdf()
            elif choice == "6":
                run_pdf_to_ppt()
            elif choice == "7":
                run_excel_to_pdf()
            elif choice == "8":
                run_pdf_to_excel()
            elif choice == "9":
                run_merge_pdf()
            elif choice == "10":
                run_split_pdf()
            elif choice == "11":
                run_compress_pdf()
            elif choice == "12":
                run_rotate_pdf()
            elif choice == "13":
                run_protect_pdf()
            elif choice == "14":
                run_unlock_pdf()
            elif choice == "15":
                run_watermark_pdf()
            elif choice == "16":
                run_media_downloader()
            elif choice == "0" or choice.lower() in ("q", "quit", "exit"):
                print(f"\n{GREEN}Goodbye! 👋{RESET}\n")
                break
            elif registry.get_by_number(choice):
                plugin = registry.get_by_number(choice)
                plugin.run()
            else:
                print(f"\n{YELLOW}Invalid selection '{choice}'. Please choose 0 to {max_opt}.{RESET}")

            input(f"\n{DIM}Press Enter to return to main menu...{RESET}")
            clear_screen()
        except KeyboardInterrupt:
            print(f"\n\n{GREEN}Session interrupted. Goodbye! 👋{RESET}\n")
            break

if __name__ == "__main__":
    main()
