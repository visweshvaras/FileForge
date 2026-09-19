"""
Cross-Platform File Dialog Manager.
Supports Windows (Tkinter / PowerShell native dialogs),
Linux (Zenity / Tkinter), macOS (Tkinter / AppleScript),
with an interactive terminal drag-and-drop fallback.
"""
import os
import sys
import shutil
import subprocess
from typing import List, Optional

def _has_zenity() -> bool:
    """Check if zenity is installed and a display is available (Linux)."""
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return has_display and (shutil.which("zenity") is not None)

def _pick_via_tkinter(
    title: str,
    file_filters: Optional[List[str]] = None,
    multiple: bool = False,
    save: bool = False,
    default_filename: Optional[str] = None,
    directory: bool = False,
    initial_dir: Optional[str] = None
):
    """
    Native GUI dialog via tkinter.
    Built-in by default on Windows & macOS Python distributions.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        # Bring dialog to the front
        root.attributes('-topmost', True)
        root.update()

        # Format filetypes: [('Supported Files', '*.jpg *.png'), ('All Files', '*.*')]
        types = []
        if file_filters:
            ext_pat = " ".join(file_filters)
            types.append(("Supported Files", ext_pat))
        types.append(("All Files", "*.*"))

        result = None
        if directory:
            result = filedialog.askdirectory(title=title, initialdir=initial_dir)
        elif save:
            result = filedialog.asksaveasfilename(
                title=title,
                initialdir=initial_dir,
                initialfile=default_filename,
                filetypes=types
            )
        else:
            if multiple:
                files = filedialog.askopenfilenames(
                    title=title,
                    initialdir=initial_dir,
                    filetypes=types
                )
                result = list(files) if files else []
            else:
                f = filedialog.askopenfilename(
                    title=title,
                    initialdir=initial_dir,
                    filetypes=types
                )
                result = [f] if f else []

        root.destroy()
        return result
    except Exception:
        return None

def _pick_via_windows_ps(
    title: str,
    file_filters: Optional[List[str]] = None,
    multiple: bool = False,
    save: bool = False,
    default_filename: Optional[str] = None,
    directory: bool = False,
    initial_dir: Optional[str] = None
):
    """
    Native Windows dialog via PowerShell System.Windows.Forms.
    Guaranteed available on 100% of Windows systems as a zero-dependency fallback.
    """
    if sys.platform != "win32":
        return None

    try:
        filter_str = ""
        if file_filters:
            patterns = ";".join(file_filters)
            filter_str = f"Supported Files ({patterns})|{patterns}|All Files (*.*)|*.*"
        else:
            filter_str = "All Files (*.*)|*.*"

        init_dir_arg = f"$f.InitialDirectory = '{initial_dir}';" if initial_dir else ""

        if directory:
            ps_cmd = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                f"$f.Description = '{title}'; "
                f"{init_dir_arg} "
                f"if($f.ShowDialog() -eq 'OK'){{ $f.SelectedPath }}"
            )
        elif save:
            init_file_arg = f"$f.FileName = '{default_filename}';" if default_filename else ""
            ps_cmd = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$f = New-Object System.Windows.Forms.SaveFileDialog; "
                f"$f.Title = '{title}'; "
                f"$f.Filter = '{filter_str}'; "
                f"{init_dir_arg} {init_file_arg} "
                f"if($f.ShowDialog() -eq 'OK'){{ $f.FileName }}"
            )
        else:
            multi_str = "$true" if multiple else "$false"
            ps_cmd = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$f = New-Object System.Windows.Forms.OpenFileDialog; "
                f"$f.Title = '{title}'; "
                f"$f.Multiselect = {multi_str}; "
                f"$f.Filter = '{filter_str}'; "
                f"{init_dir_arg} "
                f"if($f.ShowDialog() -eq 'OK'){{ $f.FileNames -join '|' }}"
            )

        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            raw = res.stdout.strip()
            if directory or save:
                return raw
            files = raw.split("|") if multiple else [raw]
            return [os.path.abspath(f.strip()) for f in files if os.path.isfile(f.strip())]
    except Exception:
        pass
    return None

def choose_input_files(
    title: str = "Select File",
    file_filters: Optional[List[str]] = None,
    multiple: bool = False,
    default_dir: Optional[str] = None
) -> List[str]:
    """
    Pop up native file selection window.
    Returns list of chosen absolute file paths.
    """
    initial_dir = default_dir or os.path.expanduser("~/Documents")

    # 1. On Windows: Try Tkinter, then PowerShell
    if sys.platform == "win32":
        print(f"\n\033[96m📂 Opening file picker window...\033[0m Please select your file(s).")
        res = _pick_via_tkinter(title, file_filters, multiple=multiple, initial_dir=initial_dir)
        if res is not None and len(res) > 0:
            return [os.path.abspath(f) for f in res if os.path.isfile(f)]
        
        ps_res = _pick_via_windows_ps(title, file_filters, multiple=multiple, initial_dir=initial_dir)
        if ps_res:
            return ps_res

    # 2. On Linux: Try Zenity first
    elif _has_zenity():
        cmd = [
            "zenity",
            "--file-selection",
            f"--title={title}",
            f"--filename={os.path.join(initial_dir, '')}",
        ]
        if multiple:
            cmd.append("--multiple")
            cmd.append("--separator=|")

        if file_filters:
            filter_str = " ".join(file_filters)
            cmd.append(f"--file-filter=Supported Files ({filter_str}) | {filter_str}")
            cmd.append("--file-filter=All Files | *")

        try:
            print(f"\n\033[96m📂 Opening file picker window...\033[0m Please select your file(s).")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode == 0:
                raw = proc.stdout.strip()
                if raw:
                    files = raw.split("|") if multiple else [raw]
                    valid = [os.path.abspath(f.strip()) for f in files if os.path.isfile(f.strip())]
                    if valid:
                        return valid
        except Exception:
            pass

    # 3. On macOS or other Unix: Try Tkinter
    else:
        res = _pick_via_tkinter(title, file_filters, multiple=multiple, initial_dir=initial_dir)
        if res is not None and len(res) > 0:
            return [os.path.abspath(f) for f in res if os.path.isfile(f)]

    # 4. Terminal fallback
    print(f"\n\033[93m[File Picker]\033[0m {title}")
    if file_filters:
        print(f"Supported extensions: {', '.join(file_filters)}")
    prompt_txt = "Enter file path(s) separated by comma (or drag & drop here): " if multiple else "Enter file path (or drag & drop here): "
    
    try:
        user_input = input(prompt_txt).strip().strip("'\"")
        if not user_input:
            return []
        
        paths = [p.strip().strip("'\"") for p in user_input.split(",")] if multiple else [user_input]
        valid = [os.path.abspath(os.path.expanduser(p)) for p in paths if os.path.isfile(os.path.expanduser(p))]
        return valid
    except (KeyboardInterrupt, EOFError):
        return []

def choose_save_location(
    title: str = "Save File As",
    default_filename: str = "output.pdf",
    file_filters: Optional[List[str]] = None,
    default_dir: Optional[str] = None
) -> Optional[str]:
    """
    Pop up native Save As file selection window.
    Returns chosen absolute destination file path.
    """
    initial_dir = default_dir or os.path.expanduser("~/Documents")
    suggested_path = os.path.join(initial_dir, default_filename)

    # 1. On Windows: Try Tkinter, then PowerShell
    if sys.platform == "win32":
        print(f"\n\033[96m💾 Opening save dialog...\033[0m Choose where to save your file.")
        res = _pick_via_tkinter(
            title, file_filters, save=True, default_filename=default_filename, initial_dir=initial_dir
        )
        if res:
            ext = os.path.splitext(default_filename)[1]
            if ext and not res.lower().endswith(ext.lower()):
                res += ext
            return os.path.abspath(res)

        ps_res = _pick_via_windows_ps(
            title, file_filters, save=True, default_filename=default_filename, initial_dir=initial_dir
        )
        if ps_res:
            ext = os.path.splitext(default_filename)[1]
            if ext and not ps_res.lower().endswith(ext.lower()):
                ps_res += ext
            return os.path.abspath(ps_res)

    # 2. On Linux: Try Zenity first
    elif _has_zenity():
        cmd = [
            "zenity",
            "--file-selection",
            "--save",
            "--confirm-overwrite",
            f"--title={title}",
            f"--filename={suggested_path}",
        ]
        if file_filters:
            filter_str = " ".join(file_filters)
            cmd.append(f"--file-filter=Destination Format ({filter_str}) | {filter_str}")
            cmd.append("--file-filter=All Files | *")

        try:
            print(f"\n\033[96m💾 Opening save dialog...\033[0m Choose where to save your file.")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode == 0:
                chosen = proc.stdout.strip()
                if chosen:
                    ext = os.path.splitext(default_filename)[1]
                    if ext and not chosen.lower().endswith(ext.lower()):
                        chosen += ext
                    return os.path.abspath(chosen)
        except Exception:
            pass

    # 3. On macOS or other Unix: Try Tkinter
    else:
        res = _pick_via_tkinter(
            title, file_filters, save=True, default_filename=default_filename, initial_dir=initial_dir
        )
        if res:
            ext = os.path.splitext(default_filename)[1]
            if ext and not res.lower().endswith(ext.lower()):
                res += ext
            return os.path.abspath(res)

    # 4. Terminal fallback
    print(f"\n\033[93m[Save Dialog]\033[0m {title}")
    prompt_txt = f"Enter destination file path [default: {suggested_path}]: "
    try:
        user_input = input(prompt_txt).strip().strip("'\"")
        if not user_input:
            return suggested_path
        target = os.path.abspath(os.path.expanduser(user_input))
        if os.path.isdir(target):
            target = os.path.join(target, default_filename)
        return target
    except (KeyboardInterrupt, EOFError):
        return None

def choose_directory(
    title: str = "Select Destination Folder",
    default_dir: Optional[str] = None
) -> Optional[str]:
    """
    Pop up native folder selection window.
    Returns chosen absolute folder path.
    """
    initial_dir = default_dir or os.path.expanduser("~/Downloads" if os.path.exists(os.path.expanduser("~/Downloads")) else "~/Documents")

    # 1. On Windows: Try Tkinter, then PowerShell
    if sys.platform == "win32":
        print(f"\n\033[96m📂 Opening folder picker window...\033[0m Choose where to save.")
        res = _pick_via_tkinter(title, directory=True, initial_dir=initial_dir)
        if res:
            return os.path.abspath(res)
        
        ps_res = _pick_via_windows_ps(title, directory=True, initial_dir=initial_dir)
        if ps_res:
            return os.path.abspath(ps_res)

    # 2. On Linux: Try Zenity
    elif _has_zenity():
        cmd = [
            "zenity",
            "--file-selection",
            "--directory",
            f"--title={title}",
            f"--filename={os.path.join(initial_dir, '')}",
        ]
        try:
            print(f"\n\033[96m📂 Opening folder picker window...\033[0m Choose where to save.")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode == 0:
                chosen = proc.stdout.strip()
                if chosen and os.path.isdir(chosen):
                    return os.path.abspath(chosen)
        except Exception:
            pass

    # 3. On macOS or other Unix: Try Tkinter
    else:
        res = _pick_via_tkinter(title, directory=True, initial_dir=initial_dir)
        if res:
            return os.path.abspath(res)

    # 4. Terminal fallback
    print(f"\n\033[93m[Folder Picker]\033[0m {title}")
    prompt_txt = f"Enter destination folder path [default: {initial_dir}]: "
    try:
        user_input = input(prompt_txt).strip().strip("'\"")
        if not user_input:
            return initial_dir
        target = os.path.abspath(os.path.expanduser(user_input))
        if os.path.isdir(target):
            return target
        os.makedirs(target, exist_ok=True)
        return target
    except (KeyboardInterrupt, EOFError):
        return None
