#sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Watchlist, Media, Users
#IMDb imports
import imdb

class WatchlistModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///Watchlists.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    @classmethod
    def getAllWatchlists(cls):
        watchlists = cls.session.query(Watchlist).all()
        return watchlists

    @classmethod
    def getWatchlistByID(cls, watchlist_id):
        watchlist = cls.session.query(Watchlist).filter_by(id = watchlist_id).one()
        return watchlist

    @classmethod
    def postNewWatchlist(cls, name, user_id):
        watchlist = Watchlist(name = name, user_id = user_id)
        cls.session.add(watchlist)
        cls.session.commit()

class MediaModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///Watchlists.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    #IMDb object
    imdbObj = imdb.IMDb()

    @classmethod
    def getAllMediaItems(cls, watchlist_id):
        items = cls.session.query(Media).filter_by(watchlist_id = watchlist_id)
        return items

    @classmethod
    def postNewMedia(cls, watchlist_id, name, art, imdb_id, rating, comments, type, user_id):
        media = Media(name = name, rating = rating, art = art, imdb_id = imdb_id, comments = comments, watchlist_id = watchlist_id, type = type, user_id = user_id)
        cls.session.add(media)
        cls.session.commit()

    @classmethod
    def postEditMedia(cls, watchlist_id, media_id, name, rating, comments):
        media = cls.getMediaByID(media_id)
        media.name = name
        media.course = course
        media.description = description
        media.price = price
        media.restaurant_id = restaurant_id
        cls.session.add(media)
        cls.session.commit()

    @classmethod
    def getMediaByID(cls, id):
        media = cls.session.query(Media).filter_by(id = id).one()
        return media

    @classmethod
    def deleteMedia(cls, id):
        media = cls.getMediaByID(id)
        cls.session.delete(media)
        cls.session.commit()

    #IMDb info
    @classmethod
    def getIMDBbyID(cls, id):
        obj = cls.imdbObj.get_movie(id)
        return obj

    @classmethod
    def searchIMDBbyMovie(cls, movie, searchInt):
        result = cls.imdbObj.search_movie(movie)
        id = result[0].movieID
        return id

    @classmethod
    def getIMDBcoverById(cls, id):
        obj = cls.getIMDBbyID(id)
        return obj['cover']

class UsersModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///Watchlists.db')
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

class PasswordsModel():
    #sqlalchemy code
    engine = create_engine('sqlite:///Watchlists.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    @classmethod
    def getPasswordById(cls, id):
        user = cls.session.query(Password).filter_by(user_id = id).one()
        return user.password

    @classmethod
    def getSaltById(cls, id):
        user = cls.session.query(Password).filter_by(user_id = id).one()
        return user.salt
