from pathlib import Path
from constants import (
    COMPONENT_LABELS,
    COMPONENT_SHEET_PATTERNS,
    SKIP_SHEET_KEYWORDS,
)
from schemas import DetectionResult, SheetDetail, SheetScore, VectorArray
from utils.cosine_similarity import cosine_similarity
from utils.load_excel import list_workbook_sheet_names, read_sheet_items
from utils.parse_items import sheet_uses_component_row_filter


def component_label_texts(component: str) -> list[str]:
    return COMPONENT_LABELS.get(component, [component])


def is_skip_sheet_name(sheet_name: str) -> bool:
    sheet_lower = sheet_name.lower()
    return any(keyword in sheet_lower for keyword in SKIP_SHEET_KEYWORDS)


def is_component_sheet_by_name(sheet_name: str, component: str) -> bool:
    if is_skip_sheet_name(sheet_name):
        return False
    if sheet_uses_component_row_filter(sheet_name, component):
        return True
    sheet_patterns = COMPONENT_SHEET_PATTERNS.get(component, ())
    return any(pattern.search(sheet_name) for pattern in sheet_patterns)


def score_sheet_names(
    sheet_names: list[str],
    component: str,
    component_vectors: VectorArray,
    sheet_vectors: VectorArray,
) -> list[SheetScore]:
    sheet_scores: list[SheetScore] = []
    for sheet_index, sheet_name in enumerate(sheet_names):
        if is_skip_sheet_name(sheet_name):
            sheet_scores.append({
                "sheet_name": sheet_name,
                "embedding_score": 0.0,
                "name_match": False,
                "final_score": 0.0,
            })
            continue

        embedding_score = max(
            cosine_similarity(sheet_vectors[sheet_index], component_vector)
            for component_vector in component_vectors
        )
        name_match = is_component_sheet_by_name(sheet_name, component)
        final_score = 1.0 if name_match else embedding_score
        sheet_scores.append({
            "sheet_name": sheet_name,
            "embedding_score": round(embedding_score, 4),
            "name_match": name_match,
            "final_score": round(final_score, 4),
        })

    return sheet_scores


def select_component_sheets(
    sheet_names: list[str],
    sheet_scores: list[SheetScore],
    component: str,
    sheet_similarity_threshold: float,
) -> list[str]:
    name_matches = [
        sheet_name
        for sheet_name in sheet_names
        if is_component_sheet_by_name(sheet_name, component)
    ]
    if name_matches:
        return name_matches

    if len(sheet_names) == 1 and sheet_uses_component_row_filter(sheet_names[0], component):
        return [sheet_names[0]]

    return [
        row["sheet_name"]
        for row in sheet_scores
        if row["embedding_score"] >= sheet_similarity_threshold and not is_skip_sheet_name(row["sheet_name"])
    ]


def count_sheet_items(file_path: Path | str, sheet_name: str, component: str) -> int:
    filter_component_only = sheet_uses_component_row_filter(sheet_name, component)
    sheet_items, _ = read_sheet_items(
        file_path,
        sheet_name,
        component,
        filter_component_only=filter_component_only,
    )
    return len(sheet_items)


def find_component_sheets(
    file_path: Path | str,
    component: str,
    sheet_similarity_threshold: float,
    component_vectors: VectorArray,
    sheet_vectors: VectorArray,
) -> DetectionResult:
    sheet_names = list_workbook_sheet_names(file_path)
    sheet_scores = score_sheet_names(
        sheet_names,
        component,
        component_vectors,
        sheet_vectors,
    )
    selected_sheets = select_component_sheets(
        sheet_names,
        sheet_scores,
        component,
        sheet_similarity_threshold,
    )

    if not selected_sheets:
        return {
            "status": "no_component",
            "message": f"This file does not contain a {component}-related sheet/component.",
            "sheets": [],
            "sheet_scores": sheet_scores,
        }

    usable_sheets: list[SheetDetail] = []
    for sheet_name in selected_sheets:
        item_count = count_sheet_items(file_path, sheet_name, component)
        if item_count > 0:
            usable_sheets.append({"sheet_name": sheet_name, "item_count": item_count})

    if not usable_sheets:
        return {
            "status": "empty_sheet",
            "message": f"{component} sheet found, but it contains no usable rows.",
            "sheets": selected_sheets,
            "sheet_scores": sheet_scores,
        }

    return {
        "status": "ok",
        "message": "",
        "sheets": [row["sheet_name"] for row in usable_sheets],
        "sheet_details": usable_sheets,
        "sheet_scores": sheet_scores,
    }
