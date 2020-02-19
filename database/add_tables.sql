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
  division int CHECK (division = 1 OR division = 2 OR division = 3),
  UNIQUE (name, division)
);
CREATE TABLE school
(
  id SERIAL PRIMARY KEY,
  ncaa_id int UNIQUE NOT NULL,
  name varchar NOT NULL,
  nickname varchar,
  url varchar
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
  UNIQUE (year, conference_id, school_id),
  UNIQUE (year, school_id)
);
CREATE TABLE player
(
  id SERIAL PRIMARY KEY,
  ncaa_id int NOT NULL UNIQUE,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL
);
CREATE TYPE class AS ENUM ('n/a','freshman', 'sophomore', 'junior', 'senior');

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
  inning int NOT NULL CHECK (inning > 0),
  ord int NOT NULL,
  text text NOT NULL,
  pitches varchar,
  UNIQUE (game_id, team_id, inning, ord)
);
CREATE TYPE pos AS ENUM ('p', 'c', '1b', '2b', '3b', 'ss', 'lf', 'cf', 'rf', 'dh', 'ph', 'pr', 'n/a');

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
CREATE TABLE pitching_line
(
  game_id int NOT NULL REFERENCES game,
  roster_id int NOT NULL REFERENCES roster,
  app int CHECK (app = 0 OR app = 1),
  gs int CHECK (gs = 0 OR app = 1),
  ord int,
  w int CHECK (w = 0 OR w = 1),
  l int CHECK (l = 0 OR l = 1),
  sv int CHECK (sv = 0 OR sv = 1),
  ip float,
  p int,
  bf int,
  h int,
  dbl int,
  tpl int,
  hr int,
  bb int,
  ibb int,
  hbp int,
  r int,
  er int,
  ir int,
  irs int,
  fo int,
  go int,
  k int,
  kl int,
  sf int,
  sh int,
  bk int,
  wp int,
  cg int CHECK (cg = 0 OR cg = 1),
  sho int CHECK (sho = 0 OR sho = 1),
  UNIQUE (game_id, roster_id)
);
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
CREATE TABLE umpire
(
  id SERIAL PRIMARY KEY,
  first_name varchar NOT NULL,
  last_name varchar NOT NULL
);
CREATE TYPE ump_pos AS ENUM ('hp', '1b', '2b', '3b', 'lf', 'rf');

CREATE TABLE game_umpire
(
  game_id int NOT NULL REFERENCES game,
  umpire_id int NOT NULL REFERENCES umpire,
  position ump_pos NOT NULL,
  --UNIQUE (game_id, umpire_id),
  UNIQUE (game_id, position)
);
\copy year_info (year, year_id, hitting_id, pitching_id, fielding_id) from 'csv-data/year_info.csv' delimiter ',' NULL AS '' CSV HEADER ;
