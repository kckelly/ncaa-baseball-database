CREATE TABLE fielding_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  po int,
  a int,
  e int,
  pb int,
  ci int,
  sb int,
  cs int,
  dp int,
  tp int,
  UNIQUE (game_id, roster_id)
);
