CREATE TABLE transactions(
  account TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  amount REAL NOT NULL,
  currency TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NULL,
  note TEXT NULL,
  id INTEGER PRIMARY KEY AUTOINCREMENT);

CREATE INDEX account ON transactions(account);
CREATE INDEX timestamp ON transactions(timestamp ASC);


CREATE TABLE categories(
  pattern TEXT NOT NULL,
  field TEXT NOT NULL,
  category TEXT NOT NULL
);

CREATE INDEX category ON categories(category ASC);
