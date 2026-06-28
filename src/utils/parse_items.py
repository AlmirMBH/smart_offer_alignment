import re
import pandas as pd
from constants import COMPONENT_ITEM_KEYWORDS, COMPONENT_ROW_FILTER_SHEETS
from schemas import ColumnMap, ItemDict
from utils.price_imputation import calculate_total_price
from utils.text import truncate_text


def sheet_uses_component_row_filter(sheet_name: str, component: str) -> bool:
    row_filter_sheet_names = COMPONENT_ROW_FILTER_SHEETS.get(component, ())
    return sheet_name.strip().upper() in row_filter_sheet_names


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip())


def build_embed_text(parent_description: str, child_description: str) -> str:
    parent_text = parent_description or ""
    child_text = child_description or ""
    return collapse_whitespace(f"{parent_text} {child_text}".strip())


def has_ordinal(ordinal_value: str | None) -> bool:
    if pd.isna(ordinal_value):
        return False
    ordinal_text = str(ordinal_value).strip()
    if not ordinal_text or ordinal_text.lower() == "nan":
        return False
    return bool(re.match(r"^[\dA-Za-z]", ordinal_text))


def is_section_title(description_text: str) -> bool:
    description_text = collapse_whitespace(description_text)
    if not description_text:
        return True
    if len(description_text) < 80 and description_text.upper() == description_text:
        return True
    if re.match(r"^P\d+\b", description_text, re.I):
        return True
    if re.match(r"^(RADOVI|INSTALACIJE|UKUPNO)\b", description_text, re.I):
        return True
    return False


def read_cell(row: pd.Series, column_name: str | None) -> str | None:
    if column_name is None:
        return None
    value = row.get(column_name)
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() == "nan" or text == "":
        return None
    return text


def read_number(row: pd.Series, column_name: str | None) -> float | None:
    if column_name is None:
        return None
    value = row.get(column_name)
    if pd.isna(value):
        return None
    number_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(number_value):
        return None
    return float(number_value)


def clean_price_value(price_value: float | None) -> float | None:
    if price_value is None or price_value == 0:
        return None
    return price_value


def apply_prices(
    quantity: float | None,
    unit_price: float | None,
    total_price: float | None,
) -> tuple[float | None, float | None]:
    unit_price = clean_price_value(unit_price)
    total_price = clean_price_value(total_price)
    if quantity and unit_price and not total_price:
        total_price = calculate_total_price(quantity, unit_price)
    elif quantity and total_price and not unit_price:
        unit_price = total_price / quantity
    return unit_price, total_price


def is_component_row(parent_description: str, child_description: str, component: str) -> bool:
    item_keywords = COMPONENT_ITEM_KEYWORDS.get(component, ())
    embed_text = build_embed_text(parent_description, child_description).lower()
    return any(keyword in embed_text for keyword in item_keywords)


def extract_items(
    dataframe: pd.DataFrame,
    column_map: ColumnMap,
    source_sheet: str,
    component: str,
    filter_component_only: bool = False,
) -> tuple[list[ItemDict], list[str]]:
    items: list[ItemDict] = []
    dropped_rows: list[str] = []
    current_parent = ""

    for _, row in dataframe.iterrows():
        ordinal_value = read_cell(row, column_map["ordinal"])
        description_value = read_cell(row, column_map["description"])
        unit_value = read_cell(row, column_map["unit"])
        quantity_value = read_number(row, column_map["quantity"])
        unit_price_value = read_number(row, column_map["unit_price"])
        total_price_value = read_number(row, column_map["total_price"])

        has_unit_or_quantity = unit_value is not None and quantity_value is not None

        if not description_value and not has_unit_or_quantity:
            continue

        if has_unit_or_quantity:
            if has_ordinal(ordinal_value) and description_value and not is_section_title(description_value):
                parent_description = ""
                child_description = description_value
                current_parent = description_value
            elif description_value:
                parent_description = current_parent
                child_description = description_value
            elif current_parent:
                parent_description = current_parent
                child_description = ""
            else:
                dropped_rows.append("row with unit/qty but no description or parent")
                continue

            if filter_component_only and not is_component_row(parent_description, child_description, component):
                dropped_rows.append(f"non-{component}: {truncate_text(build_embed_text(parent_description, child_description))}")
                continue

            unit_price_value, total_price_value = apply_prices(
                quantity_value, unit_price_value, total_price_value
            )

            items.append({
                "source_sheet": source_sheet,
                "parent_description": parent_description,
                "child_description": child_description,
                "unit": unit_value,
                "quantity": quantity_value,
                "unit_price": unit_price_value,
                "total_price": total_price_value,
            })
            continue

        if description_value and is_section_title(description_value):
            current_parent = ""
            continue

        if has_ordinal(ordinal_value) and description_value and not is_section_title(description_value):
            current_parent = description_value
        elif description_value and current_parent:
            current_parent = collapse_whitespace(f"{current_parent} {description_value}")
        elif description_value:
            current_parent = description_value

    return items, dropped_rows
