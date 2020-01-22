CREATE TABLE year_info
(
  year int PRIMARY KEY,
  year_id int NOT NULL UNIQUE,
  hitting_id int UNIQUE NOT NULL,
  pitching_id int UNIQUE NOT NULL,
  fielding_id int UNIQUE NOT NULL
);
CREATE TABLE conference
(
  id SERIAL PRIMARY KEY,
  name varchar NOT NULL,
  division int NOT NULL CHECK (division = 1 OR division = 2 OR division = 3),
  UNIQUE (name, division)
);
CREATE TABLE school
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  name varchar NOT NULL,
  nickname varchar NOT NULL,
  url varchar NOT NULL
);
CREATE TABLE coach
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL,
  alma_mater varchar,
  year_graduated int
);
CREATE TABLE stadium
(
  id SERIAL PRIMARY KEY,
  name varchar NOT NULL,
  capacity int,
  year_built int
);
CREATE TABLE team
(
  id SERIAL PRIMARY KEY,
  year int NOT NULL REFERENCES year_info,
  conference_id int NOT NULL REFERENCES conference,
  school_id int NOT NULL REFERENCES school,
  coach_id int REFERENCES coach,
  stadium_id int REFERENCES stadium,
  UNIQUE (year, conference_id, school_id)
);
CREATE TABLE player
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL
);
CREATE TYPE class AS ENUM ('freshman', 'sophomore', 'junior', 'senior');

CREATE TABLE roster
(
  id SERIAL PRIMARY KEY,
  team_id int NOT NULL REFERENCES team,
  player_id int NOT NULL REFERENCES player,
  class class NOT NULL,
  UNIQUE (team_id, player_id)
);
CREATE TABLE game
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE,
  away_team_id int NOT NULL REFERENCES team,
  home_team_id int NOT NULL REFERENCES team,
  date date NOT NULL,
  location varchar,
  attendance int
);
CREATE TABLE inning
(
  game_id int NOT NULL REFERENCES game,
  team_id int NOT NULL REFERENCES team,
  inning int NOT NULL CHECK (inning > 0),
  runs int NOT NULL CHECK (runs >= 0),
  UNIQUE (game_id, team_id, inning)
);
CREATE TABLE play_by_play
(
  game_id int NOT NULL REFERENCES game,
  team_id int NOT NULL REFERENCES team,
  ord int NOT NULL,
  text text NOT NULL,
  UNIQUE (game_id, team_id, ord)
);
CREATE TYPE pos AS ENUM ('p', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'dh', 'ph', 'pr');

CREATE TABLE game_position
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  position pos NOT NULL,
  UNIQUE (game_id, roster_id, position)
);
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
CREATE TABLE pitching_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  app int NOT NULL CHECK (app = 0 OR app = 1),
  gs int NOT NULL CHECK (gs = 0 OR app = 1),
  ord int NOT NULL,
  w int NOT NULL CHECK (w = 0 OR w = 1),
  l int NOT NULL CHECK (l = 0 OR l = 1),
  sv int NOT NULL CHECK (sv = 0 OR sv = 1),
  ip float NOT NULL,
  p int NOT NULL,
  bf int NOT NULL,
  h int NOT NULL,
  dbl int NOT NULL,
  tpl int NOT NULL,
  hr int NOT NULL,
  bb int NOT NULL,
  ibb int NOT NULL,
  hbp int NOT NULL,
  r int NOT NULL,
  er int NOT NULL,
  ir int NOT NULL,
  irs int NOT NULL,
  fo int NOT NULL,
  go int NOT NULL,
  k int NOT NULL,
  kl int NOT NULL,
  sf int NOT NULL,
  sh int NOT NULL,
  bk int NOT NULL,
  wp int NOT NULL,
  cg int NOT NULL CHECK (cg = 0 OR cg = 1),
  sho int NOT NULL CHECK (sho = 0 OR sho = 1),
  UNIQUE (game_id, roster_id)
);
CREATE TABLE fielding_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  tc int NOT NULL,
  po int NOT NULL,
  a int NOT NULL,
  e int NOT NULL,
  pb int NOT NULL,
  ci int NOT NULL,
  sb int NOT NULL,
  cs int NOT NULL,
  dp int NOT NULL,
  tp int NOT NULL,
  UNIQUE (game_id, roster_id)
);
CREATE TABLE umpire
(
  id SERIAL PRIMARY KEY,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL
);
CREATE TABLE game_umpire
(
  game_id int NOT NULL REFERENCES game,
  umpire_id int NOT NULL REFERENCES umpire,
  position pos NOT NULL,
  UNIQUE (game_id, umpire_id),
  UNIQUE (game_id, position)
);
\copy year_info(year, year_id, hitting_id, pitching_id, fielding_id) from 'csv-data/year_info.csv' delimiter ',' NULL AS '' CSV HEADER;