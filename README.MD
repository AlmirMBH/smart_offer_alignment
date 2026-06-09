# Pricelist Comparison Tool

This project compares Excel cost sheets (troskovnici) by aligning line items across contractor offers. The user uploads Excel files with a component label (for example `piping` or `electro`). The app detects the relevant sheets, parses rows, embeds item descriptions, matches similar items with cosine similarity, and exports one comparison CSV with all offers side by side.

The implementation is the practical part of the **CDA/MLRP** course project. The report and poster describe the domain analysis, EDA, embedding model choice, threshold validation, and results.

---

## 1) Project Background

This is a course project for **CDA/MLRP** at the Faculty of Electrical Engineering, University of Sarajevo. The supervisor is **Aida Brankovic**.

The goal is to help procurement compare multiple contractor offers in one table: same item on one row, each offer in its own columns (unit, quantity, unit price, total price). Items that appear in only one offer keep empty cells for the other offers.

The pipeline is developed and validated on **piping** data (ViK/ViO sheets). Component-specific rules live in `constants.py` (`piping` and starter `electro` entries). Matching is scoped by component so piping items never merge with electro items.

### Accompanying deliverables

- **Report** — Nature Scientific Reports style (~5–6 pages): domain understanding, methods, EDA, validation, results, discussion, conclusion.
- **Poster** — course template.
- **This repository** — FastAPI backend and web UI.

---

## 2) Technologies

| Library | Role |
| -------- | ----- |
| Python 3 | Implementation language |
| pandas, openpyxl, xlrd | Excel loading and CSV export |
| sentence-transformers | Local multilingual embeddings |
| NumPy | Cosine similarity |
| FastAPI, uvicorn | REST API and UI server |
| SQLAlchemy, Alembic | Database models and migrations |
| SQLite / PostgreSQL | Database (SQLite default) |
| Plotly.js | EDA and validation charts in the browser (CDN) |
| python-dotenv | Load settings from `.env` |

All Python dependencies are listed in `requirements.txt`.

---

## 3) Project Setup

### Dataset

Place the course Excel files in `cda_and_mlpr_project_datasets/` at the project root. **Do not commit or share these files publicly.**

Expected piping files for development:

| File | Piping sheet(s) |
| ---- | ---------------- |
| 1 Troskovnik.xls | XVII. VIK |
| 2 Troskovnik.xls | TROŠKOVNIK (piping rows only) |
| 3 Troskovnik.xlsx | C VIK |
| 4 Troskovnik.xls | ViK (empty) |
| 5 Troskovnik.xlsx | none (fasada only) |
| 6 Troškovnik.xlsx | 3. VANJSKI ViO + 5. UNUTARNJI VIO (one offer) |
| 8 troskovnik.xlsx | none (electro only) |

There is no file 7 in the provided dataset.

### Virtual environment

