# konto
web based HBCI banking software

## how to install
* pip3 install bottle (https://bottlepy.org/)
* jquery (http://jquery.com/) -- put this library into the "static" folder
* plotly for javascript (https://plot.ly/javascript/) -- put this library into the "static" folder

## how to use
* python3 index.py dev
* open http://localhost:8080

the tool will now scan for ".list" files within the "lists" directory

## how to poll your bank account for updates
have a look at the hbciMail/config_mail.py example and the MailWebsiteChanges tool (https://github.com/mtill/MailWebsiteChanges)
