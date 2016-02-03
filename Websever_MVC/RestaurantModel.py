from Database import Restaurant, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class RestaurantModel():
    session = None
    def __init__(self):
        engine = create_engine('sqlite:///restaurantmenu.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def getRestaurants(self):
        # database query
        return self.session.query(Restaurant).all()

    def getRestaurant(self, id):
        return self.session.query(Restaurant).filter_by(id = id).one()

    def updateRestaurant(self, restaurant):
        self.session.add(restaurant)
        self.session.commit()