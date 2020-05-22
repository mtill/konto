# konto
web based HBCI banking software

## how to install
* pip3 install bottle (https://bottlepy.org/)
* cp mwc-full.conf /usr/local/share/aqbanking/imexporters/csv/profiles

## how to use
* python3 index.py dev
* open http://localhost:8080

## how to poll your bank account for updates
have a look at the hbcifetch.sh and hbciimport.sh scripts

## how to backup the transaction database
sqlite3 my_database.sqlite ".backup backup_file.sqlite"
OR: sqlite3 my_database .dump > my_database.back
