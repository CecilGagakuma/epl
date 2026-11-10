-- League table computed directly in Postgres.
-- Same rules as src/epl/table.py: 3 points for a win, 1 for a draw,
-- sorted by points, then goal difference, then goals scored, then name.
--
-- Query it with:  SELECT * FROM league_table ORDER BY position;

CREATE OR REPLACE VIEW league_table AS
WITH results AS (
    -- One row per team per match, seen from that team's side.
    SELECT home_team_id AS team_id,
           home_goals   AS scored,
           away_goals   AS conceded
    FROM matches
    UNION ALL
    SELECT away_team_id,
           away_goals,
           home_goals
    FROM matches
),
totals AS (
    -- Add up each team's rows.
    SELECT t.name                                       AS team,
           count(*)                                     AS played,
           count(*) FILTER (WHERE r.scored > r.conceded) AS won,
           count(*) FILTER (WHERE r.scored = r.conceded) AS drawn,
           count(*) FILTER (WHERE r.scored < r.conceded) AS lost,
           sum(r.scored)                                AS goals_for,
           sum(r.conceded)                              AS goals_against
    FROM results AS r
    JOIN teams AS t ON t.id = r.team_id
    GROUP BY t.name
)
SELECT row_number() OVER (
           ORDER BY 3 * won + drawn DESC,
                    goals_for - goals_against DESC,
                    goals_for DESC,
                    team
       )                          AS position,
       team,
       played,
       won,
       drawn,
       lost,
       goals_for,
       goals_against,
       goals_for - goals_against  AS goal_difference,
       3 * won + drawn            AS points
FROM totals;
