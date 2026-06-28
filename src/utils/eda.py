from typing import cast
import pandas as pd
from schemas import (
    AnalysisChartData,
    ComparabilitySummary,
    CostByOfferRow,
    CostByOfferSheetRow,
    DataAnalysisResponse,
    DataQualitySummary,
    DistributionComparabilityByOfferSheetRow,
    ItemDistributionSummary,
    PriceStatsRow,
    SummaryByOfferSheetRow,
    TopItemByTotalRow,
    TotalsByOfferRow,
    QualityByOfferSheetRow,
)
from utils.price_imputation import calculate_total_price
from utils.text import is_blank_or_nan_text, truncate_text


def iter_offer_sheet_groups(items_dataframe: pd.DataFrame):
    for offer_file, offer_group in items_dataframe.groupby("offer_file"):
        for source_sheet, sheet_group in offer_group.groupby("source_sheet"):
            yield offer_file, source_sheet, sheet_group


def sum_total_price(sheet_group: pd.DataFrame) -> float:
    return float(sheet_group["total_price"].fillna(0).sum())


def build_price_stats_row(scope: str, unit_prices: pd.Series) -> PriceStatsRow:
    return {
        "scope": scope,
        "avg_unit_price": float(unit_prices.mean()),
        "min_unit_price": float(unit_prices.min()),
        "max_unit_price": float(unit_prices.max()),
    }


def normalized_embed_text(items_dataframe: pd.DataFrame) -> pd.Series:
    return items_dataframe["embed_text"].str.lower().str.strip()


def count_missing_unit_rows(sheet_group: pd.DataFrame) -> int:
    unit_series = sheet_group["unit"].astype(str).str.strip()
    return int(unit_series.isna().sum() + unit_series.apply(is_blank_or_nan_text).sum())


def count_missing_quantity_rows(sheet_group: pd.DataFrame) -> int:
    return int(sheet_group["quantity"].isna().sum())


def count_inconsistent_total_rows(items_dataframe: pd.DataFrame) -> int:
    inconsistent_count = 0
    for _, row in items_dataframe.iterrows():
        quantity = row["quantity"]
        unit_price = row["unit_price"]
        total_price = row["total_price"]
        if pd.notna(quantity) and pd.notna(unit_price) and pd.notna(total_price):
            if abs(calculate_total_price(quantity, unit_price) - total_price) > 0.01:
                inconsistent_count += 1
    return inconsistent_count


def count_within_offer_duplicate_groups(items_dataframe: pd.DataFrame) -> int:
    duplicate_group_count = 0
    for _, offer_group in items_dataframe.groupby("offer_file"):
        duplicate_counts = normalized_embed_text(offer_group).value_counts()
        duplicate_group_count += int((duplicate_counts > 1).sum())
    return duplicate_group_count


