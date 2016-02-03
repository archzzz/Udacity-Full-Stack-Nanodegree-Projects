from database_setup import Restaurant

class RestaurantView():

    def renderRestaurants(self, restaurants, response):
        pagePath = "templates/Restaurants.template"
        tilePath = "templates/RestaurantsTile.template"
        #load template
        with open(pagePath, "r") as pageFile:
            restaurantPage = pageFile.read()
        with open(tilePath, "r") as tileFile:
            restaurantTile = tileFile.read()

        tiles = ""
        for restaurant in restaurants:
            tiles += restaurantTile.format(restaurant_name=restaurant.name, restaurant_id=restaurant.id)
        output = restaurantPage.format(restaurant_tiles=tiles)

        response.write(output)
		#replace placeholder

    def renderRestaurant(self, restaurant, response):
        pagePath = "templates/Restaurant.template"

        with open(pagePath, "r") as pageFile:
            restaurantPage = pageFile.read()

        output = restaurantPage.format(restaurant_name=restaurant.name, restaurant_id=restaurant.id)

        response.write(output)

