
"""Load Premier League matches from a football-data.co.uk CSV file."""
 
import csv
from datetime import date, datetime
 
from epl.models import Match
 
# Older seasons use a 2-digit year (08/08/15), newer ones use 4 digits.
DATE_FORMATS = ("%d/%m/%Y", "%d/%m/%y")
 
 
def parse_date(text: str) -> date:
    """Turn '08/08/2015' or '08/08/15' into a date."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {text!r}")
 
 
def is_blank(row: dict) -> bool:
    """True for filler rows such as ',,,,,' at the end of a file."""
    return not any((value or "").strip() for value in row.values())
 
 
def row_to_match(row: dict) -> Match:
    """Convert one CSV row (a dict of strings) into a Match."""
    return Match(
        match_date=parse_date(row["Date"]),
        home_team=row["HomeTeam"].strip(),
        away_team=row["AwayTeam"].strip(),
        home_goals=int(row["FTHG"]),
        away_goals=int(row["FTAG"]),
        home_shots=int(row["HS"]),
        away_shots=int(row["AS"]),
        home_shots_on_target=int(row["HST"]),
        away_shots_on_target=int(row["AST"]),
    )
 
 
def load_matches(path: str) -> list[Match]:
    """Read a football-data.co.uk CSV and return its matches.
 
    Blank filler rows are skipped. A row that looks like a real match but
    has a missing or invalid value raises ValueError naming the line, so
    bad data is never dropped silently.
    """
    matches = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if is_blank(row):
                continue
            try:
                matches.append(row_to_match(row))
            except (KeyError, ValueError) as error:
                raise ValueError(
                    f"{path}, line {reader.line_num}: bad match row ({error})"
                ) from error
    return matches
 
 
if __name__ == "__main__":
    import sys
 
    loaded = load_matches(sys.argv[1])
    print(f"Loaded {len(loaded)} matches")
    print(f"First: {loaded[0]}")
    print(f"Last:  {loaded[-1]}")
