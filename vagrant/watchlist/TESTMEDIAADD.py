from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Watchlist, Base, Media

engine = create_engine('sqlite:///Watchlists.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
media = session.query(Media).all()
for medium in media:
    session.delete(medium)
    session.commit()
print 'Previous items deleted'
game_of_thrones = Media(name="Game of Thrones", imdb_id = int('0944947'), type = "TV Show", rating = int('2'),
                comments="An amazing show", watchlist_id= int('1'), user_id="1")

seinfeld = Media(name="Seinfeld", imdb_id = int('0098904'), type = "TV Show", rating = int('2'),
                comments="An amazing show", watchlist_id= int('1'), user_id="1")

session.add(game_of_thrones)
session.add(seinfeld)
session.commit()


print "added media items!"
