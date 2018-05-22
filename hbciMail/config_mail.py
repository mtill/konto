#!/usr/bin/env python3
# coding=utf-8

from config_mail_model import HBCIParser, HBCIBalanceParser, SaveTitlesParser

from mwctools import URLReceiver as uri
from mwctools import CommandReceiver as command
from mwctools import XPathParser as xpath
from mwctools import CSSParser as css
from mwctools import RegExParser as regex
from mwctools import Content
from mwctools import Parser
from mwctools import getSubject

import os


workingDirectory = '/opt/MailWebsiteChanges-data'

sites = [

         {'name': 'banking',
          'parsers': [command(command='/opt/MailWebsiteChanges/bnk/banking.sh', contenttype='text'),
                      regex(contentregex='^.*$'),
                      HBCIParser()
                     ],
          'postRun': [SaveTitlesParser(thepath=workingDirectory, filenamebase='banking')]
         }

        ]


enableMailNotifications = True
sender = 'example@gmx.de'
smtphost = 'mail.gmx.net'
maxMailsPerSession = 15
useTLS = True
smtpport = 587
smtpusername = sender
smtppwd = 'secret'
receiver = 'example@gmx.de'

enableRSSFeed = False
rssfile = 'feed.xml'
maxFeeds = 100
