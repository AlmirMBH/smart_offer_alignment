import re
from utils.parse_items import collapse_whitespace

_price_catalog_by_websites: dict[tuple[str, ...], list[tuple[str, float]]] = {}


def clear_price_catalog_cache() -> None:
    global _price_catalog_by_websites
    _price_catalog_by_websites = {}


def parse_preferred_websites(preferred_websites_value: str) -> list[str]:
    return [
        website.strip()
        for website in preferred_websites_value.split(",")
        if website.strip()
    ]


def parse_price_range_midpoint(price_range_text: str) -> float | None:
    numbers = re.findall(r"\d+(?:[.,]\d+)?", price_range_text)
    if not numbers:
        return None
    values = [float(number.replace(",", ".")) for number in numbers[:2]]
    if len(values) == 1:
        return values[0]
    return sum(values) / len(values)


def parse_price_catalog_from_page_text(page_text: str) -> list[tuple[str, float]]:
    catalog: list[tuple[str, float]] = []

    for section_match in re.finditer(
        r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2[^>]*>|$)",
        page_text,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        title = collapse_whitespace(re.sub(r"<[^>]+>", " ", section_match.group(1)))
        if not title:
            continue

        body = section_match.group(2)
        price_match = re.search(
            r"(\d+(?:[.,]\d+)?\s*-\s*\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)",
            body,
        )
        if not price_match:
            continue

        midpoint = parse_price_range_midpoint(price_match.group(1))
        if midpoint is not None:
            catalog.append((title.lower(), midpoint))

    return catalog


def get_price_catalog_for_websites(
    preferred_websites: list[str],
    page_texts: list[str],
) -> list[tuple[str, float]]:
    catalog_cache_key = tuple(preferred_websites)
    if catalog_cache_key in _price_catalog_by_websites:
        return _price_catalog_by_websites[catalog_cache_key]

    catalog: list[tuple[str, float]] = []
    for page_text in page_texts:
        catalog.extend(parse_price_catalog_from_page_text(page_text))

    _price_catalog_by_websites[catalog_cache_key] = catalog
    return catalog
