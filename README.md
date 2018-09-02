# konto
web based HBCI banking software

## how to install
* pip3 install bottle (https://bottlepy.org/)
* jquery (http://jquery.com/) -- put this library into the "static" folder
* plotly for javascript (https://plot.ly/javascript/) -- put this library into the "static" folder

## how to use
* python3 index.py dev
* open http://localhost:8080

## how to poll your bank account for updates
have a look at the hbciMail/config_mail.py example and the MailWebsiteChanges tool (https://github.com/mtill/MailWebsiteChanges)

# database model
~~~~
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
~~~~

# database backup
~~~~
sqlite3 my_database.sqlite ".backup backup_file.sqlite"
OR: sqlite3 my_database .dump > my_database.back
~~~~
