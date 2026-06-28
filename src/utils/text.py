def truncate_text(text: str, max_length: int = 80) -> str:
    return text[:max_length]


def is_blank_or_nan_text(text: str) -> bool:
    stripped_text = str(text).strip()
    return not stripped_text or stripped_text.lower() == "nan"
