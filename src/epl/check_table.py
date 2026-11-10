"""Check that the league_table view in Postgres matches the Python table.

Usage (from the project root, with Postgres running and data loaded):
    PYTHONPATH=src python src/epl/check_table.py data/E0.csv
"""

import os
import sys

import psycopg
from dotenv import load_dotenv

from epl.loader import load_matches
from epl.table import compute_table


def python_table(csv_path: str) -> list[tuple]:
    """The table computed in Python, one tuple per team in league order."""
    return [
        (r.team, r.played, r.won, r.drawn, r.lost,
         r.goals_for, r.goals_against, r.goal_difference, r.points)
        for r in compute_table(load_matches(csv_path))
    ]


def sql_table(conn: psycopg.Connection) -> list[tuple]:
    """The table computed by the league_table view, in the same shape."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT team, played, won, drawn, lost,
                   goals_for, goals_against, goal_difference, points
            FROM league_table
            ORDER BY position
            """
        )
        return cur.fetchall()


def main(csv_path: str) -> int:
    load_dotenv()
    with psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    ) as conn:
        from_sql = sql_table(conn)

    from_python = python_table(csv_path)

    if from_sql == from_python:
        print(f"OK: SQL and Python tables match ({len(from_sql)} teams).")
        return 0

    print("MISMATCH between SQL and Python tables:")
    for position in range(max(len(from_sql), len(from_python))):
        sql_row = from_sql[position] if position < len(from_sql) else None
        py_row = from_python[position] if position < len(from_python) else None
        if sql_row != py_row:
            print(f"  position {position + 1}:")
            print(f"    SQL:    {sql_row}")
            print(f"    Python: {py_row}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
