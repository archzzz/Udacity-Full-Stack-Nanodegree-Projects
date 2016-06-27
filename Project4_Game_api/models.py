

from google.appengine.ext import ndb
from random import shuffle
from protorpc import messages, message_types
from utils import compute_score, NUMBER_OF_PAIRS



class User(ndb.Model): 
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    score = ndb.IntegerProperty(default=0)

    def to_ranking_form(self):
        return RankForm(user_name=self.name, score = self.score)


class History(ndb.Model):
    card1 = ndb.IntegerProperty()
    card2 = ndb.IntegerProperty()
    result = ndb.StringProperty()

    def to_form(self):
        return HistoryForm(cards=[self.card1, self.card2], 
                           result=self.result)


class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    start_time = ndb.DateTimeProperty(required=True)
    end_time = ndb.DateTimeProperty()
    steps = ndb.IntegerProperty(default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    gameboard_values = ndb.IntegerProperty(repeated=True)
    gameboard_fliped = ndb.BooleanProperty(repeated=True)
    pairs = ndb.IntegerProperty(default=0)
    historys = ndb.StructuredProperty(History, repeated=True)

    @classmethod
    def new_game(cls, user, start_time):
        """Creates and return a new game"""
        values = [i for i in range(52)]
        shuffle(values)
        fliped = [False for i in range(0, 52)]

        game = Game(user=user,
                    start_time=start_time,
                    game_over=False,
                    gameboard_values=values,
                    gameboard_fliped=fliped)
        game.put()
        return game

    def to_form(self, message=None):
        """Returns a GameForm representation of a Game"""
        return GameForm(urlsafe_key = self.key.urlsafe(),
                        user_name = self.user.get().name,
                        start_time = self.start_time,
                        end_time = self.end_time,
                        game_over = self.game_over,
                        steps = self.steps,
                        pairs = self.pairs,
                        gameboard_values = self.gameboard_values,
                        gameboard_fliped = self.gameboard_fliped,
                        message = message)

    def end_game(self, end_time):
        """End the game -- store the end_time for score calculation, 
        put score in database if player won the game"""
        self.game_over = True
        self.end_time = end_time
        self.put()

        if self.pairs == NUMBER_OF_PAIRS:
            diff = self.end_time - self.start_time
            time = diff.days * 86400 + diff.seconds  
            score = Score(user = self.user, 
                          date = self.start_time.date(), 
                          time = time,
                          steps = self.steps,
                          score = compute_score(time, self.steps))
            user = self.user.get()
            user.score += score.score
            user.put()
            score.put()


class Score(ndb.Model):
    """Score project"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    time = ndb.IntegerProperty(required=True)
    steps = ndb.IntegerProperty(required=True)
    score = ndb.IntegerProperty()

    def to_form(self):
        return ScoreForm(urlsafe_key = self.key.urlsafe(),
                         user_name = self.user.get().name,
                         date = str(self.date),
                         time = self.time,
                         steps = self.steps,
                         score = self.score)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    start_time = message_types.DateTimeField(3, required=True)
    end_time = message_types.DateTimeField(4)
    game_over = messages.BooleanField(5, required=True)
    steps = messages.IntegerField(6, required=True)
    pairs = messages.IntegerField(7)
    gameboard_values=messages.IntegerField(8, repeated=True)
    gameboard_fliped=messages.BooleanField(9, repeated=True)
    message = messages.StringField(10)

class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound score information"""
    urlsafe_key = messages.StringField(1,required=True)
    user_name = messages.StringField(2)
    date = messages.StringField(3)
    time = messages.IntegerField(4)
    steps = messages.IntegerField(5)
    score = messages.IntegerField(6)

class ScoreForms(messages.Message):
    """Return mutiple ScoreForms"""
    items=messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound single string message"""
    message = messages.StringField(1, required=True)

class RankForm(messages.Message):
    """Ranking form of one player"""
    user_name = messages.StringField(1)
    score = messages.IntegerField(2)

class RankForms(messages.Message):
    """Return multiple RankForm"""
    items = messages.MessageField(RankForm, 1, repeated=True)

class HistoryForm(messages.Message):
    """HistoryForm -- a history move"""
    cards = messages.IntegerField(1, repeated=True)
    result = messages.StringField(2)

class HistoryForms(messages.Message):
    """Return mutiple of HistoryForms"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)