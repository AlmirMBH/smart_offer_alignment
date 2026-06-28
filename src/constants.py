import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

EMBEDDING_MODEL_OPTIONS = (
    "paraphrase-multilingual-MiniLM-L12-v2",
    "paraphrase-multilingual-mpnet-base-v2",
    "distiluse-base-multilingual-cased-v2",
    "intfloat/multilingual-e5-small",
)

PRICE_IMPUTATION_MODEL_OPTIONS = (
    "paraphrase-multilingual-MiniLM-L12-v2",
    "paraphrase-multilingual-mpnet-base-v2",
    "distiluse-base-multilingual-cased-v2",
    "intfloat/multilingual-e5-small",
)

DEFAULT_PREFERRED_WEBSITES = "https://www.emajstor.hr/cijene/vodoinstalacije"

PRICE_IMPUTATION_MIN_CATALOG_SIMILARITY = 0.30

WEB_FETCH_TIMEOUT_SECONDS = 30
# Some sites return 403 for bot-like User-Agent strings. A browser User-Agent avoids that.
WEB_FETCH_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

COMPONENT_LABELS = {
    "piping": [
        "piping",
        "ViK",
        "VIO",
        "vodovod i odvodnja",
        "vodoinstalaterski radovi",
        "hidroinstalacije",
    ],
    "electro": [
        "electro",
        "elektro",
        "E ELEKTRO",
        "XIX. ELEKTRO",
        "Elektroinstalacije",
        "elektroinstalacije",
        "električne instalacije",
    ],
}

COMPONENT_ITEM_KEYWORDS = {
    "piping": (
        "voda", "vodovod", "odvod", "kanaliz", "cijev", "sifon", "ventil",
        "sanitarn", "instalacij", "perilic", "sudoper", "kupaonic", "vodoinstal",
    ),
    "electro": (
        "kabel", "elektro", "elektri", "utičnic", "prekidač", "razvod", "ormar",
        "svjetil", "instalacij", "napajan", "faz", "nul", "uzemlj",
    ),
}

COMPONENT_SHEET_PATTERNS = {
    "piping": (
        re.compile(r"vi[kc]", re.IGNORECASE),
        re.compile(r"vio", re.IGNORECASE),
    ),
    "electro": (
        re.compile(r"elektro", re.IGNORECASE),
        re.compile(r"^\s*e\s+elektro", re.IGNORECASE),
        re.compile(r"xix.*elektro", re.IGNORECASE),
    ),
}

COMPONENT_ROW_FILTER_SHEETS = {
    "piping": ("TROŠKOVNIK",),
    "electro": (),
}

SKIP_SHEET_KEYWORDS = (
    "rekap", "nasl", "uvjet", "opć", "opc", "program", "sveukup", "ou_", "ou ", "ou.",
)
