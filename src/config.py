import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from constants import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite").lower()
SQLITE_DATABASE_PATH = os.getenv("SQLITE_DATABASE_PATH", "./app.db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
SHEET_SIMILARITY_THRESHOLD = float(os.getenv("SHEET_SIMILARITY_THRESHOLD", "0.75"))


def build_database_url() -> str:
    if DATABASE_ENGINE == "sqlite":
        return f"sqlite:///{SQLITE_DATABASE_PATH}"

    if DATABASE_ENGINE == "postgresql":
        missing_variables = [
            variable_name
            for variable_name, variable_value in {
                "POSTGRES_HOST": POSTGRES_HOST,
                "POSTGRES_DB": POSTGRES_DB,
                "POSTGRES_USER": POSTGRES_USER,
                "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
            }.items()
            if not variable_value
        ]
        if missing_variables:
            missing_list = ", ".join(missing_variables)
            raise ValueError(f"Missing required PostgreSQL environment variables: {missing_list}")

        encoded_password = quote_plus(POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg2://{POSTGRES_USER}:{encoded_password}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

    raise ValueError(f"Unsupported DATABASE_ENGINE: {DATABASE_ENGINE}")


DATABASE_URL = build_database_url()
