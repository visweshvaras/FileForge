"""
Media Downloader Module using yt-dlp and ffmpeg.
Supports downloading high-quality audio songs (MP3 with album art) and videos with custom resolution selection (4K, 1440p, 1080p, 720p, etc.).
Optimized for YouTube, YouTube Music, SoundCloud, and 1000+ streaming sites.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import time
from typing import Dict, Any, Optional, List

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def sanitize_media_url(url: str) -> str:
    """
    Sanitize YouTube / YouTube Music URLs:
    - Removes automated radio queue mixes (&list=RD...) which cause infinite playlist scraping.
    - Normalizes clean direct video/song links.
    """
    clean = url.strip()
    if "youtube.com" in clean or "youtu.be" in clean:
        if "list=RD" in clean:
            clean = re.sub(r'[?&]list=RD[^&]*', '', clean)
            if '?' not in clean and '&' in clean:
                clean = clean.replace('&', '?', 1)
    return clean

def get_media_info(url: str) -> Optional[Dict[str, Any]]:
    """Fetch title, duration, and uploader using yt-dlp."""
    yt_bin = shutil.which("yt-dlp")
    if not yt_bin:
        return None
    try:
        clean_url = sanitize_media_url(url)
        cmd = [
            yt_bin,
            "--dump-single-json",
            "--no-warnings",
            "--no-playlist",
            clean_url
        ]
        if shutil.which("node"):
            cmd.extend(["--js-runtimes", "node"])

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            return {
                "title": data.get("title", "Unknown Title"),
                "uploader": data.get("uploader", "Unknown Artist"),
                "duration": data.get("duration", 0),
                "thumbnail": data.get("thumbnail"),
                "extractor": data.get("extractor_key", "Media")
            }
    except Exception:
        pass
    return None

def get_available_resolutions(url: str) -> List[Dict[str, Any]]:
    """
    Detect all available video resolutions for a given video URL.
    Returns a list of dicts: [{'height': 2160, 'label': '2160p (4K UHD)', 'fps': 60}, ...] sorted descending.
    """
    yt_bin = shutil.which("yt-dlp")
    if not yt_bin:
        return []

    clean_url = sanitize_media_url(url)
    cmd = [
        yt_bin,
        "-J",
        "--no-playlist",
        "--no-warnings",
        clean_url
    ]
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
        if res.returncode != 0 or not res.stdout.strip():
            return []

        data = json.loads(res.stdout)
        formats = data.get("formats", [])

        res_map = {}
        for f in formats:
            h = f.get("height")
            vcodec = f.get("vcodec", "none")
            if h and vcodec != "none":
                fps = f.get("fps") or 30
                if h not in res_map or fps > res_map[h]:
                    res_map[h] = int(fps)

        label_map = {
            4320: "4320p (8K Ultra HD)",
            2160: "2160p (4K UHD)",
            1440: "1440p (2K QHD)",
            1080: "1080p (Full HD)",
            720:  "720p (HD)",
            480:  "480p (Standard Definition)",
            360:  "360p (Data Saver)",
            240:  "240p (Low Quality)",
            144:  "144p (Minimum)",
        }

        results = []
        for h in sorted(res_map.keys(), reverse=True):
            # Only list heights of 144 and above
            if h < 144:
                continue
            base_label = label_map.get(h, f"{h}p")
            fps = res_map[h]
            results.append({
                "height": h,
                "label": base_label,
                "fps": fps
            })

        return results
    except Exception:
        return []

def download_media(
    url: str,
    output_dir: str,
    download_mode: str = "mp3",  # 'mp3', 'video', '720p_video', 'original_audio'
    resolution: Optional[int] = None
) -> Dict[str, Any]:
    """
    Download video or audio using yt-dlp.

    Args:
        url: Link to media (YouTube, YouTube Music, SoundCloud, Instagram, etc.)
        output_dir: Folder to save downloaded file.
        download_mode: 'mp3', 'video', '720p_video', 'original_audio'
        resolution: Specific video height target (e.g. 2160, 1440, 1080, 720). None for Best Available.
    """
    t0 = time.time()
    yt_bin = shutil.which("yt-dlp")
    if not yt_bin:
        return {"success": False, "error": "yt-dlp executable not found in PATH."}

    os.makedirs(output_dir, exist_ok=True)
    out_template = os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s")

    clean_url = sanitize_media_url(url)

    cmd = [
        yt_bin,
        "--no-mtime",
        "--embed-metadata",
        "--no-playlist"
    ]

    # Use Node.js for solving JS signature challenges
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node", "--remote-components", "ejs:github"])

    if download_mode == "mp3":
        cmd.extend([
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--convert-thumbnails", "png",
            "--embed-thumbnail",
            "-o", out_template,
            clean_url
        ])
    elif download_mode == "original_audio":
        cmd.extend([
            "-x",
            "--convert-thumbnails", "png",
            "--embed-thumbnail",
            "-o", out_template,
            clean_url
        ])
    elif download_mode in ("video", "best_video"):
        if resolution:
            format_spec = f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best"
        else:
            format_spec = "bestvideo+bestaudio/best"

        cmd.extend([
            "-f", format_spec,
            "--merge-output-format", "mp4",
            "--convert-thumbnails", "png",
            "--embed-thumbnail",
            "-o", out_template,
            clean_url
        ])
    elif download_mode == "720p_video":
        cmd.extend([
            "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "--merge-output-format", "mp4",
            "--convert-thumbnails", "png",
            "--embed-thumbnail",
            "-o", out_template,
            clean_url
        ])
    else:
        cmd.extend([
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "--convert-thumbnails", "png",
            "--embed-thumbnail",
            "-o", out_template,
            clean_url
        ])

    print(f"\n{CYAN}{BOLD}⚡ Starting yt-dlp download...{RESET}\n")

    captured_errors = []

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in proc.stdout:
            sys_line = line.strip()
            if not sys_line:
                continue

            if "[download]" in sys_line and "%" in sys_line:
                print(f"\r{CYAN}{sys_line}{RESET}", end="", flush=True)
            elif "ERROR:" in sys_line:
                print(f"\n{RED}{BOLD}{sys_line}{RESET}")
                captured_errors.append(sys_line)
            elif "WARNING:" in sys_line:
                if "older than 90 days" not in sys_line:
                    print(f"\n{YELLOW}{sys_line}{RESET}")
            elif any(tag in sys_line for tag in ["[ExtractAudio]", "[Merger]", "[EmbedThumbnail]", "[Metadata]", "[ThumbnailsConvertor]"]):
                print(f"\n{GREEN}{sys_line}{RESET}")
            elif "[download] Destination:" in sys_line:
                print(f"\n{YELLOW}{sys_line}{RESET}")
            elif "[youtube]" in sys_line or "[info]" in sys_line:
                print(f"  {DIM}{sys_line}{RESET}")

        proc.wait()
        print()  # newline after progress

        if proc.returncode != 0:
            err_details = "\n".join(captured_errors[-3:]) if captured_errors else f"yt-dlp process exited with error code {proc.returncode}"
            return {"success": False, "error": err_details}

        # Find the downloaded file in output_dir modified recently
        candidates = []
        for root, _, files in os.walk(output_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime >= t0 - 5:
                        candidates.append((mtime, fpath))
                except OSError:
                    pass

        mode_desc = f"{resolution}p Video" if resolution else download_mode
        if candidates:
            candidates.sort(reverse=True)
            downloaded_file = candidates[0][1]
            f_size = os.path.getsize(downloaded_file)
            return {
                "success": True,
                "input": clean_url,
                "output": downloaded_file,
                "count": "1 media file",
                "size_bytes": f_size,
                "duration": time.time() - t0,
                "format": mode_desc
            }
        else:
            return {
                "success": True,
                "input": clean_url,
                "output": output_dir,
                "count": "Media downloaded",
                "duration": time.time() - t0,
                "format": mode_desc
            }

    except Exception as e:
        return {"success": False, "error": f"Download failed: {e}"}
