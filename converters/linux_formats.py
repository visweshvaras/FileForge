"""
Linux Formats & Application Execution Engine.
Comprehensive management for standalone Linux files:
1. .AppImage Portable Applications (run, FUSE check, desktop integration)
2. .deb Software Packages (APT dependency resolution, DPKG + repair, inspect/extract)
3. .tar / .tar.gz / .tar.xz / .zip Compressed Archives (safe extraction, binary & doc discovery)
4. .run Self-extracting Installers (chmod +x, sudo/user execution)
5. .sh and .bin Shell Scripts & Binaries (chmod +x, interactive execution)
6. Snap & Flatpak Package Management (search, install, local .flatpakref)
7. Universal Smart Runner (auto-detect any Linux file and launch)
"""
import os
import sys
import shutil
import subprocess
import tarfile
import zipfile
import stat
from typing import Dict, Any, List, Optional, Tuple

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ==============================================================================
# 1. FORMAT DETECTION
# ==============================================================================

def detect_linux_format(filepath: str) -> Dict[str, Any]:
    """
    Detect the Linux file type based on extension and magic header bytes.
    Returns metadata dictionary with format type, label, and description.
    """
    if not os.path.exists(filepath):
        return {
            "format": "invalid",
            "label": "File Not Found",
            "description": f"The file '{filepath}' does not exist."
        }

    lower_name = os.path.basename(filepath).lower()
    
    # 1. AppImage
    if lower_name.endswith(".appimage"):
        return {
            "format": "appimage",
            "label": "AppImage Portable Application",
            "description": "Standalone Linux application containing all required libraries.",
            "icon": "📦"
        }

    # 2. Debian Package
    if lower_name.endswith(".deb"):
        return {
            "format": "deb",
            "label": "Debian / Ubuntu Package (.deb)",
            "description": "System software package for Debian/Ubuntu with dependency tracking.",
            "icon": "💿"
        }

    # 3. Archives
    archive_exts = (
        ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz",
        ".tar", ".zip", ".tar.zst"
    )
    for ext in archive_exts:
        if lower_name.endswith(ext):
            return {
                "format": "archive",
                "label": f"Compressed Software Archive ({ext})",
                "description": "Compressed bundle containing binaries, scripts, or source code.",
                "icon": "🗜️"
            }

    # 4. .run Installer
    if lower_name.endswith(".run"):
        return {
            "format": "run",
            "label": "Self-Extracting Linux Installer (.run)",
            "description": "Executable installer package often used for drivers, games, and vendor tools.",
            "icon": "⚡"
        }

    # 5. Shell scripts & binary installers
    if lower_name.endswith((".sh", ".bash", ".bin")):
        return {
            "format": "script",
            "label": "Shell Script / Setup Binary (.sh / .bin)",
            "description": "Linux executable script or installation binary.",
            "icon": "📜"
        }

    # 6. Flatpak packages / references
    if lower_name.endswith((".flatpakref", ".flatpak")):
        return {
            "format": "flatpak",
            "label": "Flatpak Application / Reference",
            "description": "Sandboxed desktop application format for Flatpak runtime.",
            "icon": "🌐"
        }

    # 7. Check ELF binary header if no known extension
    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
            if header == b"\x7fELF":
                # Check if it has AppImage signature in ELF
                f.seek(8)
                ai_magic = f.read(3)
                if ai_magic in (b"AI\x01", b"AI\x02"):
                    return {
                        "format": "appimage",
                        "label": "AppImage Portable Application (detected via ELF)",
                        "description": "Standalone Linux application containing all required libraries.",
                        "icon": "📦"
                    }
                return {
                    "format": "binary",
                    "label": "Linux ELF Native Binary",
                    "description": "Compiled executable binary for Linux systems.",
                    "icon": "⚙️"
                }
    except Exception:
        pass

    return {
        "format": "unknown",
        "label": "Unrecognized Linux Format",
        "description": "File does not match common Linux package or installer signatures.",
        "icon": "❓"
    }


# ==============================================================================
# 2. APPIMAGE HANDLER
# ==============================================================================

