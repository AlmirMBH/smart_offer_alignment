from collections.abc import Callable
import numpy as np
from schemas import VectorArray


def cosine_similarity(vector_a: VectorArray, vector_b: VectorArray) -> float:
    return float(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)))


def to_float_vector(vector: VectorArray | list[float]) -> VectorArray:
    return np.array(vector, dtype=np.float64)


def find_best_cosine_match(
    query_vector: VectorArray,
    candidate_vectors: list[VectorArray],
    should_compare: Callable[[int], bool] | None = None,
    skip_shape_mismatch: bool = True,
    minimum_similarity: float | None = None,
) -> tuple[int, float]:
    best_index = -1
    best_similarity = -1.0
    query_vector = to_float_vector(query_vector)
    for index, candidate_vector in enumerate(candidate_vectors):
        if should_compare is not None and not should_compare(index):
            continue
        candidate_vector = to_float_vector(candidate_vector)
        if skip_shape_mismatch and query_vector.shape != candidate_vector.shape:
            continue
        similarity = cosine_similarity(query_vector, candidate_vector)
        if minimum_similarity is not None:
            if similarity >= minimum_similarity and similarity > best_similarity:
                best_similarity = similarity
                best_index = index
        elif similarity > best_similarity:
            best_similarity = similarity
            best_index = index
    return best_index, best_similarity
