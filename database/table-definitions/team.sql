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
