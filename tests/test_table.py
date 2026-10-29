from datetime import date

from epl.models import Match
from epl.table import compute_table


def make_match(home: str, away: str, home_goals: int, away_goals: int) -> Match:
    """Build a Match where only teams and score matter for the test."""
    return Match(date(2015, 8, 8), home, away, home_goals, away_goals, 0, 0, 0, 0)


def test_win_gives_three_points_and_loss_gives_none():
    table = compute_table([make_match("Leicester", "Sunderland", 4, 2)])
    winner, loser = table
    assert (winner.team, winner.points, winner.won) == ("Leicester", 3, 1)
    assert (loser.team, loser.points, loser.lost) == ("Sunderland", 0, 1)


def test_draw_gives_one_point_each():
    table = compute_table([make_match("Chelsea", "Swansea", 2, 2)])
    assert [r.points for r in table] == [1, 1]
    assert all(r.drawn == 1 for r in table)


def test_goals_and_goal_difference_add_up_across_matches():
    table = compute_table([
        make_match("Arsenal", "West Ham", 0, 2),
        make_match("Crystal Palace", "Arsenal", 1, 2),
    ])
    arsenal = next(r for r in table if r.team == "Arsenal")
    assert (arsenal.played, arsenal.goals_for, arsenal.goals_against) == (2, 2, 3)
    assert arsenal.goal_difference == -1


def test_level_on_points_sorted_by_goal_difference():
    # Both win once; A wins 3-0 (GD +3), B wins 1-0 (GD +1)
    table = compute_table([
        make_match("A", "X", 3, 0),
        make_match("B", "Y", 1, 0),
    ])
    assert [r.team for r in table[:2]] == ["A", "B"]


def test_level_on_points_and_goal_difference_sorted_by_goals_scored():
    # Both GD +1; A wins 3-2, B wins 1-0, so A has scored more
    table = compute_table([
        make_match("B", "Y", 1, 0),
        make_match("A", "X", 3, 2),
    ])
    assert [r.team for r in table[:2]] == ["A", "B"]
