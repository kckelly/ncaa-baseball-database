CREATE TABLE roster
(
  id SERIAL PRIMARY KEY,
  team_id int NOT NULL REFERENCES team,
  player_id int NOT NULL REFERENCES player,
  class class NOT NULL,
  UNIQUE (team_id, player_id)
);
