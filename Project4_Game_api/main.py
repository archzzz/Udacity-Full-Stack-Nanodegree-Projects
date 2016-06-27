"""main.py - this file contains handlers that are called by taskqueue or/and 
cronjobs."""

import logging

import webapp2
from google.appengine.api import mail, app_identity
from concentration import ConcentrationGameApi

from models import User, Game


logger = logging.getLogger('google.appengine.tools.appengine_rpc')

class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """"Send a reminder email to each user who has an incomplete game.
        Call every 1 hours using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over != True)
        for game in games:
            user = game.user.get()
            subject = 'Reminder of your incomplete game!'
            body = 'Hello {}, time to finish your concentration game!'.format(user.name)
            #from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                            user.email,
                            subject,
                            body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
