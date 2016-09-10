#sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, Users



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
    def postNewMenuItem(cls, restaurant_id, name, course, description, price, user_id):
        menuItem = MenuItem(name = name, course = course, description = description, price = price, restaurant_id = restaurant_id, user_id = user_id)
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

class UsersModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    '''
    isLoggedIn will return a boolean true if the user is logged in or false if they are not a user
    '''
    @classmethod
    def isLoggedIn(cls, login_session):
        #since we require email, a logged in user will always have an email address
        if 'email' in login_session:
            return True
        else:
            return False

    @classmethod
    def createUser(cls, login_session):
        newUser = Users(name=login_session['username'], email=login_session[
                       'email'], picture=login_session['picture'])
        cls.session.add(newUser)
        cls.session.commit()
        user = cls.session.query(Users).filter_by(email=login_session['email']).one()
        return user.id

    @classmethod
    def getUserInfo(cls, user_id):
        user = cls.session.query(Users).filter_by(id=user_id).one()
        return user

    @classmethod
    def getUserID(cls, email):
        try:
            user = cls.session.query(Users).filter_by(email=email).one()
            return user.id
        except:
            return None
