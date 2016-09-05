#sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem



class RestaurantModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    @classmethod
    def getRestaurantByID(cls, restaurant_id):
        restaurant = cls.session.query(Restaurant).filter_by(id = restaurant_id).one()
        return restaurant

class MenuItemModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    @classmethod
    def postNewMenuItem(cls, restaurant_id, name, course, description, price):
        menuItem = MenuItem(name = name, course = course, description = description, price = price, restaurant_id = restaurant_id)
        cls.session.add(menuItem)
        cls.session.commit()
