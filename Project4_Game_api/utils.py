# question: can I combine MakeMoveForm and GameForm


import logging
from google.appengine.ext import ndb
import endpoints

def inite_tables():
    time_table = []
    step_table = []

    for n in range(0,50):
        time_table.append(10)

    for val in xrange(9,1,-1):
        for n in range(0,10):
            time_table.append(val)

    for n in range(0,30):
        step_table.append(10)

    for val in xrange(9,1,-1):
        for n in range(0,20):
            step_table.append(val)

    return time_table, step_table

NUMBER_OF_PAIRS = 26
TIME_TABLE, STEP_TABLE = inite_tables()

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity




def compute_score(time, steps):
    """
    Computes the score using time and steps:
        time: 
            <50s    10     |   <100s   5
            <60s    9      |   <110s   4
            <70s    8      |   <120s   3
            <80s    7      |   <130s   2
            <90s    6      |   else    1
                            
        steps: 
            <30    10      |   <130   5
            <50    9       |   <150   4
            <70    8       |   <170   3
            <90    7       |   <190   2
            <110   6       |   else   1
    
    score = time * steps
    """

    if int(time) < 130:
        time_points = TIME_TABLE[time]
    else:
        time_points = 1

    if steps < 190:
        steps_points = STEP_TABLE[steps]
    else:
        steps_points = 1

    return time_points * steps_points




