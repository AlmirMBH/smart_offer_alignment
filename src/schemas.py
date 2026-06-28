from typing import NotRequired, TypedDict
import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, Field


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


class AppSettingsValues(BaseModel):
    embedding_model: str = Field(description="Sentence-transformers model name")
    price_imputation_model: str = Field(description="Price imputation model name")
    preferred_websites: str = Field(description="Comma-separated URLs to prioritize for price search")
    similarity_threshold: float = Field(description="Item similarity for export matching")
    item_similarity_threshold_pricing: float = Field(description="Item similarity for pricing reference")
    pricing_similarity_threshold: int = Field(description="Price ±% for auto-approve")
    sheet_similarity_threshold: float = Field(description="Sheet name embedding match threshold")
    auto_approve_prices: bool = Field(description="Auto-approve imputed prices when gates pass")
    merge_export_when_unit_matches: bool = Field(
        description="Export merge requires matching quantity unit when enabled"
    )
    price_approvals_page_size: int = Field(description="Rows per page on Price Approvals tab", ge=1)


class SettingsGetResponse(AppSettingsValues):
    embedding_model_options: list[str] = Field(description="Selectable embedding model names")
    price_imputation_model_options: list[str] = Field(description="Selectable price imputation model names")


class PriceApprovalRow(BaseModel):
    offer_item_id: int = Field(description="offer_items.id")
    offer_name: str = Field(description="Uploaded offer file name")
    embed_text: str = Field(description="Item description used for embedding")
    unit: str = Field(description="Unit of measure")
    quantity: float = Field(description="Line quantity")
    unit_price: float | None = Field(description="Unit price")
    total_price: float | None = Field(description="Total price")
    source_sheet: str = Field(description="Excel sheet name")
    approved: bool = Field(description="Whether price is approved for export")
    auto_approved: bool = Field(description="Whether approved was set by ingest auto-approve gates")


class PriceApprovalsResponse(BaseModel):
    rows: list[PriceApprovalRow] = Field(description="All offer items for the component")


class OfferItemActionResponse(BaseModel):
    offer_item_id: int = Field(description="offer_items.id")
    approved: bool = Field(description="Updated approval flag")


class BulkOfferItemsApprovalRequest(BaseModel):
    offer_item_ids: list[int] = Field(description="offer_items.id values to update")
    approved: bool = Field(description="Approval flag to set on all listed items")


class BulkOfferItemsApprovalResponse(BaseModel):
    updated_count: int = Field(description="Number of offer_items rows updated")


class OfferItemUpdateRequest(BaseModel):
    offer_name: str = Field(description="Uploaded offer file name")
    embed_text: str = Field(description="Item description used for embedding")
    unit: str = Field(description="Unit of measure")
    quantity: float = Field(description="Line quantity")
    unit_price: float | None = Field(description="Unit price")
    total_price: float | None = Field(description="Total price")
    approved: bool = Field(description="Whether price is approved for export")


class OfferItemUpdateResponse(PriceApprovalRow):
    pass


class OfferItemDeleteResponse(BaseModel):
    offer_item_id: int = Field(description="Deleted offer_items.id")


SummaryRow = dict[str, str | float | int]
VectorArray = NDArray[np.float64]
