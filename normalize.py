"""Normalization utilities for extracted fields."""
import re
from datetime import datetime
from typing import Any


def normalize_currency(text: str | None) -> float | None:
    """Parse currency string and return USD amount."""
    if not text:
        return None

    # Remove common currency symbols and text
    text = str(text).replace("$", "").replace("USD", "").replace(",", "").strip()

    # Extract first number
    match = re.search(r"[\d.]+", text)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def normalize_date(text: str | None) -> str | None:
    """Parse date string and return ISO yyyy-mm-dd format."""
    if not text:
        return None

    text = str(text).strip()

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def compute_keyword_score(text: str, keywords: list[str]) -> float:
    """Compute keyword match score from text."""
    if not text or not keywords:
        return 0.0

    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in text_lower)
    return matches / len(keywords) if keywords else 0.0


def extract_adverse_keywords(text: str) -> list[str]:
    """Extract adverse keywords from text."""
    if not text:
        return []

    adverse_vocab = [
        "staged", "prior loss", "inconsistent story", "suspicious",
        "fraud", "conflicting", "exaggerated", "dubious",
        "repeat", "multiple claims", "false", "fabricated"
    ]

    text_lower = text.lower()
    found = []
    for kw in adverse_vocab:
        if kw in text_lower:
            found.append(kw)

    return found


def normalize_injury_severity(text: str | None) -> str:
    """Normalize injury severity to standard values."""
    if not text:
        return "none"

    text_lower = str(text).lower()

    if any(word in text_lower for word in ["severe", "critical", "life-threatening", "major"]):
        return "severe"
    elif any(word in text_lower for word in ["minor", "slight", "small", "bruise"]):
        return "minor"

    return "none"


def normalize_incident_type(text: str | None) -> str:
    """Normalize incident type to standard categories."""
    if not text:
        return "auto"

    text_lower = str(text).lower()

    if any(word in text_lower for word in ["theft", "stolen", "burglar"]):
        return "theft"
    elif any(word in text_lower for word in ["property", "building", "home", "house"]):
        return "property"
    elif any(word in text_lower for word in ["liability", "injury", "slip", "fall"]):
        return "liability"

    return "auto"
