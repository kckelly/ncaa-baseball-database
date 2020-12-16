CREATE TABLE hitting_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  lineup_spot int CHECK (lineup_spot >= 1 AND lineup_spot <= 9),
  sub boolean,
  ab int,
  h int,
  dbl int,
  tpl int,
  hr int,
  bb int,
  ibb int,
  hbp int,
  r int,
  rbi int,
  k int,
  sf int,
  sh int,
  dp int,
  sb int,
  cs int,
  UNIQUE (game_id, roster_id)
);
