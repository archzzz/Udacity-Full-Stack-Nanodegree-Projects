from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Catalog, Item, User, Base
from datetime import datetime

engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

session.query(Catalog).delete()
session.query(Item).delete()

#Init catalogs
catalog1 = Catalog(name="Books")
catalog2 = Catalog(name="Movies")

session.add(catalog1)
session.add(catalog2)
session.commit()

item1 = Item(name="Harry Potter", description="Harry Potter is a series of seven novels written by British author J. K. Rowling. The novels chronicle the life of a young wizard, Harry Potter, and his friends Hermione Granger and Ron Weasley, all of whom are students at Hogwarts School of Witchcraft and Wizardry. ", catalog=catalog1, create_time=datetime.now())
item2 = Item(name="The Godfather", description="The Godfather is a crime novel written by Italian American author Mario Puzo, originally published in 1969 by G. P. Putnam's Sons. It details the story of a fictitious Mafia family based in New York City (and Long Beach, New York), headed by Don Vito Corleone, who became synonymous with the Italian Mafia. ", catalog=catalog1 , create_time=datetime.now())

item3 = Item(name="Legend of 1900", description="The Legend of 1900 is a 1998 Italian drama film directed by Giuseppe Tornatore and starring Tim Roth, Pruitt Taylor Vince and Melanie Thierry. It was Tornatore's first English-language film.", catalog=catalog2, create_time=datetime.now())

session.add(item1)
session.add(item2)
session.add(item3)
session.commit()

print "add 2 catalogs"