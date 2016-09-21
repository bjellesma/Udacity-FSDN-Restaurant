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

restaurants = session.query(Restaurant).all()
print ''
print 'restaurants'
print '______'
for restaurant in restaurants:
    print restaurant.name

items = session.query(MenuItem).all()
print ''
print 'items'
print '______'
for item in items:
    print item.name
