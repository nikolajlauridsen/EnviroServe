PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sensors(
  id int NOT NULL UNIQUE,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS climate (
  temp REAL,
  humid REAL,
  pressure REAL,
  light REAL,
  smoke REAL,
  time INT NOT NULL,
  sensor_id INT NOT NULL,
  FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);