"""
Convert single or multiple images (JPEG, PNG, WEBP, etc.) into a combined PDF.
"""
import os
import time
from typing import List, Dict, Any
from PIL import Image

def images_to_pdf(input_paths: List[str], output_pdf: str) -> Dict[str, Any]:
    t0 = time.time()
    if not input_paths:
        return {"success": False, "error": "No input images provided"}

    pil_images = []
    for path in input_paths:
        if not os.path.isfile(path):
            continue
        try:
            img = Image.open(path)
            # Flatten transparency to white background if RGBA or P
            if img.mode in ("RGBA", "LA", "P"):
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                pil_images.append(rgb_img)
            elif img.mode != "RGB":
                pil_images.append(img.convert("RGB"))
            else:
                pil_images.append(img.copy())
        except Exception as e:
            return {"success": False, "error": f"Failed to load image {os.path.basename(path)}: {e}"}

    if not pil_images:
        return {"success": False, "error": "Could not read any valid images"}

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf)) or ".", exist_ok=True)

    first_image = pil_images[0]
    rest_images = pil_images[1:]

    try:
        first_image.save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=rest_images)
        duration = time.time() - t0
        return {
            "success": True,
            "input": f"{len(input_paths)} image(s) combined",
            "output": os.path.abspath(output_pdf),
            "count": f"{len(pil_images)} page(s)",
            "size_bytes": os.path.getsize(output_pdf),
            "duration": duration
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to save PDF: {e}"}
