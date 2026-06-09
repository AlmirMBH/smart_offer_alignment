import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATASET_DIR = PROJECT_ROOT / "cda_and_mlpr_project_datasets"

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

CSV_COLUMNS = (
    "source_sheet",
    "embed_text",
    "unit",
    "quantity",
    "unit_price",
    "total_price",
)
