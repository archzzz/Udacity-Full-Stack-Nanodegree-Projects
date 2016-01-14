import webbrowser

class Movie:

	# return a Movie object with a csv line
	def make_movie(entry):
		return Movie(entry[0], entry[1], entry[2])
	make_movie = staticmethod(make_movie)

	def __init__(self, title, poster_image, trailer_ytb):
		self.title = title
		self.poster_image_url = poster_image
		self.trailer_ytb_url = trailer_ytb

	# open youtube video 
	def show_trailer(self):
		webbrowser.open(self.trailer_ytb_url)

	def __str__(self):
		return "title: " + self.title + ", image: " + self.poster_image_url + ", trailer: " + self.trailer_ytb_url