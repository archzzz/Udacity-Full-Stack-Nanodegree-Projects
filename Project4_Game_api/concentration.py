import datetime
import endpoints
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from protorpc import remote, messages

from models import User, Game, Score, StringMessage, History
from models import GameForm, ScoreForm, ScoreForms, GameForms
from models import RankForm, RankForms, HistoryForm, HistoryForms

from utils import get_by_urlsafe, NUMBER_OF_PAIRS

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1), email=messages.StringField(2))
NEW_GAME_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),
    first_card=messages.IntegerField(2),
    second_card=messages.IntegerField(3))
RESULT_REQUEST = endpoints.ResourceContainer(
    number_of_result = messages.IntegerField(1, required=False))

DEAFULT_NUMBER_OF_REQUEST = 10
CORRECT_PAIR = 26

@endpoints.api(name='concentration_game', version='v1')
class ConcentrationGameApi(remote.Service):

    """Concentration game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A user with that name already exists!')

        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST, 
                      response_message=GameForm, 
                      path='game', 
                      name='new_game', 
                      http_method='POST')
    def new_game(self, request):
        """Creates a new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        game = Game.new_game(user.key, datetime.datetime.now())
        return game.to_form('Good luck!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return game.to_form('Time to make a move!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Make a move. Return new game state"""
        game = get_by_urlsafe(request.urlsafe_game_key,Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            return game.to_form('Game already over!')
        if game.gameboard_fliped[request.first_card] or game.gameboard_fliped[request.second_card]:
            game.historys.append(History(card1=request.first_card, 
                                         card2=request.second_card,
                                         result='Can not choose a fliped card.'))
            return game.to_form('Can not choose a fliped card.')

        game.steps += 1

        if abs(game.gameboard_values[request.first_card] - game.gameboard_values[request.second_card]) == CORRECT_PAIR:
            game.pairs += 1
            game.gameboard_fliped[request.first_card] = True
            game.gameboard_fliped[request.second_card] = True

            if game.pairs == NUMBER_OF_PAIRS:
                game.end_game(datetime.datetime.now())
                msg = "You win!"
            
            else:
                msg = "Correct pairs!"

        else:
            msg = "Incorrect pairs!"
        
        game.historys.append(History(card1=game.gameboard_values[request.first_card],
                                     card2=game.gameboard_values[request.second_card],
                                     result=msg))
        game.put()
        return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='score/user/{user_name}',
                      name='get_user_score',
                      http_method='GET')
    def get_user_score(self, request):
        """Return all scores of a user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
              'A user with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all games played by a user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
              'A user with that name does not exist!')
        games = Game.query(Game.user == user.key)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game in progress"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            return StringMessage(message="Can not cancel a completed game!")
        game.key.delete()
        return StringMessage(message="Game {} is deleted!".format(request.urlsafe_game_key))


    @endpoints.method(request_message=RESULT_REQUEST,
                      response_message=ScoreForms,
                      path='high_score',
                      name='get_high_scores',
                      http_method='PUT')
    def get_high_scores(self, request):
        """Get high scores in decreasing order"""
        if not request.number_of_result:
            number = DEAFULT_NUMBER_OF_REQUEST
        else:
            number = request.number_of_result
        scores = Score.query().order(-Score.score).fetch(limit=number)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=RankForms,
                      path='ranking',
                      name='get_user_ranking',
                      http_method='POST')
    def get_user_ranking(self, request):
        """Get all users ranked by score"""
        users = User.query().order(-User.score)
        return RankForms(items=[user.to_ranking_form() for user in users])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='POST')
    def get_game_history(self, request):
        """Get all history moves of a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        return HistoryForms(items=[history.to_form() for history in game.historys])


api = endpoints.api_server([ConcentrationGameApi])



