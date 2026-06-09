from typing import NotRequired, TypedDict
import numpy as np
from numpy.typing import NDArray


class ItemDict(TypedDict):
    source_sheet: str
    parent_description: str
    child_description: str
    unit: str
    quantity: float
    unit_price: float | None
    total_price: float | None
    offer_file: NotRequired[str]
    component: NotRequired[str]
    embed_text: NotRequired[str]


class ParsedItemDict(ItemDict):
    offer_file: str
    component: str
    embed_text: str


class ColumnMap(TypedDict):
    ordinal: str
    description: str | None
    unit: str | None
    quantity: str | None
    unit_price: str | None
    total_price: str | None


class OfferFieldsDict(TypedDict):
    unit: str
    quantity: float
    unit_price: float | None
    total_price: float | None
    source_sheet: str


class TemplateRow(TypedDict):
    embed_text: str
    component: str
    offers: dict[str, OfferFieldsDict]


class SheetScore(TypedDict):
    sheet_name: str
    embedding_score: float
    name_match: bool
    final_score: float


class SheetDetail(TypedDict):
    sheet_name: str
    item_count: int


class DetectionResult(TypedDict, total=False):
    status: str
    message: str
    sheets: list[str]
    sheet_scores: list[SheetScore]
    sheet_details: list[SheetDetail]
    item_count: int


class OfferDict(TypedDict):
    name: str
    items: list[ItemDict]
    vectors: NDArray[np.float64]


class FlatItemDict(TypedDict):
    offer_name: str
    embed_text: str
    vector: NDArray[np.float64]


class OfferListItem(TypedDict):
    id: int
    name: str
    uploaded_at: str


class UploadOfferResponse(TypedDict):
    offer_id: int
    offer_name: str
    component: str
    item_count: int
    sheets: list[str]


class SummaryByOfferSheetRow(TypedDict):
    offer_file: str
    source_sheet: str
    item_count: int
    total_value: float
    avg_embed_text_length: float


class TotalsByOfferRow(TypedDict):
    offer_file: str
    item_count: int
    total_value: float


class QualityByOfferSheetRow(TypedDict):
    offer_file: str
    source_sheet: str
    rows_without_unit: int
    rows_without_quantity: int
    rows_without_unit_price: int
    rows_without_total_price: int


class CostByOfferRow(TypedDict):
    offer_file: str
    total_value: float
    item_count: int


class CostByOfferSheetRow(TypedDict):
    offer_file: str
    source_sheet: str
    total_value: float


class PriceStatsRow(TypedDict):
    scope: str
    avg_unit_price: float
    min_unit_price: float
    max_unit_price: float


class TopItemByTotalRow(TypedDict):
    offer_file: str
    embed_text: str
    total_price: float


class DataQualitySummary(TypedDict):
    missing_unit_count: int
    missing_quantity_count: int
    missing_unit_price_count: int
    missing_total_price_count: int
    zero_price_count: int
    inconsistent_total_count: int
    within_offer_duplicate_group_count: int


class ItemDistributionSummary(TypedDict):
    unique_embed_text_count: int
    repeated_embed_text_count: int


class ComparabilitySummary(TypedDict):
    items_in_one_offer_only: int
    items_in_multiple_offers: int


class DistributionComparabilityByOfferSheetRow(TypedDict):
    offer_file: str
    source_sheet: str
    unique_descriptions: int
    repeated_descriptions: int
    shared_with_other_offers: int
    offer_only_descriptions: int


class ItemsPerOfferSeries(TypedDict):
    source_sheet: str
    item_counts: list[int]


class ItemsPerOfferChart(TypedDict):
    offer_files: list[str]
    series: list[ItemsPerOfferSeries]


class UnitCountsChart(TypedDict):
    units: list[str]
    counts: list[int]


class TotalValueByOfferChart(TypedDict):
    offer_files: list[str]
    values: list[float]


class AnalysisChartData(TypedDict):
    component: str
    items_per_offer: ItemsPerOfferChart
    description_lengths: list[int]
    unit_counts: UnitCountsChart
    total_value_by_offer: TotalValueByOfferChart
    unit_price_histogram: list[float]
    comparability_counts: list[int]


class DataAnalysisResponse(TypedDict):
    item_count: int
    observations: list[str]
    summary_by_offer_sheet: list[SummaryByOfferSheetRow]
    totals_by_offer: list[TotalsByOfferRow]
    cost_by_offer: list[CostByOfferRow]
    cost_by_offer_sheet: list[CostByOfferSheetRow]
    price_stats: list[PriceStatsRow]
    top_items_by_total: list[TopItemByTotalRow]
    data_quality: DataQualitySummary
    quality_by_offer_sheet: list[QualityByOfferSheetRow]
    distribution_comparability_by_offer_sheet: list[DistributionComparabilityByOfferSheetRow]
    chart_data: AnalysisChartData


class LabeledPairDict(TypedDict):
    description_a: str
    offer_a: str
    description_b: str
    offer_b: str
    same_item: int | str
    notes: str


class ThresholdMetricsDict(TypedDict):
    threshold: float
    precision: float
    recall: float
    f1: float
    accuracy: float
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int


class ValidationChartData(TypedDict):
    same_item_similarities: list[float]
    different_item_similarities: list[float]


class ValidationResponse(TypedDict):
    labeled_pair_count: int
    same_item_count: int
    negative_pair_count: int
    current_threshold: float
    current_metrics: ThresholdMetricsDict
    recommended_threshold: float
    recommended_metrics: ThresholdMetricsDict
    threshold_metrics: list[ThresholdMetricsDict]
    chart_data: ValidationChartData


SummaryRow = dict[str, str | float | int]
VectorArray = NDArray[np.float64]
