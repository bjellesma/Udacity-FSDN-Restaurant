from sqlalchemy import create_engine
#we need sessionmaker in order to perform queries
from sqlalchemy.orm import sessionmaker
#importing previously made files
from database_setup import Base, Restaurant, MenuItem
#creating sqlite3 engine
engine = create_engine('sqlite:///restaurantmenu.db')
#connecting to db file
Base.metadata.bind = engine
#starting session with engine
DBSession = sessionmaker(bind = engine)
#creating instance of DBsession
session = DBSession()
entity = raw_input('What type of item would you like to create (Choices: restaurant, menuitem): ')
if entity == 'restaurant':
    #in python 2.7, we need to use raw_input
    name = raw_input('What is the name of the restaurant: ')

    restaurant = Restaurant(name = name)
    #addming new item to staging area
    session.add(restaurant)
    #commiting changes to database
    session.commit()
elif entity == 'menuitem':
    #in python 2.7, we need to use raw_input
    name = raw_input('What is the name of the menu item: ')
    description = raw_input('What is the description: ')
    course = raw_input('Which course is this: ')
    price = raw_input('What is the price of the menu item: ')
    restaurant = raw_input('What is the restaurant this item belongs to: ')

    menu_item = MenuItem(name = name, description = description, course = course, price = price, restaurant = Restaurant(name = restaurant))
    session.add(menu_item)
    session.commit()

else:
    print "answer not recognized. Exiting"
