from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

import psycopg  # noqa: E402

from app.core.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    migrations = sorted((ROOT / "db").glob("[0-9][0-9][0-9]_*.sql"))
    if not migrations:
        raise SystemExit("No SQL migrations found in db/")

    with psycopg.connect(settings.database_url) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )

        existing_schema = conn.execute(
            "SELECT to_regclass('public.analyses') IS NOT NULL"
        ).fetchone()[0]
        applied = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }

        if existing_schema and "001_initial.sql" not in applied:
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                ("001_initial.sql",),
            )
            applied.add("001_initial.sql")
            print("Detected existing GAP schema; marked 001_initial.sql as applied.")

        for migration in migrations:
            if migration.name in applied:
                print(f"skip  {migration.name}")
                continue
            sql = migration.read_text(encoding="utf-8")
            conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (migration.name,),
            )
            print(f"apply {migration.name}")

    print("Database migrations complete.")


if __name__ == "__main__":
    main()
