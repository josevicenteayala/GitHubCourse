#!/usr/bin/env python3
"""Record merged PR metadata to persistent storage.

Supports two backends selected via --backend (default: sql):
  - sql    — PostgreSQL via DATABASE_URL connection string
  - sheets — Google Sheets via gspread + service account

Usage:
    python3 scripts/record_to_db.py \\
        --pr-id 42 --title "Step 01 solution" --author "student" \\
        --step step-01 --status pass --merged-at "2026-03-25T10:00:00Z"

    python3 scripts/record_to_db.py --backend sheets \\
        --pr-id 42 --title "Step 01 solution" --author "student" \\
        --step step-01 --status pass --merged-at "2026-03-25T10:00:00Z"

Environment variables:
    STORAGE_BACKEND     — "sql" (default) or "sheets"
    DATABASE_URL        — PostgreSQL connection string (sql backend)
    STORAGE_CREDENTIALS — Base64-encoded Google Cloud service account JSON (sheets)
    SPREADSHEET_ID      — Google Sheets spreadsheet ID (sheets)
"""
import argparse
import base64
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

DEFAULT_BACKEND = "sql"


# ---------------------------------------------------------------------------
# SQL (PostgreSQL) backend
# ---------------------------------------------------------------------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pr_records (
    id          SERIAL PRIMARY KEY,
    pr_id       TEXT NOT NULL,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    step        TEXT NOT NULL,
    review_status TEXT NOT NULL,
    merged_at   TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
"""

INSERT_SQL = """
INSERT INTO pr_records (pr_id, title, author, step, review_status, merged_at, recorded_at)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""


def record_to_sql(
    pr_id: str,
    title: str,
    author: str,
    step: str,
    status: str,
    merged_at: str,
) -> None:
    """Insert a row into the PostgreSQL database."""
    import psycopg2  # type: ignore[import-untyped]

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    recorded_at = datetime.now(timezone.utc).isoformat()

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute(
                INSERT_SQL,
                (pr_id, title, author, step, status, merged_at, recorded_at),
            )
        conn.commit()
    finally:
        conn.close()

    print(f"Recorded PR #{pr_id} ({step}) to database")


# ---------------------------------------------------------------------------
# Google Sheets backend
# ---------------------------------------------------------------------------


def _get_gspread_client():
    """Authenticate with Google Sheets using service account credentials."""
    import gspread  # type: ignore[import-untyped]
    from google.oauth2.service_account import Credentials  # type: ignore[import-untyped]

    creds_b64 = os.environ.get("STORAGE_CREDENTIALS", "")
    if not creds_b64:
        raise RuntimeError("STORAGE_CREDENTIALS environment variable is not set")

    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    creds_data = json.loads(creds_json)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(creds_data, tmp)
        tmp_path = tmp.name

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_file(tmp_path, scopes=scopes)
    os.unlink(tmp_path)

    return gspread.authorize(credentials)


def record_to_sheets(
    pr_id: str,
    title: str,
    author: str,
    step: str,
    status: str,
    merged_at: str,
) -> None:
    """Append a row to the configured Google Sheet."""
    spreadsheet_id = os.environ.get("SPREADSHEET_ID", "")
    if not spreadsheet_id:
        raise RuntimeError("SPREADSHEET_ID environment variable is not set")

    client = _get_gspread_client()
    sheet = client.open_by_key(spreadsheet_id).sheet1

    try:
        existing_headers = sheet.row_values(1)
    except Exception:
        existing_headers = []

    expected_headers = [
        "PR_ID",
        "Title",
        "Author",
        "Step",
        "Review_Status",
        "Merged_At",
        "Recorded_At",
    ]
    if not existing_headers:
        sheet.append_row(expected_headers)

    recorded_at = datetime.now(timezone.utc).isoformat()
    row = [pr_id, title, author, step, status, merged_at, recorded_at]
    sheet.append_row(row)
    print(f"Recorded PR #{pr_id} ({step}) to spreadsheet")


# ---------------------------------------------------------------------------
# Backend dispatch
# ---------------------------------------------------------------------------

BACKENDS = {
    "sql": record_to_sql,
    "sheets": record_to_sheets,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Record merged PR to storage")
    parser.add_argument(
        "--backend",
        choices=list(BACKENDS.keys()),
        default=os.environ.get("STORAGE_BACKEND", DEFAULT_BACKEND),
        help="Storage backend (default: sql). Override via STORAGE_BACKEND env var.",
    )
    parser.add_argument("--pr-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--merged-at", required=True)
    args = parser.parse_args()

    record_fn = BACKENDS[args.backend]

    try:
        record_fn(
            pr_id=args.pr_id,
            title=args.title,
            author=args.author,
            step=args.step,
            status=args.status,
            merged_at=args.merged_at,
        )
    except RuntimeError as exc:
        print(f"Storage error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