def is_fuse_available() -> bool:
    """Check if FUSE subsystem is working on the system."""
    fuse_dev = os.path.exists("/dev/fuse")
    has_fusermount = shutil.which("fusermount") is not None or shutil.which("fusermount3") is not None
    return fuse_dev and has_fusermount


def make_executable(filepath: str) -> bool:
    """Ensure executable bits (chmod +x) are set on the file."""
    try:
        current_stat = os.stat(filepath)
        os.chmod(filepath, current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except Exception as e:
        print(f"{YELLOW}Warning: Could not set executable permission: {e}{RESET}")
        return False


def run_appimage(
    filepath: str,
    install_desktop: bool = False,
    force_extract_run: bool = False,
    background: bool = True
) -> Dict[str, Any]:
    """
    Execute an AppImage file.
    - Sets chmod +x.
    - Checks FUSE compatibility (falls back to --appimage-extract-and-run if FUSE is absent).
    - Optionally creates a .desktop file in ~/.local/share/applications/ for system menu integration.
    """
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"success": False, "error": f"File '{abs_path}' does not exist."}

    # Step 1: Make executable
    make_executable(abs_path)

    # Step 2: Check FUSE
    cmd = [abs_path]
    needs_extract = force_extract_run or (not is_fuse_available())
    if needs_extract:
        cmd.append("--appimage-extract-and-run")
        print(f"{YELLOW}ℹ️  Using '--appimage-extract-and-run' mode (FUSE bypass).{RESET}")

    # Step 3: Desktop integration if requested
    desktop_file = None
    if install_desktop:
        desktop_file = integrate_appimage_desktop(abs_path)

    # Step 4: Launch application
    try:
        if background:
            # Spawn detached process so terminal stays open and clean
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return {
                "success": True,
                "pid": proc.pid,
                "command": " ".join(cmd),
                "desktop_file": desktop_file,
                "message": f"AppImage launched in background (PID {proc.pid})."
            }
        else:
            ret = subprocess.call(cmd)
            return {
                "success": ret == 0,
                "returncode": ret,
                "command": " ".join(cmd),
                "desktop_file": desktop_file,
                "message": f"AppImage finished with exit code {ret}."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def integrate_appimage_desktop(appimage_path: str) -> Optional[str]:
    """
    Creates a .desktop launcher entry in ~/.local/share/applications/
    so the AppImage permanently appears in the Ubuntu / GNOME application menu.
    """
    base_name = os.path.splitext(os.path.basename(appimage_path))[0]
    clean_title = base_name.replace("-", " ").replace("_", " ").title()
    
    app_dir = os.path.expanduser("~/Applications")
    os.makedirs(app_dir, exist_ok=True)
    
    # Copy or reference AppImage
    target_appimage = os.path.join(app_dir, os.path.basename(appimage_path))
    if os.path.abspath(appimage_path) != os.path.abspath(target_appimage):
        try:
            shutil.copy2(appimage_path, target_appimage)
            make_executable(target_appimage)
            exec_path = target_appimage
        except Exception:
            exec_path = appimage_path
    else:
        exec_path = appimage_path

    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    desktop_file = os.path.join(desktop_dir, f"appimage-{base_name.lower()}.desktop")

    desktop_content = f"""[Desktop Entry]
Type=Application
Name={clean_title}
Exec="{exec_path}" %U
Icon=application-x-executable
Terminal=false
Categories=Utility;Application;
Comment=Installed via FileForge Linux Workstation
"""
    try:
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(desktop_content)
        
        # Update system desktop database
        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", desktop_dir], capture_output=True)

        return desktop_file
    except Exception as e:
        print(f"{YELLOW}Warning: Could not create desktop entry: {e}{RESET}")
        return None


# ==============================================================================
# 3. DEB PACKAGE HANDLER
# ==============================================================================

def get_deb_info(filepath: str) -> Dict[str, Any]:
    """Extract metadata (Package, Version, Architecture, Description, Depends) from .deb."""
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"error": "File not found"}

    dpkg_deb = shutil.which("dpkg-deb")
    if not dpkg_deb:
        return {"error": "dpkg-deb command is not installed."}

    try:
        proc = subprocess.run(
            [dpkg_deb, "-I", abs_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if proc.returncode != 0:
            return {"error": proc.stderr.strip() or "Failed to read deb package"}

        raw_info = proc.stdout
        info: Dict[str, str] = {}
        for line in raw_info.splitlines():
            line_str = line.strip()
            if line_str.startswith("Package:"):
                info["package"] = line_str.split(":", 1)[1].strip()
            elif line_str.startswith("Version:"):
                info["version"] = line_str.split(":", 1)[1].strip()
            elif line_str.startswith("Architecture:"):
                info["architecture"] = line_str.split(":", 1)[1].strip()
            elif line_str.startswith("Installed-Size:"):
                info["installed_size"] = line_str.split(":", 1)[1].strip() + " KB"
            elif line_str.startswith("Depends:"):
                info["depends"] = line_str.split(":", 1)[1].strip()
            elif line_str.startswith("Description:"):
                info["description"] = line_str.split(":", 1)[1].strip()

        info["file_size"] = f"{os.path.getsize(abs_path):,} bytes"
        info["filename"] = os.path.basename(abs_path)
        return info
    except Exception as e:
        return {"error": str(e)}


def install_deb(filepath: str, method: str = "apt") -> Dict[str, Any]:
    """
    Install a .deb file using APT (auto-resolves dependencies) or DPKG (with fix-broken).
    Note: 'sudo apt install ./package.deb' strictly requires the leading './' or absolute path!
    """
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"success": False, "error": f"File '{abs_path}' does not exist."}

    print(f"\n{CYAN}{BOLD}⚡ Preparing installation for: {os.path.basename(abs_path)}{RESET}\n")

    if method == "apt":
        # Using APT with explicit absolute or relative path
        cmd = ["sudo", "apt", "install", "-y", abs_path]
        print(f"{DIM}Running command: {' '.join(cmd)}{RESET}\n")
        ret = subprocess.call(cmd)
        return {
            "success": ret == 0,
            "returncode": ret,
            "method": "apt",
            "message": "Package installed successfully via APT." if ret == 0 else f"APT returned exit code {ret}."
        }
    elif method == "dpkg":
        # Classic DPKG + auto-repair
        cmd1 = ["sudo", "dpkg", "-i", abs_path]
        print(f"{DIM}Running: {' '.join(cmd1)}{RESET}\n")
        ret1 = subprocess.call(cmd1)
        if ret1 != 0:
            print(f"\n{YELLOW}⚠️  Missing dependencies encountered. Running 'sudo apt --fix-broken install' to resolve...{RESET}\n")
            cmd2 = ["sudo", "apt", "--fix-broken", "install", "-y"]
            ret2 = subprocess.call(cmd2)
            return {
                "success": ret2 == 0,
                "returncode": ret2,
                "method": "dpkg_repaired",
                "message": "Installed via DPKG with dependency auto-repair." if ret2 == 0 else "Dependency repair failed."
            }
        return {
            "success": True,
            "returncode": 0,
            "method": "dpkg",
            "message": "Package installed successfully via DPKG."
        }
    else:
        return {"success": False, "error": f"Unknown installation method '{method}'"}


def extract_deb_contents(filepath: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
    """Extract contents of .deb package to examine files without needing root permissions."""
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    dpkg_deb = shutil.which("dpkg-deb")
    if not dpkg_deb:
        return {"success": False, "error": "dpkg-deb is not available."}

    if not target_dir:
        base = os.path.splitext(os.path.basename(abs_path))[0]
        target_dir = os.path.join(os.path.dirname(abs_path), f"{base}_extracted")

    os.makedirs(target_dir, exist_ok=True)
    try:
        proc = subprocess.run([dpkg_deb, "-x", abs_path, target_dir], capture_output=True, text=True)
        if proc.returncode == 0:
            return {"success": True, "target_dir": target_dir}
        return {"success": False, "error": proc.stderr.strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# 4. ARCHIVE HANDLER (.tar.gz, .tar.xz, .zip)
# ==============================================================================

def is_safe_path(base_dir: str, path: str) -> bool:
    """Prevent ZipSlip and Tar directory traversal attacks."""
    matchpath = os.path.abspath(os.path.join(base_dir, path))
    return base_dir == os.path.commonpath([base_dir, matchpath])


def extract_archive(filepath: str, target_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely extract .tar, .tar.gz, .tar.xz, .tar.bz2, or .zip archives.
    Scans the extracted folder for READMEs, documentation, and executable binaries.
    """
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"success": False, "error": f"File '{abs_path}' not found."}

    # Determine extract target directory
    if not target_dir:
        base_name = os.path.basename(abs_path)
        for ext in (".tar.gz", ".tar.xz", ".tar.bz2", ".tgz", ".tbz2", ".txz", ".zip", ".tar"):
            if base_name.lower().endswith(ext):
                base_name = base_name[:-len(ext)]
                break
        target_dir = os.path.join(os.path.dirname(abs_path), f"{base_name}_extracted")

    os.makedirs(target_dir, exist_ok=True)

    try:
        lower = abs_path.lower()
        if lower.endswith(".zip"):
            with zipfile.ZipFile(abs_path, 'r') as zf:
                for member in zf.namelist():
                    if is_safe_path(target_dir, member):
                        zf.extract(member, target_dir)
        elif lower.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz", ".tar")):
            with tarfile.open(abs_path, 'r:*') as tf:
                for member in tf.getmembers():
                    if is_safe_path(target_dir, member.name):
                        tf.extract(member, target_dir, filter="data" if hasattr(tarfile, 'data_filter') else None)
        else:
            return {"success": False, "error": "Unsupported archive format."}

        # Inspect extracted contents for docs and executables
        inspection = scan_directory_for_executables_and_docs(target_dir)

        return {
            "success": True,
            "target_dir": target_dir,
            "executables": inspection["executables"],
            "docs": inspection["docs"]
        }
    except Exception as e:
        return {"success": False, "error": f"Extraction failed: {e}"}


def scan_directory_for_executables_and_docs(dir_path: str) -> Dict[str, List[Dict[str, str]]]:
    """Scan directory recursively for README documentation and executable programs."""
    executables = []
    docs = []

    doc_names = ("readme", "install", "usage", "license", "changelog", "getting_started")

    for root, _, files in os.walk(dir_path):
        for f in files:
            full_path = os.path.join(root, f)
            lower = f.lower()

            # Check docs
            base_doc = os.path.splitext(lower)[0]
            if base_doc in doc_names or any(lower.startswith(d) for d in doc_names):
                docs.append({
                    "name": f,
                    "path": full_path,
                    "rel_path": os.path.relpath(full_path, dir_path)
                })

            # Check executables: .sh, .bin, start*, run*, or executable permission or ELF
            is_exec = False
            desc = "Executable"
            if lower.endswith((".sh", ".bash")):
                is_exec = True
                desc = "Shell Script"
            elif lower.endswith(".bin"):
                is_exec = True
                desc = "Binary Program"
            elif lower in ("start", "run", "launch", "setup", "install", "main"):
                is_exec = True
                desc = "Startup Executable"
            else:
                # Check ELF header
                try:
                    with open(full_path, "rb") as bf:
                        if bf.read(4) == b"\x7fELF":
                            is_exec = True
                            desc = "ELF Native Binary"
                except Exception:
                    pass

            if is_exec:
                make_executable(full_path)
                executables.append({
                    "name": f,
                    "type": desc,
                    "path": full_path,
                    "rel_path": os.path.relpath(full_path, dir_path)
                })

    return {"executables": executables, "docs": docs}


# ==============================================================================
# 5. .RUN INSTALLER HANDLER
# ==============================================================================

def execute_run_installer(filepath: str, use_sudo: bool = True, extra_args: str = "") -> Dict[str, Any]:
    """
    Execute a self-extracting .run installer (commonly used for proprietary drivers & packages).
    Grants chmod +x and runs interactively.
    """
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"success": False, "error": f"File '{abs_path}' not found."}

    make_executable(abs_path)

    cmd = []
    if use_sudo:
        cmd.append("sudo")
    cmd.append(abs_path)

    if extra_args.strip():
        cmd.extend(extra_args.strip().split())

    print(f"\n{CYAN}{BOLD}⚡ Executing Installer:{RESET} {' '.join(cmd)}\n")

    try:
        ret = subprocess.call(cmd)
        return {
            "success": ret == 0,
            "returncode": ret,
            "message": f"Installer exited with code {ret}."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# 6. .SH AND .BIN SCRIPTS HANDLER
# ==============================================================================

def execute_script(filepath: str, use_sudo: bool = False, extra_args: str = "") -> Dict[str, Any]:
    """Execute a .sh shell script or .bin binary with chmod +x."""
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not os.path.isfile(abs_path):
        return {"success": False, "error": f"File '{abs_path}' not found."}

    make_executable(abs_path)

    cmd = []
    if use_sudo:
        cmd.append("sudo")
    
    if abs_path.endswith((".sh", ".bash")):
        cmd.extend(["bash", abs_path])
    else:
        cmd.append(abs_path)

    if extra_args.strip():
        cmd.extend(extra_args.strip().split())

    print(f"\n{CYAN}{BOLD}▶ Executing Script:{RESET} {' '.join(cmd)}\n")

    try:
        ret = subprocess.call(cmd)
        return {
            "success": ret == 0,
            "returncode": ret,
            "message": f"Script execution finished with return code {ret}."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==============================================================================
# 7. SNAP & FLATPAK QUICK ASSISTANT
# ==============================================================================

def check_package_managers() -> Dict[str, bool]:
    """Check availability of snap and flatpak."""
    return {
        "snap": shutil.which("snap") is not None,
        "flatpak": shutil.which("flatpak") is not None
    }


def search_package(query: str, manager: str = "all") -> Dict[str, Any]:
    """Search Snap Store or Flathub for applications."""
    results = {"snap": [], "flatpak": []}
    
    if manager in ("all", "snap") and shutil.which("snap"):
        try:
            proc = subprocess.run(["snap", "find", query], capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                lines = proc.stdout.strip().splitlines()
                # Skip header
                for line in lines[1:10]:
                    parts = line.split()
                    if len(parts) >= 3:
                        results["snap"].append({
                            "name": parts[0],
                            "version": parts[1],
                            "publisher": parts[2],
                            "notes": " ".join(parts[3:]) if len(parts) > 3 else ""
                        })
        except Exception:
            pass

    if manager in ("all", "flatpak") and shutil.which("flatpak"):
        try:
            proc = subprocess.run(["flatpak", "search", query], capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                lines = proc.stdout.strip().splitlines()
                for line in lines[:8]:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        results["flatpak"].append({
                            "name": parts[0].strip(),
                            "id": parts[1].strip() if len(parts) > 1 else "",
                            "version": parts[2].strip() if len(parts) > 2 else "",
                            "branch": parts[3].strip() if len(parts) > 3 else "",
                            "description": parts[4].strip() if len(parts) > 4 else ""
                        })
        except Exception:
            pass

    return results


def install_flatpak_file(filepath: str) -> Dict[str, Any]:
    """Install local .flatpak or .flatpakref file."""
    abs_path = os.path.abspath(os.path.expanduser(filepath))
    if not shutil.which("flatpak"):
        return {"success": False, "error": "Flatpak is not installed on this system. Run: sudo apt install flatpak"}

    cmd = ["flatpak", "install", "-y", abs_path]
    print(f"\n{CYAN}{BOLD}⚡ Running Flatpak install:{RESET} {' '.join(cmd)}\n")
    try:
        ret = subprocess.call(cmd)
        return {"success": ret == 0, "message": f"Flatpak install completed with exit code {ret}."}
    except Exception as e:
        return {"success": False, "error": str(e)}
