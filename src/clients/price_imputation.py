import re
import numpy as np
from sentence_transformers import SentenceTransformer
from constants import PRICE_IMPUTATION_MIN_CATALOG_SIMILARITY
from clients.embedding import cosine_similarity
from clients.web_search import fetch_page_text


_price_imputation_model: SentenceTransformer | None = None
_price_imputation_model_name: str | None = None
_price_catalog_by_websites: dict[tuple[str, ...], list[tuple[str, float]]] = {}


def parse_preferred_websites(preferred_websites_value: str) -> list[str]:
    return [
        website.strip()
        for website in preferred_websites_value.split(",")
        if website.strip()
    ]


def invalidate_price_imputation_model_cache() -> None:
    global _price_imputation_model, _price_imputation_model_name
    _price_imputation_model = None
    _price_imputation_model_name = None


def reload_price_imputation_model(price_imputation_model_name: str) -> None:
    global _price_imputation_model, _price_imputation_model_name
    _price_imputation_model = SentenceTransformer(price_imputation_model_name)
    _price_imputation_model_name = price_imputation_model_name


def clear_price_catalog_cache() -> None:
    global _price_catalog_by_websites
    _price_catalog_by_websites = {}


def get_price_imputation_model(price_imputation_model_name: str) -> SentenceTransformer:
    global _price_imputation_model, _price_imputation_model_name
    if (
        _price_imputation_model is None
        or _price_imputation_model_name != price_imputation_model_name
    ):
        reload_price_imputation_model(price_imputation_model_name)
    return _price_imputation_model


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
        title = re.sub(r"<[^>]+>", " ", section_match.group(1))
        title = re.sub(r"\s+", " ", title).strip()
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


def load_internet_price_catalog(preferred_websites: list[str]) -> list[tuple[str, float]]:
    catalog_cache_key = tuple(preferred_websites)
    if catalog_cache_key in _price_catalog_by_websites:
        return _price_catalog_by_websites[catalog_cache_key]

    catalog: list[tuple[str, float]] = []
    for website_url in preferred_websites:
        page_text = fetch_page_text(website_url)
        catalog.extend(parse_price_catalog_from_page_text(page_text))

    _price_catalog_by_websites[catalog_cache_key] = catalog
    return catalog


def find_best_catalog_price(
    item_description: str,
    catalog: list[tuple[str, float]],
    price_imputation_model_name: str,
) -> float | None:
    if not catalog:
        return None

    price_imputation_model = get_price_imputation_model(price_imputation_model_name)
    item_vector = price_imputation_model.encode([item_description], show_progress_bar=False)[0]
    catalog_descriptions = [catalog_row[0] for catalog_row in catalog]
    catalog_vectors = price_imputation_model.encode(catalog_descriptions, show_progress_bar=False)

    best_price = None
    best_similarity = -1.0

    for catalog_index, catalog_vector in enumerate(catalog_vectors):
        similarity = cosine_similarity(
            np.array(item_vector, dtype=np.float64),
            np.array(catalog_vector, dtype=np.float64),
        )
        if similarity > best_similarity:
            best_similarity = similarity
            best_price = catalog[catalog_index][1]

    if best_price is None or best_similarity < PRICE_IMPUTATION_MIN_CATALOG_SIMILARITY:
        return None
    return best_price


def impute_unit_price(
    item_description: str,
    price_imputation_model_name: str,
    preferred_websites_value: str,
) -> float | None:
    preferred_websites = parse_preferred_websites(preferred_websites_value)
    if preferred_websites:
        preferred_catalog = load_internet_price_catalog(preferred_websites)
        preferred_price = find_best_catalog_price(
            item_description,
            preferred_catalog,
            price_imputation_model_name,
        )
        if preferred_price is not None:
            return preferred_price

    return None
