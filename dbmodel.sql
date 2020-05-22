CREATE TABLE transactions(
  account TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  amount REAL NOT NULL,
  currency TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NULL,
  note TEXT NULL);

CREATE INDEX account ON transactions(account);
CREATE INDEX timestampASC ON transactions(timestamp ASC);
CREATE INDEX timestampDESC ON transactions(timestamp DESC);


CREATE TABLE categories(
  pattern TEXT NOT NULL,
  field TEXT NOT NULL,
  category TEXT NOT NULL,
  expectedValue TEXT NULL,
  priority INTEGER NOT NULL DEFAULT 50
);

CREATE INDEX category ON categories(category ASC);
CREATE INDEX priority ON categories(priority DESC);