From the project root (`cda_mlrp/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust settings if needed.

On first run, `sentence-transformers` downloads the embedding model from Hugging Face (public model, no API key required).

### Run the web app

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn main:app --reload
```

Open http://127.0.0.1:8000/

**Comparison tab**

1. Choose component (`piping` or `electro`).
2. Upload Excel troskovnici one by one.
3. Click **Download comparison CSV**.

**Data Analysis tab**

1. Click **Run data analysis** for pre-modeling summaries, tables, and a Plotly dashboard.

**Validation tab**

1. Upload at least 2 offers, then click **Run validation** for threshold metrics and charts.
2. Change `SIMILARITY_THRESHOLD` in `.env` based on the recommended value (read-only in UI).

If a file has no sheet for the requested component, the UI shows an error message and nothing is stored.

---

## 4) Project Structure

```
cda_mlrp/
├── alembic/
│   └── env.py
├── cda_and_mlpr_project_datasets/   # local only, not in git
├── frontend/
│   └── index.html
├── outputs/                         # comparison CSV, gitignored
├── uploads/                         # temp uploads, gitignored
├── src/
│   ├── main.py
│   ├── config.py                    # .env settings (database, thresholds, model)
│   ├── constants.py                 # paths, component rules, keywords
│   ├── schemas.py                   # TypedDicts for API and pipeline data
│   ├── routes/                      # HTTP entry points
│   │   ├── home.py
│   │   ├── upload_offer.py
│   │   ├── list_offers.py
│   │   ├── export_summary.py
│   │   ├── data_analysis.py
│   │   └── validation.py
│   ├── services/                    # business logic (one service per route, with repository)
│   │   ├── upload_offer.py
│   │   ├── list_offers.py
│   │   └── export_summary.py
│   ├── repositories/                # database access
│   │   ├── base_repository.py
│   │   ├── upload_offer.py
│   │   ├── list_offers.py
│   │   └── export_summary.py
│   ├── utils/                       # pure logic (no database access)
│   │   ├── find_component_sheets.py
│   │   ├── load_excel.py
│   │   ├── parse_items.py
│   │   ├── extract_offer.py
│   │   ├── embed_items.py
│   │   ├── match_offers.py
│   │   ├── export_summary.py
│   │   ├── eda.py
│   │   └── validate_threshold.py
│   └── db/
│       ├── models.py
│       └── session.py
├── .env.example
├── alembic.ini
├── plan.txt
├── project_task.txt
└── requirements.txt
```

### Architecture

- **Routes** call **services** (when a flow has its own repository) or orchestrate **services + utils**.
- **Services** always have a dedicated **repository**; they may call other services for cross-flow data.
- **Repositories** are the only database access layer.
- **Utils** contain pure logic and never touch the database.

### Layered backend

Routes, services, and repositories use **matching names** per flow (e.g. `upload_offer`) so the stack is easy to follow. Services call their repository for DB access and other services when a flow needs cross-cutting data — logic stays in one place instead of scattered duplicates.

### Typing

Functions use **TypedDict** argument and return types in `schemas.py` so each step’s inputs and outputs are explicit when reading the code.

### Naming

Variables and functions use **full descriptive names** (no abbreviations) to keep the pipeline readable without extra comments.

### Web UI

Three tabs:

- **Comparison** — upload offers and download the side-by-side CSV.
- **Data Analysis** — pre-modeling structure, quality, distribution, comparability, and charts.
- **Validation** — threshold metrics and confusion-matrix / similarity charts.

---

## 5) Configuration

Settings are loaded from `.env` via `config.py`. Static app values (paths, component keywords, sheet patterns) are in `constants.py`.

| Setting | Description |
| -------- | ----------- |
| `DATABASE_ENGINE` | `sqlite` (default) or `postgresql` |
| `SQLITE_DATABASE_PATH` | SQLite file path (default `./app.db`) |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | PostgreSQL connection parts (required when `DATABASE_ENGINE=postgresql`) |
| `EMBEDDING_MODEL` | Hugging Face sentence-transformers model (default `paraphrase-multilingual-MiniLM-L12-v2`) |
| `SIMILARITY_THRESHOLD` | Item match cutoff for cosine similarity (default `0.85`) |
| `SHEET_SIMILARITY_THRESHOLD` | Fallback embedding cutoff for sheet detection (default `0.75`) |

To switch to PostgreSQL, set `DATABASE_ENGINE=postgresql` and fill in the `POSTGRES_*` variables in `.env`. Do not pass a full database URL.

---

## 6) Pipeline Overview

### Sheet detection

`find_component_sheets()` reads sheet names and picks component-related sheets using name patterns and embedding scores from `constants.py` (per-component labels, patterns, and keywords).

### Item extraction

Each row is parsed into:

- `parent_description`, `child_description`
- `unit`, `quantity`, `unit_price`, `total_price`
- `source_sheet`

Embed/match text is built in code as `parent_description + child_description`.

Prices are read from Excel. Empty or zero prices stay blank. Total or unit price is calculated only when the other value and quantity exist.

### Matching

For each new item, the app computes cosine similarity against existing items with the **same component**. If the best score is at or above `SIMILARITY_THRESHOLD`, the item is attached to that template row. Otherwise a new row is created.

### Export

The final deliverable is **one CSV** named `troskovnik_DD_MM_YYYY.csv` with columns:

`item | offer1_unit | offer1_qty | offer1_unit_price | offer1_total | offer2_unit | ...`

A `UKUPNO` row sums totals per offer where prices exist.

---

## 7) API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/` | Web UI |
| `POST` | `/upload` | Upload Excel + component → detect, parse, match, save to DB |
| `GET` | `/offers?component=piping` | List loaded offers |
| `GET` | `/summary?component=piping` | Download comparison CSV |
| `GET` | `/data-analysis?component=piping` | Pre-modeling data analysis — structure, cost, quality, distribution, comparability + Plotly dashboard |
| `GET` | `/validation?component=piping` | Run threshold validation — JSON with metrics and chart series (needs 2+ offers) |

Upload errors (no component sheet, empty sheet) return HTTP 400 with a clear message.

---

## 8) Database

SQLite is the default for local demo. PostgreSQL is supported via split env variables (see section 5).

| Table | Role |
| ----- | ---- |
| `offers` | One row per uploaded file |
| `items` | Template items with embedding vector |
| `offer_items` | Offer-specific unit, quantity, prices, descriptions |

Tables are created on app startup. Alembic is available for migrations:

```bash
PYTHONPATH=src alembic upgrade head
```

---

## 9) Validation

The **Validation** tab calls `GET /validation`, which loads offers from the DB and runs `utils/validate_threshold.py` on demand. It returns labeled-pair counts, current vs recommended threshold metrics, and series for a Plotly precision/recall/f1 chart. Results are not saved to disk. Set `SIMILARITY_THRESHOLD` in `.env` manually; the comparison export uses that value on every upload.

---

## 10) Application Flow

```
Web UI (frontend/index.html)
  ├── Comparison tab
  │     ├── POST /upload
  │     │     ├── find_component_sheets()
  │     │     ├── extract_offer_items_from_excel_file()
  │     │     ├── embed_items()
  │     │     └── ServiceUploadOffer → RepositoryUploadOffer → DB
  │     ├── GET /offers
  │     └── GET /summary
  │           ├── ServiceExportSummary → DB
  │           └── write_summary_csv() → troskovnik_DD_MM_YYYY.csv
  └── Data Analysis tab
        └── GET /data-analysis → run_data_analysis_from_dataframe() → JSON + 2×2 Plotly dashboard
  └── Validation tab
        └── GET /validation → run_validation_from_offers() → JSON + Plotly metrics chart
```

---

## 11) Known Limitations

- Sheet detection rules are tuned on the course piping dataset; `electro` has starter constants that may need tuning with real electro sheets.
- Most source files have no unit prices filled in; comparison CSV shows quantities and units but often blank price columns.
- The embedding model is downloaded on first use (~420 MB); first upload is slower.
- This is a coursework demo, not a production procurement system.
- Course Excel data must stay private and out of version control.

---

## Contact

**Almir Mustafic** — project author.

Team context: similar electro comparison may be developed in parallel (see `project_task.txt`).

---

## License

This project is released under the MIT License.

---

## Acknowledgments

Embedding model: [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) (sentence-transformers).

**Aida Brankovic** supervised the course project.

---

## Disclaimer

The troskovnik Excel datasets are provided for coursework only. They must not be committed to public repositories or shared outside the course. This tool was built for **CDA/MLRP** and is intended for local academic use.
