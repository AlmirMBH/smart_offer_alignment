import pandas as pd
from sqlalchemy.orm import Session
from repositories.data_analysis import RepositoryDataAnalysis
from schemas import DataAnalysisResponse
from utils.eda import run_data_analysis_from_dataframe


class ServiceDataAnalysis:
    repository_data_analysis: RepositoryDataAnalysis

    def __init__(self, db: Session) -> None:
        self.repository_data_analysis = RepositoryDataAnalysis(db)

    def run_data_analysis_by_component(self, component: str) -> DataAnalysisResponse | None:
        offer_item_rows = self.repository_data_analysis.get_offer_item_rows_by_component(component)
        if not offer_item_rows:
            return None
        items_dataframe = pd.DataFrame(offer_item_rows)
        return run_data_analysis_from_dataframe(items_dataframe, component)
