import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from schemas import ParsedItemDict, VectorArray


_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


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
