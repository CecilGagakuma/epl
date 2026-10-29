"""Compute a Premier League table from match results."""

from dataclasses import dataclass

from epl.models import Match

POINTS_FOR_WIN = 3
POINTS_FOR_DRAW = 1


@dataclass
class TeamRecord:
    """One team's running totals. Not frozen: it is updated after each match."""

    team: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return POINTS_FOR_WIN * self.won + POINTS_FOR_DRAW * self.drawn


def record_result(record: TeamRecord, scored: int, conceded: int) -> None:
    """Update one team's totals from a single match, seen from its side."""
    record.played += 1
    record.goals_for += scored
    record.goals_against += conceded
    if scored > conceded:
        record.won += 1
    elif scored == conceded:
        record.drawn += 1
    else:
        record.lost += 1


def get_record(table: dict[str, TeamRecord], team: str) -> TeamRecord:
    """Return a team's record, creating an empty one the first time we see it."""
    if team not in table:
        table[team] = TeamRecord(team=team)
    return table[team]


def compute_table(matches: list[Match]) -> list[TeamRecord]:
    """Return every team's record, sorted into league order.

    Order: points, then goal difference, then goals scored (all highest
    first), then team name A-Z so the result is always predictable.
    """
    table: dict[str, TeamRecord] = {}
    for match in matches:
        home = get_record(table, match.home_team)
        away = get_record(table, match.away_team)
        record_result(home, scored=match.home_goals, conceded=match.away_goals)
        record_result(away, scored=match.away_goals, conceded=match.home_goals)

    return sorted(
        table.values(),
        key=lambda r: (-r.points, -r.goal_difference, -r.goals_for, r.team),
    )


def format_table(records: list[TeamRecord]) -> str:
    """Return the table as aligned text for printing."""
    lines = [f"{'Pos':>3}  {'Team':<16}{'P':>3}{'W':>4}{'D':>4}{'L':>4}"
             f"{'GF':>5}{'GA':>5}{'GD':>5}{'Pts':>5}"]
    for position, r in enumerate(records, start=1):
        lines.append(
            f"{position:>3}  {r.team:<16}{r.played:>3}{r.won:>4}{r.drawn:>4}"
            f"{r.lost:>4}{r.goals_for:>5}{r.goals_against:>5}"
            f"{r.goal_difference:>+5}{r.points:>5}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    from epl.loader import load_matches

    print(format_table(compute_table(load_matches(sys.argv[1]))))
