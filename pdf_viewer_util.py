"""PDF viewer utility with bbox overlay support."""
from pathlib import Path
from typing import Any
import io

try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageDraw
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not installed. PDF preview not available.")


def is_pdf_viewer_available() -> bool:
    """Check if PDF viewer is available."""
    return PDF2IMAGE_AVAILABLE


def render_pdf_page(
    pdf_path: str | Path,
    page_number: int = 0,
    dpi: int = 150,
    bboxes: list[dict[str, Any]] = None
) -> Image.Image | None:
    """Render a PDF page as an image with optional bbox overlays.

    Args:
        pdf_path: Path to PDF file
        page_number: Page number to render (0-indexed)
        dpi: DPI for rendering (higher = better quality but slower)
        bboxes: List of bounding boxes to overlay, each with:
            - x0, y0, x1, y1: coordinates
            - label: optional label text
            - color: optional color (default: red)

    Returns:
        PIL Image or None if rendering fails
    """
    if not PDF2IMAGE_AVAILABLE:
        return None

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return None

    try:
        # Convert PDF page to image
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=page_number + 1,
            last_page=page_number + 1
        )

        if not images:
            return None

        image = images[0]

        # Draw bboxes if provided
        if bboxes:
            draw = ImageDraw.Draw(image)

            for bbox in bboxes:
                x0 = bbox.get("x0", 0)
                y0 = bbox.get("y0", 0)
                x1 = bbox.get("x1", 0)
                y1 = bbox.get("y1", 0)
                label = bbox.get("label", "")
                color = bbox.get("color", "red")

                # Scale coordinates to match rendered DPI
                # Assuming original coords are at 72 DPI (PDF standard)
                scale = dpi / 72.0
                x0_scaled = int(x0 * scale)
                y0_scaled = int(y0 * scale)
                x1_scaled = int(x1 * scale)
                y1_scaled = int(y1 * scale)

                # Draw rectangle
                draw.rectangle(
                    [(x0_scaled, y0_scaled), (x1_scaled, y1_scaled)],
                    outline=color,
                    width=3
                )

                # Draw label if provided
                if label:
                    draw.text(
                        (x0_scaled + 5, y0_scaled - 15),
                        label,
                        fill=color
                    )

        return image

    except Exception as e:
        print(f"Error rendering PDF page: {e}")
        return None


def get_pdf_page_count(pdf_path: str | Path) -> int:
    """Get number of pages in PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Number of pages, or 0 if error
    """
    try:
        from pypdf import PdfReader

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return 0

        reader = PdfReader(pdf_path)
        return len(reader.pages)

    except Exception as e:
        print(f"Error getting page count: {e}")
        return 0


def render_pdf_with_evidence(
    pdf_path: str | Path,
    evidence_pointers: list[dict[str, Any]],
    page_number: int = 0,
    dpi: int = 150,
    claim_bboxes: dict[str, list[dict[str, Any]]] = None
) -> Image.Image | None:
    """Render PDF page with evidence bboxes highlighted.

    Args:
        pdf_path: Path to PDF file
        evidence_pointers: List of evidence pointers with 'field', 'page', 'bbox_ref'
        page_number: Page to render
        dpi: Rendering DPI
        claim_bboxes: Dictionary mapping field names to bboxes from claim data

    Returns:
        PIL Image with highlighted evidence
    """
    # Filter evidence for this page
    page_evidence = [e for e in evidence_pointers if e.get("page") == page_number]

    if not page_evidence or not claim_bboxes:
        # No evidence on this page, render normally
        return render_pdf_page(pdf_path, page_number, dpi)

    # Build bboxes to highlight
    bboxes_to_draw = []

    # Color mapping for different field types
    field_colors = {
        "claimant_name": "#FF6B6B",
        "policy_id": "#4ECDC4",
        "incident_date": "#45B7D1",
        "claim_amount_total_usd": "#F7DC6F",
        "injury_severity": "#E74C3C",
        "incident_type": "#95A5A6",
    }

    for evidence in page_evidence:
        field = evidence.get("field", "")
        evidence_page = evidence.get("page", 0)

        if evidence_page != page_number:
            continue

        # Get bboxes for this field from claim data
        field_bboxes = claim_bboxes.get(field, [])

        for bbox in field_bboxes:
            bbox_page = bbox.get("page", 0)
            if bbox_page == page_number:
                color = field_colors.get(field, "red")
                bboxes_to_draw.append({
                    "x0": bbox.get("x0", 0),
                    "y0": bbox.get("y0", 0),
                    "x1": bbox.get("x1", 0),
                    "y1": bbox.get("y1", 0),
                    "label": field.replace("_", " ").title(),
                    "color": color
                })

    return render_pdf_page(pdf_path, page_number, dpi, bboxes_to_draw)


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """Convert PIL Image to bytes.

    Args:
        image: PIL Image
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Image bytes
    """
    buf = io.BytesIO()
    image.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()
