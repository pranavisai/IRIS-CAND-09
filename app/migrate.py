from pathlib import Path

import psycopg

from app.config import load_settings


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def run_migrations() -> None:
    settings = load_settings()

    with psycopg.connect(settings.database_url) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = migration_file.name

            applied = conn.execute(
                "SELECT 1 FROM schema_migrations WHERE version = %s",
                (version,),
            ).fetchone()

            if applied:
                print(f"Skipping already applied migration: {version}")
                continue

            sql = migration_file.read_text(encoding="utf-8")
            with conn.transaction():
                conn.execute(sql)
                conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (version,),
                )

            print(f"Applied migration: {version}")


if __name__ == "__main__":
    run_migrations()