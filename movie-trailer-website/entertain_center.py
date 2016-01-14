import media
import fresh_tomato
import csv
from media import Movie

# read movie informations from movies_info.csv, and store in a list movies
with open('movies_info.csv', 'rb') as csvfiles:
	movies = map(lambda entry:Movie.make_movie(entry), csv.reader(csvfiles, delimiter=","))

# 
fresh_tomato.open_movies_page(movies)