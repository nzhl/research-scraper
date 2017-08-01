from yagmail import SMTP
from flask import session


class Mailman(object):
    account = "nottingham.researchscraper@gmail.com"
    password = "scraper2017"
    subject = "Research Scraper registration Invitation"
        
    def __init__(self):
        #https://stackoverflow.com/questions/26852128/smtpauthenticationerror-when-sending-mail-using-gmail-and-python
        self.sender = SMTP(self.account, self.password)

    def send_invitation(self, email, name, author_id):
        with open('web/mailman/content.txt') as f:
            raw_content = f.read()
        content = raw_content % (name, session['name'], author_id)
        self.sender.send(email, self.subject, content)
