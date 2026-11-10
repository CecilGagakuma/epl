-- Premier League stats pipeline: database schema

CREATE TABLE IF NOT EXISTS teams (
    id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS matches (
    id                   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    match_date           date     NOT NULL,
    home_team_id         integer  NOT NULL REFERENCES teams (id),
    away_team_id         integer  NOT NULL REFERENCES teams (id),
    home_goals           smallint NOT NULL CHECK (home_goals >= 0),
    away_goals           smallint NOT NULL CHECK (away_goals >= 0),
    home_shots           smallint NOT NULL CHECK (home_shots >= 0),
    away_shots           smallint NOT NULL CHECK (away_shots >= 0),
    home_shots_on_target smallint NOT NULL CHECK (home_shots_on_target >= 0),
    away_shots_on_target smallint NOT NULL CHECK (away_shots_on_target >= 0),

    CHECK (home_team_id <> away_team_id),
    UNIQUE (match_date, home_team_id, away_team_id)
);