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
    def getAllRestaurants(cls):
        restaurants = cls.session.query(Restaurant).all()
        return restaurants

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
    def getAllMenuItems(cls, restaurant_id):
        items = cls.session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
        return items

    @classmethod
    def postNewMenuItem(cls, restaurant_id, name, course, description, price):
        menuItem = MenuItem(name = name, course = course, description = description, price = price, restaurant_id = restaurant_id)
        cls.session.add(menuItem)
        cls.session.commit()

    @classmethod
    def postEditMenuItem(cls, restaurant_id, menuItem_id, name, course, description, price):
        menuItem = cls.getMenuItemByID(menuItem_id)
        menuItem.name = name
        menuItem.course = course
        menuItem.description = description
        menuItem.price = price
        menuItem.restaurant_id = restaurant_id
        cls.session.add(menuItem)
        cls.session.commit()

    @classmethod
    def getMenuItemByID(cls, id):
        menuItem = cls.session.query(MenuItem).filter_by(id = id).one()
        return menuItem

    @classmethod
    def deleteMenuItem(cls, id):
        menuItem = cls.getMenuItemByID(id)
        cls.session.delete(menuItem)
        cls.session.commit()
