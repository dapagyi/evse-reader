DROP TABLE IF EXISTS charging;
DROP TABLE IF EXISTS app_state;

CREATE TABLE charging (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  charge_number_internal INTEGER NOT NULL UNIQUE,
  charge_type TEXT NOT NULL, 
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  energy_kWh REAL NOT NULL,
  duration TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_state (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT INTO app_state (key, value) VALUES ('last_updated', NULL);
INSERT INTO app_state (key, value) VALUES ('creation_time', CURRENT_TIMESTAMP);