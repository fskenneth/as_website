"""Astra Staging pricing engine — single source of truth.

Mirrors the per-item and per-area pricing currently inlined in
``page/staging_inquiry.py`` (items_data ~line 580, getAreaPrice ~line 1423,
BASE/SMALL/BIG/HUGE constants ~line 1145). Kept pure-Python so both the
website and Anna (the voice agent) can call it.

The primary entry point is :func:`quote`. When the staging_inquiry page is
eventually refactored, it should import from here instead of duplicating
the table.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Pricing tables

BASE_STAGING_FEE = 1450.00

# Per-area bulk prices used when the customer picks an area without itemizing.
SMALL_AREA = 200.00
BIG_AREA = 500.00
HUGE_AREA = 700.00

# Single-unit item prices. Keys are the display names used on the website
# modal; keep these 1:1 with ``items_data`` in page/staging_inquiry.py.
ITEM_PRICES: dict[str, float] = {
    "Sofa": 250,
    "Accent Chair": 100,
    "Coffee Table": 100,
    "End Table": 50,
    "Console": 75,
    "Bench": 65,
    "Area Rug": 80,
    "Lamp": 40,
    "Cushion": 15,
    "Throw": 18,
    "Table Decor": 10,
    "Wall Art": 40,
    "Formal Dining Set": 400,
    "Bar Stool": 40,
    "Casual Dining Set": 250,
    "Queen Bed Frame": 20,
    "Queen Headboard": 90,
    "Queen Mattress": 50,
    "Queen Beddings": 120,
    "King Bed Frame": 20,
    "King Headboard": 130,
    "King Mattress": 50,
    "King Beddings": 150,
    "Double Bed Frame": 20,
    "Double Headboard": 80,
    "Double Mattress": 50,
    "Double Bedding": 120,
    "Night Stand": 60,
    "Single Bed Frame": 20,
    "Single Headboard": 75,
    "Single Mattress": 50,
    "Single Beddings": 80,
    "Desk": 100,
    "Chair": 50,
    "Patio Set": 150,
}

PropertyType = Literal["condo", "townhouse", "house"]
PropertySize = Literal[
    "under-1000", "1000-2000", "2000-3000", "3000-4000", "over-4000"
]

# property_type -> allowed sizes, matching the website's sizeOptions map.
VALID_SIZES: dict[str, tuple[str, ...]] = {
    "condo": ("under-1000", "1000-2000", "2000-3000"),
    "townhouse": ("1000-2000", "2000-3000", "3000-4000"),
    "house": ("2000-3000", "3000-4000", "over-4000"),
}

# Canonical area slugs (match data-area attributes on the website).
VALID_AREAS: tuple[str, ...] = (
    "living-room",
    "dining-room",
    "family-room",
    "kitchen-only",
    "kitchen-island",
    "breakfast-area",
    "master-bedroom",
    "2nd-bedroom",
    "3rd-bedroom",
    "4th-bedroom",
    "5th-bedroom",
    "6th-bedroom",
    "office",
    "bathrooms",
    "basement-living",
    "basement-dining",
    "basement-1st-bedroom",
    "basement-2nd-bedroom",
    "basement-office",
    "outdoor",
)


# ---------------------------------------------------------------------------
# Core pricing logic — keep behaviour aligned with getAreaPrice / getBaseFee
# in page/staging_inquiry.py.


def _is_large_house(pt: str, ps: str) -> bool:
    return pt == "house" and ps in ("3000-4000", "over-4000")


def _is_small_condo(pt: str, ps: str) -> bool:
    return pt == "condo" and ps == "under-1000"


def base_fee(property_size: str) -> float:
    """Flat staging fee that escalates with raw square footage."""
    fee = BASE_STAGING_FEE
    if property_size in ("2000-3000", "3000-4000", "over-4000"):
        fee += 800
    elif property_size == "1000-2000":
        fee += 200
    return fee


def area_bulk_price(area: str, property_type: str, property_size: str) -> float:
    """Bulk (no-itemization) price for one staging area."""
    large = _is_large_house(property_type, property_size)
    small = _is_small_condo(property_type, property_size)

    if area == "living-room":
        return HUGE_AREA if large else BIG_AREA
    if area == "dining-room":
        if small:
            return SMALL_AREA
        return HUGE_AREA if large else BIG_AREA
    if area == "family-room":
        return HUGE_AREA if large else BIG_AREA
    if area == "kitchen-only":
        return 0
    if area == "kitchen-island":
        if small:
            return 100
        return 300 if large else 200
    if area == "breakfast-area":
        return SMALL_AREA
    if area == "master-bedroom":
        if small:
            return SMALL_AREA
        return HUGE_AREA if large else BIG_AREA
    if area == "2nd-bedroom":
        return BIG_AREA if large else SMALL_AREA
    if area in ("3rd-bedroom", "4th-bedroom", "5th-bedroom", "6th-bedroom"):
        return SMALL_AREA
    if area == "office":
        return BIG_AREA if large else SMALL_AREA
    if area == "bathrooms":
        return 0
    if area == "basement-living":
        return BIG_AREA
    if area in (
        "basement-dining",
        "basement-1st-bedroom",
        "basement-2nd-bedroom",
        "basement-office",
    ):
        return SMALL_AREA
    if area == "outdoor":
        return 150
    return 0


# ---------------------------------------------------------------------------
# Public result types


@dataclass
class AreaQuote:
    area: str
    bulk_price: float
    item_total: float | None  # None if customer didn't pick items
    charged_price: float  # min(bulk, item_total) if items present else bulk
    items: list[tuple[str, int, float]] = field(default_factory=list)  # (name, qty, line_total)


@dataclass
class Quote:
    property_type: str
    property_size: str
    base_fee: float
    areas: list[AreaQuote]
    subtotal: float  # base_fee + sum(area.charged_price)

    def summary_line(self) -> str:
        """One-sentence version suitable for speaking out loud."""
        area_count = sum(1 for a in self.areas if a.charged_price > 0)
        size_phrases = {
            "under-1000": "under 1000",
            "1000-2000": "1000 to 2000",
            "2000-3000": "2000 to 3000",
            "3000-4000": "3000 to 4000",
            "over-4000": "over 4000",
        }
        size_phrase = size_phrases.get(self.property_size, self.property_size)
        area_word = "area" if area_count == 1 else "areas"
        return (
            f"For a {self.property_type} at {size_phrase} square feet, "
            f"staging {area_count} {area_word}, you're looking at "
            f"about ${self.subtotal:,.0f} plus HST."
        )


# ---------------------------------------------------------------------------
# Entry point


def quote(
    property_type: str,
    property_size: str,
    areas: dict[str, list[tuple[str, int]]] | None = None,
) -> Quote:
    """Price a staging job.

    Args:
        property_type: ``"condo"``, ``"townhouse"``, or ``"house"``.
        property_size: one of :data:`VALID_SIZES[property_type]`.
        areas: optional mapping of area slug to item list. Each item is a
            ``(name, quantity)`` pair where ``name`` is a key in
            :data:`ITEM_PRICES`. Areas present with an empty list (or not
            present in the map but passed another way) are charged at the
            bulk price. Areas omitted entirely are not staged.

    Raises:
        ValueError: if property_type/size or an item name is unknown.
    """
    if property_type not in VALID_SIZES:
        raise ValueError(f"unknown property_type: {property_type!r}")
    if property_size not in VALID_SIZES[property_type]:
        raise ValueError(
            f"invalid size {property_size!r} for {property_type!r}; "
            f"valid: {VALID_SIZES[property_type]}"
        )

    area_quotes: list[AreaQuote] = []
    areas = areas or {}

    for area_slug, item_list in areas.items():
        if area_slug not in VALID_AREAS:
            raise ValueError(
                f"unknown area {area_slug!r}; valid slugs: {VALID_AREAS}"
            )
        bulk = area_bulk_price(area_slug, property_type, property_size)

        if item_list:
            item_lines: list[tuple[str, int, float]] = []
            total = 0.0
            for name, qty in item_list:
                if name not in ITEM_PRICES:
                    raise ValueError(f"unknown item {name!r}")
                line = ITEM_PRICES[name] * qty
                item_lines.append((name, qty, line))
                total += line
            # Website rule: charge the lesser of bulk vs itemized.
            charged = min(bulk, total) if total > 0 else bulk
            area_quotes.append(
                AreaQuote(
                    area=area_slug,
                    bulk_price=bulk,
                    item_total=total,
                    charged_price=charged,
                    items=item_lines,
                )
            )
        else:
            area_quotes.append(
                AreaQuote(
                    area=area_slug,
                    bulk_price=bulk,
                    item_total=None,
                    charged_price=bulk,
                )
            )

    fee = base_fee(property_size)
    subtotal = fee + sum(a.charged_price for a in area_quotes)

    return Quote(
        property_type=property_type,
        property_size=property_size,
        base_fee=fee,
        areas=area_quotes,
        subtotal=subtotal,
    )
