import sys
#for data types
from sqlalchemy import Column, ForeignKey, Integer, String
#for connecting
from sqlalchemy.ext.declarative import declarative_base
#for ForeignKey relationships
from sqlalchemy.orm import relationship
#for use at the end of the configuration file
from sqlalchemy import create_engine

Base = declarative_base()

"""
The restaurant class is designed to inherit from Base
"""
class Restaurant(Base):
    #__tablename__ is special in sqlalchemy to let python know the variablename we will use for tables
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)

"""
The MenuItem class is designed to inherit from Base
"""
class MenuItem(Base):
    __tablename__ = 'menu_item'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    #creating the reference for the ForeignKey to use
    restaurant = relationship(Restaurant)

#end of file wrap up
engine = create_engine('sqlite:///restaurantmenu.db')
#adds the class to the db
Base.metadata.create_all(engine)
