##Game Description:
Concentration is a memorizing game. Given a deck of 52 cards, during each move, 
player chooses two cards and turns them face up. If they are of the same rank and 
color (e.g. six of hearts and six of diamonds, queen of clubs and queen of spades) 
then player wins the pair. If they are not of the same rank and color, they 
are turned face down again.The game ends when the last pair has been picked up.

'Moves' are sent to the `make_move` endpoint which will reply with either: 
'Correct pair!', 'Incorrect pair!', 'You win!'

Many different Concentration games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - concentration.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Generates an array of  
    integers from 0 to 51 in random order to represent a deck of cards:
        0  ~ 12: Spades Ace ~ King
        13 ~ 25: Hearts Ace ~ King
        26 ~ 38: Clubs Ace ~ King
        39 ~ 51: Diamonds Ace ~ King
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, first_card, second_card
    - Returns: GameForm with new game state.
    - Description: Accepts a 'move' and returns the updated state of the game. 
    If difference of two cards equals to 26, two cards are same rank and color,
    player wins that pair. Store the 'move' to historys. If this causes a game 
    to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms.
    - Description: Returns all Games recorded by the given player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: StringMessage
    - Description: Delete a game of the given urlsafe_game_key from the datastore.
    Cannot cancel a finished game.

- **get_high_scores**
    - Path: 'high_score'
    - Method: PUT
    - Parameters: number_of_result
    - Returns: ScoreForms.
    - Description: Returns a given number of highest scores, in decreasing order. If no 
    parameters is given, use 10 as default value.

- **get_user_ranking**
    - Path: 'ranking'
    - Method: POST
    - Parameters: None
    - Returns: RankForms
    - Description: Return the name and score of all users, ranked in decreasing order 
    of scores.

- **get_game_history**
    - Path:'game/history/{urlsafe_game_key}'
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: HistoryForms
    - Description: Return all history moves of a given game.

##Models Included:
 - **User**
    - Stores unique user_name, email address and score.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

- **History**
    - Records a move history (two cards and result).
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, start_time, end_time,
    game_over flag, steps, pairs won, gameboard_values, gameboard_flipped flag,
    message, user_name).
 - **GameForms**
    - Multiple GameForm container. 
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, time, steps,
    score).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
 - **RankForm**
    - Representation of the rank of a user (user_name, score)
 - **RankForms**
    - Multiple RankForm container
 - **HistoryForm**
    - Representation of a move history(cards, result)
 - **HistoryForms**
    - Multiple HistoryForm container