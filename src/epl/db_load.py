"""Load matches from a football-data.co.uk CSV file into Postgres.

Usage (from the project root, with Postgres running):
    PYTHONPATH=src python src/epl/db_load.py data/E0.csv

Safe to run more than once: teams and matches that are already in the
database are skipped, so a second run adds nothing.
"""

import os
import sys

import psycopg
from dotenv import load_dotenv

from epl.loader import load_matches
from epl.models import Match

INSERT_TEAM = """
    INSERT INTO teams (name)
    VALUES (%s)
    ON CONFLICT (name) DO NOTHING
"""

INSERT_MATCH = """
    INSERT INTO matches (
        match_date, home_team_id, away_team_id,
        home_goals, away_goals,
        home_shots, away_shots,
        home_shots_on_target, away_shots_on_target
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (match_date, home_team_id, away_team_id) DO NOTHING
"""


def connect() -> psycopg.Connection:
    """Open a connection using the settings in .env."""
    load_dotenv()
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def team_names(matches: list[Match]) -> list[str]:
    """Every team that appears in the matches, home or away, A-Z."""
    names = {m.home_team for m in matches} | {m.away_team for m in matches}
    return sorted(names)


def count_rows(cur: psycopg.Cursor, table: str) -> int:
    """How many rows a table has. Only ever called with our own table names."""
    cur.execute(f"SELECT count(*) FROM {table}")
    return cur.fetchone()[0]


def match_row(match: Match, team_ids: dict[str, int]) -> tuple:
    """One match as a tuple, in the same order as INSERT_MATCH's columns."""
    return (
        match.match_date,
        team_ids[match.home_team],
        team_ids[match.away_team],
        match.home_goals,
        match.away_goals,
        match.home_shots,
        match.away_shots,
        match.home_shots_on_target,
        match.away_shots_on_target,
    )


def load_into_db(conn: psycopg.Connection, matches: list[Match]) -> None:
    """Insert teams, then matches, and print what changed."""
    with conn.cursor() as cur:
        teams_before = count_rows(cur, "teams")
        matches_before = count_rows(cur, "matches")

        # 1. Teams first: matches need their IDs.
        cur.executemany(INSERT_TEAM, [(name,) for name in team_names(matches)])

        # 2. Look up every team's ID once: {"Arsenal": 1, ...}
        cur.execute("SELECT id, name FROM teams")
        team_ids = {name: team_id for team_id, name in cur.fetchall()}

        # 3. Matches, using those IDs.
        cur.executemany(INSERT_MATCH, [match_row(m, team_ids) for m in matches])

        teams_after = count_rows(cur, "teams")
        matches_after = count_rows(cur, "matches")

    new_matches = matches_after - matches_before
    print(f"Teams:   {teams_after} in database ({teams_after - teams_before} new)")
    print(f"Matches: {matches_after} in database ({new_matches} new, "
          f"{len(matches) - new_matches} already loaded)")


def main(csv_path: str) -> None:
    matches = load_matches(csv_path)
    print(f"Read {len(matches)} matches from {csv_path}")

    # The `with` block is one transaction: everything is saved at the end,
    # or, if anything fails, nothing is.
    with connect() as conn:
        load_into_db(conn, matches)


if __name__ == "__main__":
    main(sys.argv[1])
