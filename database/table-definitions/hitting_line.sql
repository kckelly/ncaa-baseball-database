CREATE TABLE hitting_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  ab int NOT NULL,
  h int NOT NULL,
  dbl int NOT NULL,
  tpl int NOT NULL,
  hr int NOT NULL,
  bb int NOT NULL,
  ibb int NOT NULL,
  hbp int NOT NULL,
  r int NOT NULL,
  rbi int NOT NULL,
  k int NOT NULL,
  sf int NOT NULL,
  sh int NOT NULL,
  dp int NOT NULL,
  sb int NOT NULL,
  cs int NOT NULL,
  UNIQUE (game_id, roster_id)
);
