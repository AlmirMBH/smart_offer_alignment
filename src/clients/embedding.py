import numpy as np
from sentence_transformers import SentenceTransformer
from schemas import VectorArray

_models_by_name: dict[str, SentenceTransformer] = {}


def _load_model(model_name: str) -> SentenceTransformer:
    if model_name not in _models_by_name:
        _models_by_name[model_name] = SentenceTransformer(model_name)
    return _models_by_name[model_name]


def encode_texts(model_name: str, texts: list[str]) -> VectorArray:
    if not texts:
        return np.array([])
    return _load_model(model_name).encode(texts, show_progress_bar=False)


def load_embedding_model(model_name: str) -> None:
    _load_model(model_name)


def clear_model_cache(model_name: str) -> None:
    _models_by_name.pop(model_name, None)


# MODELS
# In this project, we tested several embedding models, including:
# - paraphrase-multilingual-MiniLM-L12-v2
# - paraphrase-multilingual-MiniLM-L6-v2
#
# The difference between these models is the number of transformer layers.
# - paraphrase-multilingual-MiniLM-L12-v2 has 12 layers
# - paraphrase-multilingual-MiniLM-L6-v2 has 6 layers
#
# The number of layers is the depth of the encoder. Each layer refines the text
# representation once more, so more layers usually give better semantic quality
# but slower encoding. Both models still output 384-dimensional vectors.
#
# DATASETS
# Our assumption was that we should take the datasets as they are, and not isolate them
# as that might mean a lot of manual work in case of larege amount of data.
# The price imputation tool was used to impute the approximate prices from online
# sources and they require manual validation before the data is inserted into the database.
# We automated this process to accept all the estimated prices that are within a customizable
# range and require validation if this option is not turned on or the price is outside the
# range (market might not be stable).
#
# IMPUTATION MODEL
# The prices and quantites for the datasets were taken mostly from
# https://www.emajstor.hr/cijene/vodoinstalacije. This site provides a
# an approximate calculator for the prices of the items.
#
# TODO:
# remove stop words and punctuation, special characters, etc.
# enforce rule-based merging e.g. if quantity unit is the same, then merge the items
# see how to remove special characters and non-alphanumeric characters from the output
# see similarity between the items in different datasets and check if they are similar manually
# write report and poster, there are exports for different models on desktop
# explain
# why different models and why they give different results
# manually validate the results and write report and poster
# see what else needs to be done from plan.txt
# update readme
