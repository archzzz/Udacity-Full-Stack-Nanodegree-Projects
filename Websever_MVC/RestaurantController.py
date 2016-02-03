from database_setup import Restaurant
from RestaurantModel import RestaurantModel
from restaurantView import RestaurantView
from urlparse import parse_qs

class RestaurantController():

    def __init__(self):
        self.restaurantModel = RestaurantModel()
        self.restaurantView  = RestaurantView()

    def getRestaurants(self, request, response):
        # retrieve data from database
        restaurants = self.restaurantModel.getRestaurants()
        self.restaurantView.renderRestaurants(restaurants, response)

    def getRestaurant(self, request, response):
        id = parse_qs(request.query)['id'][0]
        restaurant = self.restaurantModel.getRestaurant(id)
        self.restaurantView.renderRestaurant(restaurant,response)

    def updateRestaurant(self, request, response): 
        try:          
            res_id = request.get('id')[0]
            restaurant = self.restaurantModel.getRestaurant(res_id)
            restaurant.name = request.get('name')[0]
            self.restaurantModel.updateRestaurant(restaurant)
            return "/restaurants"
        except Exception as e:
            print e


