import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from schemas import ParsedItemDict, VectorArray


_embedding_model: SentenceTransformer | None = None
_active_embedding_model_name: str | None = None
_pending_embedding_model_name: str | None = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model, _active_embedding_model_name, _pending_embedding_model_name
    model_name = _pending_embedding_model_name or _active_embedding_model_name or EMBEDDING_MODEL
    if _embedding_model is None or _active_embedding_model_name != model_name:
        _embedding_model = SentenceTransformer(model_name)
        _active_embedding_model_name = model_name
        _pending_embedding_model_name = None
    return _embedding_model


def schedule_embedding_model_reload(embedding_model_name: str) -> None:
    global _embedding_model, _active_embedding_model_name, _pending_embedding_model_name
    if _active_embedding_model_name == embedding_model_name and _embedding_model is not None:
        return
    _embedding_model = None
    _active_embedding_model_name = None
    _pending_embedding_model_name = embedding_model_name


def embedding_dimensions() -> int:
    return get_embedding_model().get_sentence_embedding_dimension()


def embed_texts(texts: list[str]) -> VectorArray:
    if not texts:
        return np.array([])
    return get_embedding_model().encode(texts, show_progress_bar=False)


def cosine_similarity(vector_a: VectorArray, vector_b: VectorArray) -> float:
    return float(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)))


def embed_items(items: list[ParsedItemDict]) -> tuple[list[ParsedItemDict], VectorArray]:
    texts = [item["embed_text"] for item in items]
    vectors = embed_texts(texts)
    return items, vectors


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