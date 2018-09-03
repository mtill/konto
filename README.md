# konto
web based HBCI banking software

## how to install
* pip3 install bottle (https://bottlepy.org/)
* jquery (http://jquery.com/) -- put this library into the "static" folder (filename: jquery-latest.min.js)
* plotly for javascript (https://plot.ly/javascript/) -- put this library into the "static" folder (filename: plotly-latest.min.js)

## how to use
* python3 index.py dev
* open http://localhost:8080

## how to poll your bank account for updates
have a look at the hbciMail/config_mail.py example and the MailWebsiteChanges tool (https://github.com/mtill/MailWebsiteChanges)

## how to backup the transaction database
sqlite3 my_database.sqlite ".backup backup_file.sqlite"
OR: sqlite3 my_database .dump > my_database.back
