from typing import cast
import numpy as np
import pandas as pd
from config import SIMILARITY_THRESHOLD
from schemas import FlatItemDict, LabeledPairDict, OfferDict, ThresholdMetricsDict, ValidationResponse
from utils.embed_items import cosine_similarity, embed_texts
from utils.match_offers import match_offers_by_embedding_similarity


def flatten_offer_items_for_validation(offers: list[OfferDict]) -> list[FlatItemDict]:
    flat_items: list[FlatItemDict] = []
    for offer in offers:
        for item_index, item in enumerate(offer["items"]):
            flat_items.append({
                "offer_name": offer["name"],
                "embed_text": item["embed_text"],
                "vector": offer["vectors"][item_index],
            })
    return flat_items


def add_labeled_pair(
    pairs: list[LabeledPairDict],
    description_a: str,
    offer_a: str,
    description_b: str,
    offer_b: str,
    same_item: int | str,
    notes: str,
) -> None:
    pairs.append({
        "description_a": description_a,
        "offer_a": offer_a,
        "description_b": description_b,
        "offer_b": offer_b,
        "same_item": same_item,
        "notes": notes,
    })


def build_labeled_pairs_for_validation(offers: list[OfferDict]) -> pd.DataFrame:
    flat_items = flatten_offer_items_for_validation(offers)
    pairs: list[LabeledPairDict] = []

    for index_a, item_a in enumerate(flat_items):
        for item_b in flat_items[index_a + 1:]:
            if item_a["offer_name"] == item_b["offer_name"]:
                continue
            if item_a["embed_text"].lower().strip() == item_b["embed_text"].lower().strip():
                add_labeled_pair(
                    pairs,
                    item_a["embed_text"],
                    item_a["offer_name"],
                    item_b["embed_text"],
                    item_b["offer_name"],
                    1,
                    "exact cross-offer match",
                )

    template_rows = match_offers_by_embedding_similarity(offers)
    for template_row in template_rows:
        offer_names = list(template_row["offers"])
        if len(offer_names) < 2:
            continue
        add_labeled_pair(
            pairs,
            template_row["embed_text"],
            offer_names[0],
            template_row["embed_text"],
            offer_names[1],
            1,
            "merged at current threshold",
        )

    negative_target = max(20, 40 - len(pairs))
    negative_count = 0
    random_state = np.random.default_rng(42)
    for _ in range(2000):
        if negative_count >= negative_target:
            break
        item_a, item_b = random_state.choice(flat_items, size=2, replace=False)
        if item_a["offer_name"] == item_b["offer_name"]:
            continue
        similarity = cosine_similarity(item_a["vector"], item_b["vector"])
        if similarity >= 0.5:
            continue
        add_labeled_pair(
            pairs,
            item_a["embed_text"],
            item_a["offer_name"],
            item_b["embed_text"],
            item_b["offer_name"],
            0,
            f"auto negative sample (sim={similarity:.3f})",
        )
        negative_count += 1

    return pd.DataFrame(pairs)


def add_cosine_similarity_scores(labeled_pairs_dataframe: pd.DataFrame) -> pd.DataFrame:
    vectors_a = embed_texts(labeled_pairs_dataframe["description_a"].tolist())
    vectors_b = embed_texts(labeled_pairs_dataframe["description_b"].tolist())
    similarities = [
        cosine_similarity(vector_a, vector_b)
        for vector_a, vector_b in zip(vectors_a, vectors_b)
    ]
    scored_dataframe = labeled_pairs_dataframe.copy()
    scored_dataframe["cosine_similarity"] = similarities
    return scored_dataframe


def compute_threshold_metrics(scored_dataframe: pd.DataFrame, threshold: float) -> ThresholdMetricsDict:
    actual_same_item = scored_dataframe["same_item"] == 1
    predicted_same_item = scored_dataframe["cosine_similarity"] >= threshold

    true_positive = (predicted_same_item & actual_same_item).sum()
    false_positive = (predicted_same_item & ~actual_same_item).sum()
    false_negative = (~predicted_same_item & actual_same_item).sum()
    true_negative = (~predicted_same_item & ~actual_same_item).sum()

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (true_positive + true_negative) / len(scored_dataframe)

    return {
        "threshold": threshold,
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1_score), 4),
        "accuracy": round(float(accuracy), 4),
        "true_positive": int(true_positive),
        "false_positive": int(false_positive),
        "false_negative": int(false_negative),
        "true_negative": int(true_negative),
    }


def build_threshold_metrics_table(scored_dataframe: pd.DataFrame) -> pd.DataFrame:
    threshold_values = [round(value, 2) for value in np.arange(0.50, 0.96, 0.01)]
    return pd.DataFrame([compute_threshold_metrics(scored_dataframe, threshold) for threshold in threshold_values])


def choose_best_similarity_threshold(threshold_metrics_dataframe: pd.DataFrame) -> ThresholdMetricsDict:
    recall_ok = threshold_metrics_dataframe[threshold_metrics_dataframe["recall"] >= 0.5]
    if len(recall_ok) == 0:
        best_row = threshold_metrics_dataframe.sort_values("f1", ascending=False).iloc[0]
    else:
        best_row = recall_ok.sort_values(["precision", "threshold"], ascending=[False, False]).iloc[0]
    return {
        "threshold": float(best_row["threshold"]),
        "precision": float(best_row["precision"]),
        "recall": float(best_row["recall"]),
        "f1": float(best_row["f1"]),
        "accuracy": float(best_row["accuracy"]),
        "true_positive": int(best_row["true_positive"]),
        "false_positive": int(best_row["false_positive"]),
        "false_negative": int(best_row["false_negative"]),
        "true_negative": int(best_row["true_negative"]),
    }


def run_validation_from_offers(offers: list[OfferDict]) -> ValidationResponse:
    labeled_pairs_dataframe = build_labeled_pairs_for_validation(offers)
    scored_dataframe = add_cosine_similarity_scores(labeled_pairs_dataframe)
    threshold_metrics_dataframe = build_threshold_metrics_table(scored_dataframe)
    recommended_metrics = choose_best_similarity_threshold(threshold_metrics_dataframe)
    current_metrics = compute_threshold_metrics(scored_dataframe, SIMILARITY_THRESHOLD)

    same_item_scores = scored_dataframe[scored_dataframe["same_item"] == 1]["cosine_similarity"].round(4)
    different_item_scores = scored_dataframe[scored_dataframe["same_item"] == 0]["cosine_similarity"].round(4)

    return {
        "labeled_pair_count": len(scored_dataframe),
        "same_item_count": int((scored_dataframe["same_item"] == 1).sum()),
        "negative_pair_count": int((scored_dataframe["same_item"] == 0).sum()),
        "current_threshold": SIMILARITY_THRESHOLD,
        "current_metrics": current_metrics,
        "recommended_threshold": recommended_metrics["threshold"],
        "recommended_metrics": recommended_metrics,
        "threshold_metrics": cast(
            list[ThresholdMetricsDict],
            threshold_metrics_dataframe.to_dict(orient="records"),
        ),
        "chart_data": {
            "same_item_similarities": same_item_scores.tolist(),
            "different_item_similarities": different_item_scores.tolist(),
        },
    }
