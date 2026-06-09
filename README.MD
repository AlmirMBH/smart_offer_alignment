# Smart Offer Alignment

This project compares Excel cost sheets by aligning line items across contractor offers. The user uploads Excel files with a component label (`piping` or `electro`). The app detects sheets, parses rows, embeds item descriptions, matches items with cosine similarity, and exports one comparison CSV with all offers side by side.

---

## Project Background

This is a course project for **Computational Data Analytics/Machine Learning: Pattern Recognition** at the Faculty of Electrical Engineering, University of Sarajevo. The supervisor is **Prof. Aida Brankovic**.

The goal is to help procurement compare contractor offers in one table. Same item on one row, each offer in its own columns (unit, quantity, unit price, total price). Items that appear in only one offer keep empty cells for the other offers.

The pipeline is developed and validated on **piping** (ViK/ViO sheets) and **electro** data. Component rules live in `constants.py`. Matching is scoped by component so piping items never merge with electro items.

### Accompanying deliverables

- **Report** — Nature Scientific Reports style (5–6 pages). Covers domain understanding, methods, EDA, validation, results, discussion, and conclusion.
- **Poster** — template.
- **This repository** — FastAPI backend and web UI with upload, EDA, and validation.

---

## Technologies

| | Role |
| -------- | ----- |
| Python 3 | Implementation language |
| pandas, openpyxl, xlrd | Excel loading and CSV export |
| sentence-transformers | Multilingual embeddings |
| NumPy | Cosine similarity |
| FastAPI, uvicorn | REST API and UI server |
| SQLAlchemy, Alembic | Database models and migrations |
| SQLite / PostgreSQL | Database (SQLite default) |
| Plotly.js | EDA and validation charts in the browser (CDN) |
| python-dotenv | Load settings from `.env` |

All Python dependencies are listed in `requirements.txt`.

---

## Project Setup

### Dataset

Datasets are provided by the course professor. They are not publicly available.

### First run behavior

On startup the app creates database tables, the `uploads/` and `outputs/` folders, and loads the embedding model. The first startup downloads the model from Hugging Face (~420 MB). No API key is required. The model stays in memory for later uploads in the same session.

### Virtual environment

