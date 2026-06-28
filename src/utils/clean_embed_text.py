import re
from stopwordsiso import stopwords


EMBED_TEXT_STOP_WORDS = frozenset(stopwords("hr"))


def clean_embed_text(embed_text: str) -> str:
    lowercased_text = embed_text.lower()
    without_punctuation = re.sub(r"[^\w\s]", " ", lowercased_text, flags=re.UNICODE)
    words = without_punctuation.split()
    cleaned_words = [word for word in words if word not in EMBED_TEXT_STOP_WORDS]
    return " ".join(cleaned_words)
