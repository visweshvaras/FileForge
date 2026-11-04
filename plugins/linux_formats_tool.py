"""
Community Plugin: Linux File Formats & Package Runner.
Allows running .AppImage, .deb, .tar.gz archives, .run installers, .sh scripts, and Snaps/Flatpaks.
"""
import os
import sys
import subprocess
from plugins.base_tool import BaseTool
from ui.dialogs import choose_input_files, choose_directory
from ui.terminal_menu import (
    Spinner,
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
from converters.linux_formats import (
    detect_linux_format,
    run_appimage,
    install_deb,
    get_deb_info,
    extract_deb_contents,
    extract_archive,
    execute_run_installer,
    execute_script,
    search_package,
    install_flatpak_file,
    check_package_managers,
    is_fuse_available
)


class LinuxFormatsTool(BaseTool):
    id = "linux_runner"
    name = "Linux File Formats & App Runner"
    description = "Run/install .AppImage, .deb, .tar.gz, .run, .sh & Flatpak packages"
    category = "✨ COMMUNITY EXTENSIONS"
    icon = "🐧"
    author = "@OpenForge"
    version = "1.0.0"
    dependencies = []

    def run(self) -> None:
        if os.name != "posix" or not os.path.exists("/proc"):
            print(f"{YELLOW}⚠️  This tool is designed specifically for Linux operating systems.{RESET}")
            return

        print(f"\n{CYAN}{BOLD}▶ {self.icon} {self.name}{RESET}")
        print(f"{DIM}Select an operation or pick any Linux file to execute/install:{RESET}\n")

        print("  [1] 🚀 Smart Auto-Runner (Pick ANY Linux file)")
        print("  [2] 📦 Run / Integrate .AppImage (FUSE check & desktop menu)")
        print("  [3] 💿 Install .deb Package (via APT or DPKG)")
        print("  [4] 🗜️  Extract & Run Archive (.tar.gz, .tar.xz, .zip)")
        print("  [5] ⚡ Execute .run Installer (drivers, custom software)")
        print("  [6] 📜 Execute .sh / .bin Script (with chmod +x)")
        print("  [7] 🌐 Snap & Flatpak Package Assistant")
        print("  [0] ↩️  Back")

        choice = input(f"\n{BOLD}Choose option [0-7, default: 1]: {RESET}").strip()
        if choice in ("1", ""):
            self._smart_run()
        elif choice == "2":
            self._run_appimage()
        elif choice == "3":
            self._run_deb()
        elif choice == "4":
            self._run_archive()
        elif choice == "5":
            self._run_installer()
        elif choice == "6":
            self._run_script()
        elif choice == "7":
            self._run_snap_flatpak()

    def _smart_run(self):
        files = choose_input_files(
            title="Select Linux File to Run (*.AppImage, *.deb, *.tar.*, *.run, *.sh, *.bin)",
            file_filters=["*.AppImage", "*.deb", "*.tar.*", "*.run", "*.sh", "*.bin", "*.zip", "*.*"],
            multiple=False
        )
        if not files:
            return
        f = files[0]
        info = detect_linux_format(f)
        print(f"\n{GREEN}Detected:{RESET} {info.get('icon', '📄')} {BOLD}{info.get('label')}{RESET}")
        fmt = info.get("format")
        if fmt == "appimage":
            self._run_appimage(f)
        elif fmt == "deb":
            self._run_deb(f)
        elif fmt == "archive":
            self._run_archive(f)
        elif fmt == "run":
            self._run_installer(f)
        elif fmt == "script":
            self._run_script(f)
        elif fmt == "flatpak":
            install_flatpak_file(f)
        else:
            execute_script(f, use_sudo=False)

    def _run_appimage(self, filepath=None):
        if not filepath:
            files = choose_input_files(title="Select .AppImage File", file_filters=["*.AppImage", "*.appimage"], multiple=False)
            if not files:
                return
            filepath = files[0]

        print(f"\nAppImage: {CYAN}{os.path.basename(filepath)}{RESET}")
        print("  [1] Launch in Background")
        print("  [2] Launch & Add to Ubuntu Applications Menu")
        print("  [3] Force Extract-and-run (Bypass FUSE)")
        opt = input(f"{BOLD}Select [1-3, default: 1]: {RESET}").strip()
        add_desktop = (opt == "2")
        force_ext = (opt == "3")
        res = run_appimage(filepath, install_desktop=add_desktop, force_extract_run=force_ext)
        if res.get("success"):
            print_success_card({"input": filepath, "output": "Running", "count": res.get("message")})
        else:
            print_error_card(res.get("error", "Launch failed"))

    def _run_deb(self, filepath=None):
        if not filepath:
            files = choose_input_files(title="Select .deb Package", file_filters=["*.deb"], multiple=False)
            if not files:
                return
            filepath = files[0]

        info = get_deb_info(filepath)
        if "error" not in info:
            print(f"\nPackage: {CYAN}{info.get('package')}{RESET} ({info.get('version')})")
        print("  [1] Install via APT (Recommended - resolves dependencies)")
        print("  [2] Install via DPKG (with auto-fix)")
        print("  [3] Extract & Inspect files without root")
        opt = input(f"{BOLD}Select [1-3, default: 1]: {RESET}").strip()
        if opt in ("1", ""):
            res = install_deb(filepath, method="apt")
        elif opt == "2":
            res = install_deb(filepath, method="dpkg")
        elif opt == "3":
            res = extract_deb_contents(filepath)
            if res.get("success"):
                print_success_card({"input": filepath, "output": res.get("target_dir"), "count": "Unpacked"})
                open_file_or_dir(res.get("target_dir"))
            return
        else:
            return
        if res.get("success"):
            print_success_card({"input": filepath, "output": "System", "count": res.get("message")})
        else:
            print_error_card(res.get("error", "Install failed"))

    def _run_archive(self, filepath=None):
        if not filepath:
            files = choose_input_files(title="Select Archive", file_filters=["*.tar.gz", "*.tar.xz", "*.zip"], multiple=False)
            if not files:
                return
            filepath = files[0]

        res = extract_archive(filepath)
        if res.get("success"):
            print_success_card({"input": filepath, "output": res.get("target_dir"), "count": f"Found {len(res.get('executables', []))} executables"})
            for ex in res.get("executables", [])[:5]:
                print(f"  • {GREEN}{ex['rel_path']}{RESET} ({ex['type']})")
            open_file_or_dir(res.get("target_dir"))
        else:
            print_error_card(res.get("error", "Extraction failed"))

    def _run_installer(self, filepath=None):
        if not filepath:
            files = choose_input_files(title="Select .run Installer", file_filters=["*.run"], multiple=False)
            if not files:
                return
            filepath = files[0]
        sudo_ans = input("Run with sudo? [Y/n]: ").strip().lower()
        res = execute_run_installer(filepath, use_sudo=(sudo_ans not in ("n", "no")))
        if res.get("success"):
            print_success_card({"input": filepath, "output": "Installer Finished", "count": res.get("message")})
        else:
            print_error_card(res.get("error", "Execution failed"))

    def _run_script(self, filepath=None):
        if not filepath:
            files = choose_input_files(title="Select Script", file_filters=["*.sh", "*.bin"], multiple=False)
            if not files:
                return
            filepath = files[0]
        sudo_ans = input("Run with sudo? [y/N]: ").strip().lower()
        res = execute_script(filepath, use_sudo=(sudo_ans in ("y", "yes")))
        if res.get("success"):
            print_success_card({"input": filepath, "output": "Script Finished", "count": res.get("message")})
        else:
            print_error_card(res.get("error", "Execution failed"))

    def _run_snap_flatpak(self):
        query = input(f"{BOLD}Search Snap & Flathub package name: {RESET}").strip()
        if not query:
            return
        res = search_package(query)
        for s in res.get("snap", [])[:3]:
            print(f"  • [Snap] {s['name']} - sudo snap install {s['name']}")
        for fp in res.get("flatpak", [])[:3]:
            print(f"  • [Flatpak] {fp['name']} ({fp['id']}) - flatpak install flathub {fp['id']}")