From the project root (`smart_offer_alignment/`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Default values are enough for a local run.

### Run the web app

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn main:app --reload
```

Open http://127.0.0.1:8000/

---

## Example Workflow

1. Copy `.env.example` to `.env` and start the server.
2. Open the Comparison tab, choose `piping` or `electro`, and upload at least two files for that component.
3. Open the Validation tab and click **Run validation**. Note the recommended threshold.
4. Set `SIMILARITY_THRESHOLD` in `.env` to the recommended value and restart the server if you change it.
5. Re-upload offers if you changed the threshold after the first upload.
6. Open the Comparison tab and click **Download comparison CSV**.
7. Open the Data Analysis tab and click **Run data analysis** to inspect structure, quality, and comparability.

---

## Project Structure

```
smart_offer_alignment/
├── alembic/
│   └── env.py
├── frontend/
│   └── index.html
├── outputs/                         # comparison CSV, gitignored
├── uploads/                         # gitignored
├── src/
│   ├── main.py
│   ├── config.py                    # .env settings
│   ├── constants.py                 # component rules
│   ├── schemas.py                   # TypedDicts
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── utils/
│   └── db/
├── .env.example
└── alembic.ini
```

---

## Source Code Readability

The backend follows a fixed layer order.

- **Routes** receive HTTP requests and call services or utils.
- **Services** contain flow logic and call repositories.
- **Repositories** are the only database access layer.
- **Utils** contain pure logic and never touch the database.

Routes, services, and repositories share the same name per flow (for example `upload_offer`). Functions use **TypedDict** types from `schemas.py` for arguments and return values. Variables and functions use full names without abbreviations.

---

## Configuration

Settings are loaded from `.env` via `config.py`. Component labels, sheet patterns, and item keywords are in `constants.py`.

| Setting | Description |
| -------- | ----------- |
| `DATABASE_ENGINE` | `sqlite` (default) or `postgresql` |
| `SQLITE_DATABASE_PATH` | SQLite file path (default `./app.db`) |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | PostgreSQL connection parts (required when `DATABASE_ENGINE=postgresql`) |
| `EMBEDDING_MODEL` | Hugging Face sentence-transformers model (default `paraphrase-multilingual-MiniLM-L12-v2`) |
| `SIMILARITY_THRESHOLD` | Item match cutoff for cosine similarity (default `0.85`) |
| `SHEET_SIMILARITY_THRESHOLD` | Embedding cutoff for sheet detection when name patterns do not match (default `0.75`) |

To switch to PostgreSQL, set `DATABASE_ENGINE=postgresql` and fill in the `POSTGRES_*` variables in `.env`.

---

## Component Configuration

Each component entry in `constants.py` defines four rule groups.

| Rule group | Role |
| ---------- | ---- |
| `COMPONENT_LABELS` | Text labels embedded and compared against sheet names |
| `COMPONENT_SHEET_PATTERNS` | Regex patterns that mark a sheet as a name match |
| `COMPONENT_ITEM_KEYWORDS` | Keywords used to filter rows on mixed sheets |
| `COMPONENT_ROW_FILTER_SHEETS` | Sheet names where row filtering by keywords is enabled |

**Piping** uses ViK/ViO name patterns and plumbing-related keywords. The sheet `TROŠKOVNIK` uses row filtering so only piping rows are kept.

**Electro** uses elektro name patterns and electrical keywords. Row filtering is not enabled on a named sheet.

Sheets whose names contain rekap, naslov, uvjet, program, or similar keywords are skipped.

---

## Sheet Detection

`find_component_sheets()` in `utils/find_component_sheets.py` runs on every upload.

1. Read all sheet names from the workbook.
2. Skip sheets that match `SKIP_SHEET_KEYWORDS`.
3. Score each remaining sheet. A regex name match sets `final_score` to 1.0. Otherwise the score is the max cosine similarity between the sheet name and `COMPONENT_LABELS`.
4. Select sheets with a name match. If none match, select sheets with `embedding_score` at or above `SHEET_SIMILARITY_THRESHOLD`.
5. Parse each selected sheet and drop sheets with zero usable rows.

If no sheet passes step 4, the upload returns HTTP 400 with a no-component message. If every selected sheet has zero rows, the upload returns HTTP 400 with an empty-sheet message.

---

## Embedding Model

The app uses [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) through `sentence-transformers`. Override with `EMBEDDING_MODEL` in `.env`.

- **Model** — Multilingual MiniLM encoder for semantic similarity.
- **Why it is selected** — Item descriptions use local languages and different wording across contractors. The model covers Bosnian, Croatian, and Serbian and runs locally without an API key.
- **Embedding type** — Dense sentence embeddings. Each description maps to one numeric vector.
- **Dimensions** — 384.

---

## Matching Approach

Exact text match fails when contractors use different wording for the same item. The app embeds `parent_description` plus `child_description` and compares vectors with cosine similarity.

For each new item the app searches template items with the same component. If the best score is at or above `SIMILARITY_THRESHOLD`, the item joins that template row. Otherwise the app creates a new template row. Matching never crosses components.

---

## Pipeline Overview

### Item extraction

Each row is parsed into `parent_description`, `child_description`, `unit`, `quantity`, `unit_price`, `total_price`, and `source_sheet`. Match text is `parent_description + child_description`.

Prices are read from Excel. Empty or zero prices stay blank. Total or unit price is calculated only when the other value and quantity exist.

---

## EDA

The Data Analysis tab calls `GET /data-analysis`. The route loads all items for the selected component from the database and runs `utils/eda.py`.

The response includes tables and a 2×2 Plotly dashboard.

| Output | Content |
| ------ | ------- |
| Structure | Item counts and total value by offer and sheet |
| Cost | Totals by offer, by offer and sheet, price stats, top items by total |
| Quality | Missing unit, quantity, unit price, total price, inconsistent totals, within-offer duplicates |
| Distribution | Unique and repeated descriptions per offer and sheet |
| Comparability | Descriptions in one offer only vs shared across offers |
| Charts | Items per offer by sheet, description length, unit counts, total value by offer, unit price histogram, comparability counts |

EDA runs on demand and does not write files to disk.

---

## Evaluation

The Validation tab calls `GET /validation` with at least two uploaded offers. The route runs `utils/validate_threshold.py`.

### Labeled pairs

Positive pairs come from exact cross-offer description matches and from items merged at the current threshold. Negative pairs are sampled randomly from pairs with cosine similarity below 0.5.

### Metrics

For each threshold from 0.50 to 0.95 the app computes precision, recall, F1, and accuracy from predicted matches vs labeled pairs.

The recommended threshold is the value with recall at or above 0.5 and the highest precision. If none meet recall 0.5, the app picks the highest F1.

The UI shows metrics at the current `SIMILARITY_THRESHOLD` and at the recommended value, plus similarity histograms for same-item and different-item pairs. Update `.env` manually and restart the server to apply a new threshold.

---

## Results

Metrics depend on the offers loaded in the database. Run Validation after upload to get numbers for your session.

| Output | Meaning |
| ------ | ------- |
| Comparison CSV | One row per matched item, one column group per offer |
| Current threshold metrics | Precision, recall, F1, and accuracy at `SIMILARITY_THRESHOLD` |
| Recommended threshold metrics | Best trade-off from the threshold sweep |
| Labeled pair counts | Positive and negative pairs used in evaluation |

On course piping and electro data, semantic matching aligns items that differ in wording but refer to the same work. Most source files have blank unit prices, so totals in the CSV are often empty even when quantities match.

---

## Output Files

| Path | Role |
| ---- | ---- |
| `outputs/troskovnik_DD_MM_YYYY_HH_MM_SS.csv` | Comparison export from **Download comparison CSV** |
| `uploads/` | Temporary upload storage during POST `/upload` (file deleted after processing) |
| `app.db` | SQLite database (default path from `.env`) |

The comparison CSV has an `item` column plus `{offer}_unit`, `{offer}_qty`, `{offer}_unit_price`, and `{offer}_total` for each uploaded file. Column prefixes come from the Excel filename stem. The last row is `UKUPNO` with per-offer total sums where prices exist.

---

## Database Schema

SQLite is the default. PostgreSQL is supported through the `POSTGRES_*` variables in `.env`.

| Table | Role |
| ----- | ---- |
| `offers` | One row per uploaded file (`name`, `component`, `uploaded_at`) |
| `items` | One row per template item (`component`, `embed_text`, `embedding`) |
| `offer_items` | One row per item in an offer (`offer_id`, `item_id`, `source_sheet`, `unit`, `quantity`, `unit_price`, `total_price`) |

Relationships.

- One `offers` row links to many `offer_items` rows.
- One `items` row links to many `offer_items` rows when the same template item appears in multiple offers.
- Template items and embeddings are shared across offers through `items`.

Tables are created on app startup. Alembic migrations are in `alembic/versions/`.

```bash
PYTHONPATH=src alembic upgrade head
```

---

## API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/` | Web UI |
| `POST` | `/upload` | Upload Excel and component, detect sheets, parse, match, save to DB |
| `GET` | `/offers?component=piping` | List loaded offers |
| `GET` | `/summary?component=piping` | Download comparison CSV |
| `GET` | `/data-analysis?component=piping` | EDA JSON and Plotly chart data |
| `GET` | `/validation?component=piping` | Threshold validation JSON and chart data (needs 2+ offers) |

Upload errors return HTTP 400 with a message.

---

## Application Flow

```
Web UI (frontend/index.html)
  ├── Comparison tab
  │     ├── POST /upload
  │     │     ├── find_component_sheets()
  │     │     ├── extract_offer_items_from_excel_file()
  │     │     ├── embed_items()
  │     │     └── ServiceUploadOffer -> RepositoryUploadOffer -> DB
  │     ├── GET /offers
  │     └── GET /summary
  │           ├── ServiceExportSummary -> DB
  │           └── write_summary_csv() -> troskovnik_DD_MM_YYYY_HH_MM_SS.csv
  ├── Data Analysis tab
  │     └── GET /data-analysis -> run_data_analysis_from_dataframe()
  └── Validation tab
        └── GET /validation -> run_validation_from_offers()
```

---

## Troubleshooting

| Problem | Cause | Action |
| ------- | ----- | ------ |
| HTTP 400, no component sheet | Workbook has no sheet for the selected component | Check component choice and sheet names |
| HTTP 400, empty sheet | Sheet matched but has no usable rows | Check row content and component keywords |
| Validation tab shows an error | Fewer than two offers in the database | Upload at least two files for the same component |
| First upload is slow | Model download or first encode | Wait for the first run to finish |
| Too many unmatched rows | Threshold too high | Lower `SIMILARITY_THRESHOLD` using Validation results |
| Too many wrong merges | Threshold too low | Raise `SIMILARITY_THRESHOLD` using Validation results |
| Threshold change has no effect | Server still uses old `.env` value | Restart uvicorn after editing `.env` |

---

## Known Limitations

- Sheet detection and keywords are tuned on course piping and electro files.
- Unit prices are often blank in source Excel files.
- This is a coursework demo, not a deployed procurement service.

---

## Future Work

- Support for additional components beyond piping and electro.
- Automatic threshold update from Validation results.
- Price range checks and currency normalization.
- Deployment as a hosted service with user accounts.

---

## Contact

**Almir Mustafic** — [@AlmirMBH](https://github.com/AlmirMBH)  
**Faris Mutapcic** — [@FarisM](https://github.com/FarisM)

---

## License

This project is released under the MIT License.

---

## Acknowledgments

The embedding model is [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) (sentence-transformers).

**Prof. Aida Brankovic** supervised the course project.

---

## Disclaimer

The troskovnik Excel datasets are provided for coursework only. They must not be committed to public repositories or shared outside the course. This tool was built for **CDA/MLRP** and is intended for academic use.
