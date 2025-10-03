"""Utility functions for timing, bbox handling, and PDF rendering."""
import time
from functools import wraps
from typing import Any, Callable
from pathlib import Path
import io


def timeit(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
    return wrapper


def bbox_overlap(bbox1: dict[str, float], bbox2: dict[str, float]) -> float:
    """Compute overlap ratio between two bboxes."""
    x1 = max(bbox1["x0"], bbox2["x0"])
    y1 = max(bbox1["y0"], bbox2["y0"])
    x2 = min(bbox1["x1"], bbox2["x1"])
    y2 = min(bbox1["y1"], bbox2["y1"])

    if x2 < x1 or y2 < y1:
        return 0.0

    intersection = (x2 - x1) * (y2 - y1)
    area1 = (bbox1["x1"] - bbox1["x0"]) * (bbox1["y1"] - bbox1["y0"])
    area2 = (bbox2["x1"] - bbox2["x0"]) * (bbox2["y1"] - bbox2["y0"])

    union = area1 + area2 - intersection
    return intersection / union if union > 0 else 0.0


def bbox_to_coords(bbox: dict[str, Any]) -> tuple[float, float, float, float]:
    """Extract coordinates from bbox dict."""
    return bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]


def render_pdf_page(pdf_path: str | Path, page_num: int = 0) -> bytes | None:
    """Render a PDF page to PNG image bytes."""
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        if images:
            buf = io.BytesIO()
            images[0].save(buf, format="PNG")
            return buf.getvalue()
    except Exception:
        # Fallback: try pypdf for basic rendering
        pass

    return None


def render_pdf_with_bboxes(pdf_path: str | Path, page_num: int, bboxes: list[dict[str, Any]]) -> bytes | None:
    """Render PDF page with bounding boxes overlaid."""
    try:
        from PIL import Image, ImageDraw
        from pdf2image import convert_from_path

        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        if not images:
            return None

        img = images[0]
        draw = ImageDraw.Draw(img, "RGBA")

        for bbox in bboxes:
            if bbox.get("page") == page_num:
                x0, y0, x1, y1 = bbox_to_coords(bbox)
                # Scale to image size (assuming 72 DPI)
                scale = img.width / 612  # Standard letter width in points
                coords = [x0 * scale, y0 * scale, x1 * scale, y1 * scale]
                draw.rectangle(coords, outline="red", width=3)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default
