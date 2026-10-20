from datetime import date
from pathlib import Path

import pytest

from epl.loader import load_matches

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_matches():
    """The three matches in the small sample CSV."""
    return load_matches(FIXTURES / "sample_matches.csv")


def test_loads_every_match_and_skips_blank_rows(sample_matches):
    assert len(sample_matches) == 3


def test_first_match_is_converted_correctly(sample_matches):
    first = sample_matches[0]
    assert first.match_date == date(2015, 8, 8)
    assert first.home_team == "Bournemouth"
    assert first.away_team == "Aston Villa"
    assert first.home_goals == 0
    assert first.away_goals == 1
    assert first.result == "A"


def test_bad_row_raises_error_with_line_number(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST\n"
        "E0,08/08/2015,Leicester,Sunderland,4,,H,18,11,10,5\n"
    )
    with pytest.raises(ValueError, match="line 2"):
        load_matches(bad_csv)