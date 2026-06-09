from datetime import datetime
from pathlib import Path
import pandas as pd
from constants import OUTPUT_DIR
from schemas import SummaryRow, TemplateRow


def offer_column_prefix(offer_name: str) -> str:
    return Path(offer_name).stem.replace(" ", "_")


def blank_if_none(value: str | float | int | None) -> str | float | int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return value


def build_summary_rows(template_rows: list[TemplateRow], offer_names: list[str]) -> list[SummaryRow]:
    summary_rows: list[SummaryRow] = []
    for template_row in template_rows:
        row: SummaryRow = {"item": template_row["embed_text"]}
        for offer_name in offer_names:
            prefix = offer_column_prefix(offer_name)
            offer_data = template_row["offers"].get(offer_name, {})
            row[f"{prefix}_unit"] = blank_if_none(offer_data.get("unit"))
            row[f"{prefix}_qty"] = blank_if_none(offer_data.get("quantity"))
            row[f"{prefix}_unit_price"] = blank_if_none(offer_data.get("unit_price"))
            row[f"{prefix}_total"] = blank_if_none(offer_data.get("total_price"))
        summary_rows.append(row)
    return summary_rows


def build_total_row(summary_rows: list[SummaryRow], offer_names: list[str]) -> SummaryRow:
    total_row: SummaryRow = {"item": "UKUPNO"}
    for offer_name in offer_names:
        prefix = offer_column_prefix(offer_name)
        total_column = f"{prefix}_total"
        line_totals = [
            row[total_column] for row in summary_rows
            if row[total_column] != "" and row[total_column] is not None
        ]
        total_row[total_column] = sum(line_totals) if line_totals else ""
    return total_row


def build_output_path(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"troskovnik_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.csv"
    return output_dir / file_name


def write_summary_csv(
    template_rows: list[TemplateRow],
    offer_names: list[str],
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    summary_rows = build_summary_rows(template_rows, offer_names)
    summary_rows.append(build_total_row(summary_rows, offer_names))
    output_path = build_output_path(output_dir)
    pd.DataFrame(summary_rows).to_csv(output_path, index=False)
    return output_path