def build_summary_by_offer_sheet_table(items_dataframe: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []
    for offer_file, source_sheet, sheet_group in iter_offer_sheet_groups(items_dataframe):
        summary_rows.append({
            "offer_file": offer_file,
            "source_sheet": source_sheet,
            "item_count": len(sheet_group),
            "total_value": sum_total_price(sheet_group),
            "avg_embed_text_length": round(float(sheet_group["embed_text"].str.len().mean()), 1),
        })
    return pd.DataFrame(summary_rows)


def build_quality_by_offer_sheet_table(items_dataframe: pd.DataFrame) -> pd.DataFrame:
    quality_rows = []
    for offer_file, source_sheet, sheet_group in iter_offer_sheet_groups(items_dataframe):
        quality_rows.append({
            "offer_file": offer_file,
            "source_sheet": source_sheet,
            "rows_without_unit": count_missing_unit_rows(sheet_group),
            "rows_without_quantity": count_missing_quantity_rows(sheet_group),
            "rows_without_unit_price": int(sheet_group["unit_price"].isna().sum()),
            "rows_without_total_price": int(sheet_group["total_price"].isna().sum()),
        })
    return pd.DataFrame(quality_rows)


def build_totals_by_offer_table(summary_dataframe: pd.DataFrame) -> pd.DataFrame:
    total_rows = []
    for offer_file, offer_group in summary_dataframe.groupby("offer_file"):
        total_rows.append({
            "offer_file": offer_file,
            "item_count": int(offer_group["item_count"].sum()),
            "total_value": float(offer_group["total_value"].sum()),
        })
    return pd.DataFrame(total_rows)


def build_cost_by_offer_table(items_dataframe: pd.DataFrame) -> pd.DataFrame:
    cost_rows = []
    for offer_file, offer_group in items_dataframe.groupby("offer_file"):
        cost_rows.append({
            "offer_file": offer_file,
            "total_value": sum_total_price(offer_group),
            "item_count": len(offer_group),
        })
    return pd.DataFrame(cost_rows)


def build_cost_by_offer_sheet_table(items_dataframe: pd.DataFrame) -> pd.DataFrame:
    cost_rows = []
    for offer_file, source_sheet, sheet_group in iter_offer_sheet_groups(items_dataframe):
        cost_rows.append({
            "offer_file": offer_file,
            "source_sheet": source_sheet,
            "total_value": sum_total_price(sheet_group),
        })
    return pd.DataFrame(cost_rows)


def build_price_stats_table(items_dataframe: pd.DataFrame) -> list[PriceStatsRow]:
    price_stats_rows: list[PriceStatsRow] = []
    all_prices = items_dataframe["unit_price"].dropna()
    if len(all_prices):
        price_stats_rows.append(build_price_stats_row("all_offers", all_prices))
    for offer_file, offer_group in items_dataframe.groupby("offer_file"):
        offer_prices = offer_group["unit_price"].dropna()
        if len(offer_prices):
            price_stats_rows.append(build_price_stats_row(offer_file, offer_prices))
    return price_stats_rows


def build_top_items_by_total_table(items_dataframe: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    top_item_rows = []
    priced_items = items_dataframe[items_dataframe["total_price"].notna()].copy()
    for offer_file in priced_items["offer_file"].unique():
        offer_items = priced_items[priced_items["offer_file"] == offer_file].sort_values(
            "total_price", ascending=False
        ).head(limit)
        for _, item_row in offer_items.iterrows():
            top_item_rows.append({
                "offer_file": offer_file,
                "embed_text": truncate_text(str(item_row["embed_text"])),
                "total_price": float(item_row["total_price"]),
            })
    return pd.DataFrame(top_item_rows)


def build_data_quality_summary(items_dataframe: pd.DataFrame) -> DataQualitySummary:
    missing_unit_count = 0
    for _, _, sheet_group in iter_offer_sheet_groups(items_dataframe):
        missing_unit_count += count_missing_unit_rows(sheet_group)

    zero_price_count = int(
        ((items_dataframe["unit_price"] == 0) | (items_dataframe["total_price"] == 0)).sum()
    )
    return {
        "missing_unit_count": missing_unit_count,
        "missing_quantity_count": int(items_dataframe["quantity"].isna().sum()),
        "missing_unit_price_count": int(items_dataframe["unit_price"].isna().sum()),
        "missing_total_price_count": int(items_dataframe["total_price"].isna().sum()),
        "zero_price_count": zero_price_count,
        "inconsistent_total_count": count_inconsistent_total_rows(items_dataframe),
        "within_offer_duplicate_group_count": count_within_offer_duplicate_groups(items_dataframe),
    }


def build_item_distribution_summary(items_dataframe: pd.DataFrame) -> ItemDistributionSummary:
    text_counts = normalized_embed_text(items_dataframe).value_counts()
    return {
        "unique_embed_text_count": int((text_counts == 1).sum()),
        "repeated_embed_text_count": int((text_counts > 1).sum()),
    }


def build_comparability_summary(items_dataframe: pd.DataFrame) -> ComparabilitySummary:
    items_in_one_offer_only = 0
    items_in_multiple_offers = 0
    for _, text_group in items_dataframe.groupby(normalized_embed_text(items_dataframe)):
        if text_group["offer_file"].nunique() == 1:
            items_in_one_offer_only += 1
        else:
            items_in_multiple_offers += 1
    return {
        "items_in_one_offer_only": items_in_one_offer_only,
        "items_in_multiple_offers": items_in_multiple_offers,
    }


def build_distribution_comparability_by_offer_sheet_table(items_dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = normalized_embed_text(items_dataframe)
    offer_count_by_text = items_dataframe.groupby(normalized)["offer_file"].nunique()
    distribution_comparability_rows = []
    for offer_file, source_sheet, sheet_group in iter_offer_sheet_groups(items_dataframe):
        sheet_texts = normalized_embed_text(sheet_group)
        within_sheet_counts = sheet_texts.value_counts()
        shared_with_other_offers = 0
        offer_only_descriptions = 0
        for description_text in sheet_texts.unique():
            if offer_count_by_text[description_text] > 1:
                shared_with_other_offers += 1
            else:
                offer_only_descriptions += 1
        distribution_comparability_rows.append({
            "offer_file": offer_file,
            "source_sheet": source_sheet,
            "unique_descriptions": int(sheet_texts.nunique()),
            "repeated_descriptions": int((within_sheet_counts > 1).sum()),
            "shared_with_other_offers": shared_with_other_offers,
            "offer_only_descriptions": offer_only_descriptions,
        })
    return pd.DataFrame(distribution_comparability_rows)


def build_observations(
    component: str,
    summary_dataframe: pd.DataFrame,
    data_quality: DataQualitySummary,
    item_distribution: ItemDistributionSummary,
    comparability: ComparabilitySummary,
) -> list[str]:
    total_items = int(summary_dataframe["item_count"].sum())
    total_value = float(summary_dataframe["total_value"].sum())
    return [
        "Data analysis summary",
        f"- Component: {component}",
        f"- Offers: {summary_dataframe['offer_file'].nunique()}, sheets: {len(summary_dataframe)}, items: {total_items}",
        f"- Total value (where total_price filled): {total_value:.2f}",
        f"- Missing unit: {data_quality['missing_unit_count']}, missing quantity: {data_quality['missing_quantity_count']}, missing unit price: {data_quality['missing_unit_price_count']}",
        f"- Unique descriptions: {item_distribution['unique_embed_text_count']}, repeated: {item_distribution['repeated_embed_text_count']}",
        f"- Items in one offer only: {comparability['items_in_one_offer_only']}, in multiple offers: {comparability['items_in_multiple_offers']}",
    ]


def build_chart_data(
    summary_dataframe: pd.DataFrame,
    items_dataframe: pd.DataFrame,
    component: str,
    comparability: ComparabilitySummary,
) -> AnalysisChartData:
    offer_files = sorted(summary_dataframe["offer_file"].unique())
    source_sheets = sorted(summary_dataframe["source_sheet"].unique())
    series = []
    for source_sheet in source_sheets:
        sheet_rows = summary_dataframe[summary_dataframe["source_sheet"] == source_sheet]
        counts_by_offer = {
            row["offer_file"]: int(row["item_count"])
            for _, row in sheet_rows.iterrows()
        }
        series.append({
            "source_sheet": source_sheet,
            "item_counts": [counts_by_offer.get(offer_file, 0) for offer_file in offer_files],
        })

    unit_value_counts = items_dataframe["unit"].value_counts().head(15)
    total_values = [
        float(summary_dataframe[summary_dataframe["offer_file"] == offer_file]["total_value"].sum())
        for offer_file in offer_files
    ]
    unit_price_values = items_dataframe["unit_price"].dropna().tolist()

    return {
        "component": component,
        "items_per_offer": {
            "offer_files": list(offer_files),
            "series": series,
        },
        "description_lengths": items_dataframe["embed_text"].str.len().astype(int).tolist(),
        "unit_counts": {
            "units": unit_value_counts.index.tolist(),
            "counts": [int(value) for value in unit_value_counts.values],
        },
        "total_value_by_offer": {
            "offer_files": list(offer_files),
            "values": total_values,
        },
        "unit_price_histogram": [float(value) for value in unit_price_values],
        "comparability_counts": [
            comparability["items_in_one_offer_only"],
            comparability["items_in_multiple_offers"],
        ],
    }


def run_data_analysis_from_dataframe(items_dataframe: pd.DataFrame, component: str) -> DataAnalysisResponse:
    summary_dataframe = build_summary_by_offer_sheet_table(items_dataframe)
    quality_by_offer_sheet_dataframe = build_quality_by_offer_sheet_table(items_dataframe)
    data_quality = build_data_quality_summary(items_dataframe)
    item_distribution = build_item_distribution_summary(items_dataframe)
    comparability = build_comparability_summary(items_dataframe)
    distribution_comparability_by_offer_sheet_dataframe = build_distribution_comparability_by_offer_sheet_table(
        items_dataframe
    )
    chart_data = build_chart_data(summary_dataframe, items_dataframe, component, comparability)

    return {
        "item_count": len(items_dataframe),
        "observations": build_observations(
            component,
            summary_dataframe,
            data_quality,
            item_distribution,
            comparability,
        ),
        "summary_by_offer_sheet": cast(
            list[SummaryByOfferSheetRow],
            summary_dataframe.to_dict(orient="records"),
        ),
        "totals_by_offer": cast(
            list[TotalsByOfferRow],
            build_totals_by_offer_table(summary_dataframe).to_dict(orient="records"),
        ),
        "cost_by_offer": cast(
            list[CostByOfferRow],
            build_cost_by_offer_table(items_dataframe).to_dict(orient="records"),
        ),
        "cost_by_offer_sheet": cast(
            list[CostByOfferSheetRow],
            build_cost_by_offer_sheet_table(items_dataframe).to_dict(orient="records"),
        ),
        "price_stats": build_price_stats_table(items_dataframe),
        "top_items_by_total": cast(
            list[TopItemByTotalRow],
            build_top_items_by_total_table(items_dataframe).to_dict(orient="records"),
        ),
        "data_quality": data_quality,
        "quality_by_offer_sheet": cast(
            list[QualityByOfferSheetRow],
            quality_by_offer_sheet_dataframe.to_dict(orient="records"),
        ),
        "distribution_comparability_by_offer_sheet": cast(
            list[DistributionComparabilityByOfferSheetRow],
            distribution_comparability_by_offer_sheet_dataframe.to_dict(orient="records"),
        ),
        "chart_data": chart_data,
    }
