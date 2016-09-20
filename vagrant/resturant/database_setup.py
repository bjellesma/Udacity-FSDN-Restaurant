import sys
#for data types
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Text
#for connecting
from sqlalchemy.ext.declarative import declarative_base
#for ForeignKey relationships
from sqlalchemy.orm import relationship
#for use at the end of the configuration file
from sqlalchemy import create_engine


Base = declarative_base()



"""
The Users class is designed to inherit from Base
"""
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(80), nullable = False)

"""
The watchlist class is designed to inherit from Base
"""
class Watchlist(Base):
    #__tablename__ is special in sqlalchemy to let python know the variablename we will use for tables
    __tablename__ = 'watchlist'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

"""
The Media class is designed to inherit from Base
"""
class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key = True)
    name = Column(String(250))
    imdb_id = Column(Integer)
    type = Column(Enum("Movie", "TV Show"))
    rating = Column(String(250))
    comments = Column(Text)
    watchlist_id = Column(Integer, ForeignKey('watchlist.id'))
    #creating the reference for the ForeignKey to use
    watchlist = relationship(Watchlist)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'imdb_id': self.imdb_id,
            'type': self.type,
            'rating': self.rating,
            'comments': self.comments
        }

#end of file wrap up
engine = create_engine('sqlite:///Watchlists.db')
#adds the class to the db
Base.metadata.create_all(engine)
