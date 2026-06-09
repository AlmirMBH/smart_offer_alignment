from pathlib import Path
from schemas import DetectionResult, ParsedItemDict
from utils.find_component_sheets import find_component_sheets
from utils.load_excel import read_sheet_items
from utils.parse_items import build_embed_text, sheet_uses_component_row_filter


def extract_offer_items_from_excel_file(
    file_path: Path | str,
    component: str,
) -> tuple[list[ParsedItemDict], DetectionResult, dict[str, list[str]]]:
    detection = find_component_sheets(file_path, component=component)

    if detection["status"] != "ok":
        return [], detection, {}

    offer_file = Path(file_path).name
    all_items: list[ParsedItemDict] = []
    dropped_by_sheet: dict[str, list[str]] = {}

    for sheet_name in detection["sheets"]:
        filter_component_only = sheet_uses_component_row_filter(sheet_name, component)
        sheet_items, dropped_rows = read_sheet_items(
            file_path,
            sheet_name,
            component,
            filter_component_only=filter_component_only,
        )
        dropped_by_sheet[sheet_name] = dropped_rows
        for item in sheet_items:
            item["offer_file"] = offer_file
            item["component"] = component
            item["embed_text"] = build_embed_text(item["parent_description"], item["child_description"])
        all_items.extend(sheet_items)

    return all_items, detection, dropped_by_sheet
