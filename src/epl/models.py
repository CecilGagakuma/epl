from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Match:
    """One completed Premier League match."""

    match_date: date
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    home_shots: int
    away_shots: int
    home_shots_on_target: int
    away_shots_on_target: int

    @property
    def result(self) -> str:
        """'H' for a home win, 'A' for an away win, 'D' for a draw."""
        if self.home_goals > self.away_goals:
            return "H"
        if self.home_goals < self.away_goals:
            return "A"
        return "D"

m = Match(date(2015, 8, 8), "Bournemouth", "Aston Villa", 0, 1, 11, 7, 2, 3)
print(m.result)  