# 🛠️ FileForge: Universal File Converter & Media Workstation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-success.svg)](#installation)
[![Offline: 100% Private](https://img.shields.io/badge/Offline-100%25%20Private-brightgreen.svg)](#features)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![AI Tools Welcome](https://img.shields.io/badge/AI%20%26%20ML%20Tools-100%25%20Welcome-blueviolet.svg)](#-total-creative-freedom--ai-tools-welcome)
[![Built by Students](https://img.shields.io/badge/Built%20by-Students%20for%20Campus-orange.svg)](#-built-by-students-for-students--join-the-openforge-movement)

A modern, high-performance, terminal-driven file converter and media workstation with native GUI file pickers. Convert documents, presentations, spreadsheets, PDFs, photos, and download media with custom resolution selection—**100% locally and privately with zero data sent to the cloud**.

---

## 🌟 Built by Students, for Students — Join the OpenForge Movement!

> *"Never made an open-source contribution or submitted a Git Pull Request before? You are in the right place!"*

**FileForge** is the founding flagship project of **OpenForge**, a student-led open-source collective. Instead of building toy classroom assignments that get discarded after exams, we are teaming up to create **production-grade, 100% offline, privacy-first tools** that our entire campus uses every day.

---

### 🤖 Total Creative Freedom — AI & Machine Learning Tools Welcome!

**Got an idea for an AI tool? Build it here! You have 100% complete creative freedom.** 

There are zero corporate gatekeepers or bureaucratic rules here. Whether you want to:
* 🎙️ Connect **Offline Whisper** to transcribe recorded audio lectures into lecture notes.
* 🦙 Integrate **Local LLMs (via Ollama or Llama.cpp)** to summarize 50-page PDF textbooks without internet.
* 👁️ Build a **Vision AI / OCR** model to solve math formulas and extract tables from blackboard photos.
* 🧠 Build an **AI flashcard or quiz generator** straight from lecture slides (`.pptx`).

FileForge's modular architecture lets you plug in ANY traditional algorithm or cutting-edge AI model with zero friction. **Your tool, your rules, your code.**

---

### 🎯 Choose Your Contribution Quest

No matter your current experience level, there is an open quest waiting for you:

| Domain | What You Can Build / Improve | Difficulty |
| :--- | :--- | :---: |
| 🤖 **AI & Smart Utilities** | Plug in local Ollama LLMs, Whisper voice transcription, AI PDF summarizers, or smart quiz generators. | 🚀 Creative / Fun |
| 🐍 **Python Converters** | Add Markdown-to-PDF (`.md` ➔ `.pdf`), code-to-PDF lab report export with syntax highlighting, or text utilities. | 🟢 Beginner |
| 👁️ **OCR & Extraction** | Add local Tesseract OCR to pull editable text & tables from photos of whiteboards and textbook pages. | 🟡 Intermediate |
| 🎨 **Desktop GUI (Frontend)** | Help build a modern, sleek desktop window (using `CustomTkinter` or `PyQt`) or design terminal ASCII art themes. | 🟢 Beginner |
| 🪟 **Cross-Platform QA** | Test converters across Windows 10/11, macOS, and Linux laptops. Find edge-case formatting bugs and submit issues. | 🟢 Beginner |
| 🌐 **Localization** | Translate menu prompts and CLI messages into regional and international languages. | 🟢 Beginner |
| 📝 **Documentation & Guides** | Improve setup instructions, record demo GIFs, or write tutorials for campus classmates. | 🟢 Beginner |

### 🚀 How to Make Your First Contribution in 3 Minutes

1. **Star this repository** ⭐ at the top right to bookmark the project!
2. **Find an issue or idea**: Check out our [Open Issues](https://github.com/visweshvaras/FileForge/issues) or pick a quest from the table above.
3. **Fork & Branch**: Fork the repo to your GitHub, create a new branch (`git switch -c feature/my-cool-feature`), and make your changes.
4. **Submit a Pull Request**: Submit your PR — our team will review it, guide you through any fixes, and merge your code!

### 🏆 Hall of Contributors
Every single contribution — whether it's 2 lines of code, a bug report, or a documentation fix — gets permanently honored on this board!

<p align="center">
  <a href="https://github.com/visweshvaras/FileForge/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=visweshvaras/FileForge" alt="OpenForge Contributors" />
  </a>
</p>

<p align="center"><i>Be the next contributor on this board! 🚀</i></p>

---

## ✨ Features at a Glance

### 📄 Document & Office Converters (Vector-Fidelity Engines)
* **Word to PDF (`.docx`, `.doc` → `.pdf`)**: Exact layout preservation with embedded images, math formulas (`<m:oMath>`), styled tables, and fonts.
* **PowerPoint to PDF (`.pptx`, `.ppt` → `.pdf`)**: Pixel-perfect conversion preserving shapes, card borders, drop shadows, and headings.
* **Excel to PDF (`.xlsx`, `.xls` → `.pdf`)**: Clean auto-fitting table rendering with custom styling.
* **PDF to Word (`.pdf` → `.docx`)**: Deep layout analysis reconstructing editable Word documents.
* **PDF to PowerPoint (`.pdf` → `.pptx`)**: High-definition slide extraction.
* **PDF to Excel (`.pdf` → `.xlsx`)**: Tabular data extraction into structured spreadsheets.
* **Photos to PDF**: Combine multiple PNG, JPG, WEBP, TIFF images into a single vector document.
* **PDF to Images**: High-resolution page extraction (200+ DPI).

### 🧰 Advanced PDF Toolkit (Completely Offline)
* **Merge PDFs**: Combine multiple PDFs in any custom order.
* **Split PDF**: Extract custom page ranges (`1-3, 5, 8-10`) or burst all pages into individual files.
* **Compress / Optimize**: Garbage-collect dead objects and deflate font streams to save up to 80% size.
* **Rotate Pages**: Rotate 90°, 180°, or 270° clockwise.
* **Protect PDF**: Standard AES-256 password encryption.
* **Unlock PDF**: Remove passwords and permissions restrictions.
* **Watermark & Page Numbers**: Add diagonal watermark stamps (`CONFIDENTIAL`, `DRAFT`) or footer page numbering (`Page X of Y`).

### 🎬 Media & Song Downloader (yt-dlp + ffmpeg)
* **Audio / Songs**: High-bitrate MP3 (320 kbps) with embedded album thumbnails and ID3 metadata tags.
* **Video**: Dynamic resolution probing—choose from **4K (2160p)**, **2K (1440p)**, **1080p Full HD**, **720p**, **480p**, or Best Available.
* **YouTube Music Support**: Automatically strips radio mixes and downloads single tracks cleanly.
* **Universal Compatibility**: Works with YouTube, SoundCloud, Instagram, Twitter/X, and 1000+ platforms.

---

## 🖥️ Cross-Platform GUI File Pickers

Although operated from the terminal, the application uses your operating system's **native file explorer dialogs**:
* **Windows**: Native Windows Explorer Open / Save dialogs (via `tkinter` / `PowerShell`).
* **Linux**: Native GNOME/KDE file picker dialogs (via `zenity` / `tkinter`).
* **macOS**: Native Aqua open/save panels.
* **Headless / SSH**: Interactive terminal drag-and-drop fallback.

---

## 🚀 Quick Start & Installation

### Prerequisites
* **Python 3.8+** installed on your system.
* *(Recommended)* **ffmpeg** for video multiplexing and MP3 thumbnail embedding.
* *(Optional)* **LibreOffice** for 100% exact vector layout fidelity on complex PPTX/DOCX documents (the application includes built-in pure-Python fallback engines if LibreOffice is not installed).

---

### 🪟 Windows Setup

1. **Clone the repository**:
   ```cmd
   git clone https://github.com/your-username/file-converter.git
   cd file-converter
   ```

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Run the application**:
   * Double-click `run.bat`
   * Or run from Command Prompt / PowerShell:
     ```cmd
     python main.py
     ```

*(Optional)* Install as a global command in Windows:
```cmd
pip install -e .
file-converter
```

---

### 🐧 Linux (Ubuntu / Debian / Fedora / Arch)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/file-converter.git
   cd file-converter
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Optional system packages for enhanced media and dialogs)*:
   ```bash
   sudo apt install ffmpeg zenity nodejs
   ```

3. **Run**:
   ```bash
   ./run.sh
   # Or directly:
   python3 main.py
   ```

*(Optional)* Make it a globally accessible command:
```bash
pip install -e .
file-converter
```

---

### 🍎 macOS Setup

1. **Clone & Install**:
   ```bash
   git clone https://github.com/your-username/file-converter.git
   cd file-converter
   pip install -r requirements.txt
   ```

2. **Run**:
   ```bash
   ./run.sh
   # Or:
   python3 main.py
   ```

---

## 🎯 Usage Workflow

1. Launch `file-converter` (or `python main.py` or double-click `run.bat`).
2. Select your desired tool `[1-16]`.
3. A native file picker popup opens to select your file(s).
4. Real-time conversion / download progress is displayed in the terminal.
5. A "Save As" popup lets you pick your target folder and filename.
6. The app prompts `Open file/folder now? [y/N]` to immediately preview your result.

---

## 📁 Project Structure

```
file-converter/
├── converters/               # Core format converters
│   ├── image_to_pdf.py       # Images to unified PDF
│   ├── pdf_to_image.py       # PDF to PNG/JPG extraction
│   ├── word_to_pdf.py        # Word (.docx) to PDF
│   ├── pdf_to_word.py        # PDF to editable Word (.docx)
│   ├── ppt_to_pdf.py         # PowerPoint (.pptx) to PDF
│   ├── pdf_to_ppt.py         # PDF to PowerPoint slides
│   ├── excel_to_pdf.py       # Excel (.xlsx) to PDF tables
│   ├── pdf_to_excel.py       # PDF to Excel (.xlsx)
│   ├── pdf_tools.py          # Merge, split, compress, rotate, protect, watermark
│   └── media_downloader.py   # yt-dlp audio & custom resolution video downloader
├── engines/                  # Dual-engine conversion layer
│   ├── libreoffice_engine.py # Headless LibreOffice vector renderer
│   └── native_engine.py      # Pure-Python fallback renderer
├── ui/                       # Cross-platform interface
│   ├── dialogs.py            # Native Windows/Linux/macOS file dialogs
│   └── terminal_menu.py      # Colored menu, spinners, and result cards
├── utils/                    # System detection & font resolution
│   ├── helper.py             # Cross-platform file opening (os.startfile / xdg-open)
│   ├── fonts.py              # System TTF font discovery (Windows & Linux)
│   └── system.py             # LibreOffice & tool discovery
├── tests/                    # Unit tests & verification
├── main.py                   # Main terminal application entry point
├── run.bat                   # 1-Click launcher for Windows
├── run.sh                    # 1-Click launcher for Linux & macOS
├── pyproject.toml            # Modern Python packaging configuration
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT Open Source License
└── README.md                 # Documentation
```

---

## 🛡️ Privacy & Security

* **100% Local Processing**: All document conversions and PDF manipulations are processed entirely in memory and on your local disk.
* **No Telemetry**: Zero analytics, tracking, or cloud uploads.
* **Safe Encryption**: Protect and unlock tools use standard AES-256 cryptography.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/cool-new-feature`).
3. Commit your changes (`git commit -m 'Add some cool feature'`).
4. Push to the branch (`git push origin feature/cool-new-feature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
