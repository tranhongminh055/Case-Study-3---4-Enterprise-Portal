import argparse
import csv
import json
from pathlib import Path

from sqlalchemy import MetaData, select, or_, text

from backend.database.sqlserver import engine

DEFAULT_OUTPUT_TXT = "null_employees.txt"
DEFAULT_OUTPUT_SQL = "delete_null_employees.sql"


def find_null_rows(table_name: str, output_txt: Path, output_sql: Path, include_columns=None):
    metadata = MetaData()
    metadata.reflect(bind=engine, only=[table_name])
    if table_name not in metadata.tables:
        raise ValueError(f"Table '{table_name}' was not found in the database")

    table = metadata.tables[table_name]
    columns = list(table.columns)
    if include_columns:
        columns = [col for col in columns if col.name in include_columns]
        if not columns:
            raise ValueError("No matching columns found for include_columns")

    null_predicates = [col.is_(None) for col in columns]
    query = select(table).where(or_(*null_predicates)).order_by(table.primary_key)

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    if not rows:
        print(f"No rows with NULL values found in table '{table_name}'")
        return

    output_txt.parent.mkdir(parents=True, exist_ok=True)
    output_sql.parent.mkdir(parents=True, exist_ok=True)

    with output_txt.open("w", encoding="utf-8") as txt_file:
        writer = csv.writer(txt_file, delimiter="\t", lineterminator="\n")
        writer.writerow([col.name for col in columns])
        for row in rows:
            writer.writerow([row[col.name] for col in columns])

    pk_cols = [c.name for c in table.primary_key.columns]
    if not pk_cols:
        raise ValueError("Table has no primary key; cannot generate delete statements safely")

    with output_sql.open("w", encoding="utf-8") as sql_file:
        sql_file.write("-- Delete statements for rows containing NULL values\n")
        for row in rows:
            where_clauses = []
            for pk in pk_cols:
                value = row[pk]
                if value is None:
                    raise ValueError("Primary key value is NULL, cannot generate safe delete statement")
                if isinstance(value, str):
                    safe_value = value.replace("'", "''")
                    where_clauses.append(f"[{pk}] = '{safe_value}'")
                else:
                    where_clauses.append(f"[{pk}] = {value}")
            sql_file.write(f"DELETE FROM [{table_name}] WHERE {' AND '.join(where_clauses)};\n")

    print(f"Exported {len(rows)} rows with NULL values to {output_txt}")
    print(f"Generated delete statements in {output_sql}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export rows with NULL values from a SQL Server table.")
    parser.add_argument("--table", default="employees", help="Table name to scan")
    parser.add_argument("--txt", default=DEFAULT_OUTPUT_TXT, help="Output TXT filename")
    parser.add_argument("--sql", default=DEFAULT_OUTPUT_SQL, help="Output SQL filename")
    parser.add_argument(
        "--columns",
        nargs="*",
        help="Optional list of columns to check for NULL values; default checks all columns",
    )

    args = parser.parse_args()
    find_null_rows(args.table, Path(args.txt), Path(args.sql), include_columns=args.columns)
