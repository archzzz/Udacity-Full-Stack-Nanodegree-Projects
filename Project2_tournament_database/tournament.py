#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Fail to connect database {}".format(database_name))


def database_execute(ops):
    """database query template which passes in query operations"""
    db, cursor = connect()
    ret = ops(cursor,db)
    db.close()
    return ret


def deleteMatches():
    """Remove all the match records from the database."""
    def ops(c,db):
        query = "delete from matches"
        c.execute(query)
        db.commit()

    database_execute(ops)


def deletePlayers():
    """Remove all the player records from the database."""
    def ops(c,db):
        query = "delete from players"
        c.execute(query)
        db.commit()

    database_execute(ops)


def countPlayers():
    """Returns the number of players currently registered."""
    def ops(c,db):
        c.execute("select count(*) from players")
        return c.fetchone()[0]
    return database_execute(ops)


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    def ops(c,db):
        query = "insert into players(name) values(%s)"
        c.execute(query, (name,))
        db.commit()
    database_execute(ops)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    def ops(c,db):
        sentence = """select * from players order by win"""
        c.execute(sentence)
        return c.fetchall()

    return database_execute(ops)


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    def ops(c,db):
        c.execute("update players set match = match+1, win = win+1 where id = %s", (winner,))
        c.execute("update players set match = match+1 where id = %s", (loser,))
        c.execute("insert into matches (winner_id, loser_id) values(%s, %s)", (winner, loser))
        db.commit()

    database_execute(ops)


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    ret = playerStandings()

    if (len(ret) % 2 == 0):
        return [(ret[i][0], ret[i][1], ret[i+1][0], ret[i+1][1]) for i in range(0, len(ret), 2)]
    else:
        print("Players can not be paired.")
        return None
