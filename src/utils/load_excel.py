import re
from pathlib import Path
import pandas as pd
from schemas import ColumnMap, ItemDict
from utils.parse_items import extract_items


def list_workbook_sheet_names(file_path: Path | str) -> list[str]:
    workbook = pd.ExcelFile(file_path)
    return workbook.sheet_names


def find_all_header_rows(dataframe: pd.DataFrame) -> list[int]:
    header_rows = []
    for row_index in range(len(dataframe)):
        row_text = " ".join(str(value) for value in dataframe.iloc[row_index].tolist() if pd.notna(value)).lower()
        if re.search(r"opis|tehni|vrsta", row_text) and re.search(r"jed|mjer", row_text) and re.search(r"koli", row_text):
            header_rows.append(row_index)
    return header_rows


def find_column(columns: list[str], pattern: str) -> str | None:
    for column_name in columns:
        if re.search(pattern, str(column_name), re.I):
            return column_name
    return None


def map_columns(dataframe: pd.DataFrame) -> ColumnMap:
    columns = [str(column_name) for column_name in dataframe.columns]
    description_column = find_column(columns, r"opis|tehni|vrsta")
    unit_column = find_column(columns, r"jed.*mj|mjer")
    quantity_column = find_column(columns, r"koli")
    unit_price_column = find_column(columns, r"jed.*cijen|^cijena")
    if not unit_price_column:
        unit_price_column = find_column(columns, r"cijen")
    total_price_column = find_column(columns, r"ukupno|iznos")
    ordinal_column = columns[0]
    return {
        "ordinal": ordinal_column,
        "description": description_column,
        "unit": unit_column,
        "quantity": quantity_column,
        "unit_price": unit_price_column,
        "total_price": total_price_column,
    }


def read_sheet_items(
    file_path: Path | str,
    sheet_name: str,
    component: str,
    filter_component_only: bool = False,
) -> tuple[list[ItemDict], list[str]]:
    raw_dataframe = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    if len(raw_dataframe) == 0:
        return [], []

    header_rows = find_all_header_rows(raw_dataframe)
    if not header_rows:
        return [], []

    best_items: list[ItemDict] = []
    best_dropped_rows: list[str] = []
    for header_row in header_rows:
        dataframe = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
        column_map = map_columns(dataframe)
        items, dropped_rows = extract_items(
            dataframe,
            column_map,
            sheet_name,
            component,
            filter_component_only=filter_component_only,
        )
        if len(items) > len(best_items):
            best_items = items
            best_dropped_rows = dropped_rows

    return best_items, best_dropped_rows
