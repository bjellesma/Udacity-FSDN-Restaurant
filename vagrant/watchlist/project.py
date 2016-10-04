from flask import Flask, request, redirect, render_template, flash, jsonify, make_response
#create instance of flask class with the name of the app


#app imports
import models
import secure
import functions

#cookies
import datetime

#modules for oauth security
#notice that we can't use session because we're already using it so we use the keyword as
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

#sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Watchlist, Media

app = Flask(__name__)

#open and read JSON file with client secrets
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Watchlist Application"

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = models.UsersModel.getUserID(data["email"])
    if not user_id:
        user_id = models.UsersModel.createUser(login_session)
    login_session['user_id'] = user_id
    return redirect('/')

#diconnect user
#TODO this function is only used for testing. disconnecting should be done on the /disconnect page
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    #verify state to prevent csrf
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    login_session['provider'] = 'facebook'

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = models.UsersModel.getUserID(login_session['email'])
    if not user_id:
        user_id = models.UsersModel.createUser(login_session)
    login_session['user_id'] = user_id
    return redirect('/')


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['state']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            #TODO find out why we can't delete provider
            login_session['provider'] = ''
            #credentials are deleted by google
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['access_token']
            del login_session['state']
            del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
        if login_session['provider'] == 'watchlist':
            del login_session['username']
            del login_session['state']
            del login_session['email']
            del login_session['provider']
            #set cookie
            #we need to set the cookie in here or else it will not set properly
            response = make_response(redirect('/'))
            response.set_cookie(
                'Watchlist-login',
                '%s=' % 'user_id')
            return response
        return redirect('/')
    else:
        return redirect('/')

#sqlalchemy code
engine = create_engine('sqlite:///Watchlists.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#JSON route
#JSON allows applications to easily parse data with the html and css as extra bandwidth
#JSON is useful for creating APIs because it parses the pure data in a low bandwidth format
@app.route('/watchlist/<int:watchlist_id>/JSON')
def watchlistJSON(watchlist_id):
    watchlist = models.WatchlistModel.getWatchlistByID(watchlist_id)
    media = models.MediaModel.getAllMedia(watchlist_id)
    return jsonify(Media=[i.serialize for i in items])

@app.route('/watchlists/<int:watchlist_id>/media/<int:media_id>/JSON')
def mediaJSON(watchlist_id, media_id):
    media = models.MediaModel.getMediaByID(media_id)
    return jsonify(Media=[item.serialize])

@app.route('/login', methods=['GET'])

def showLogin():
    #the state variable will be 32 characters and be a mix of uppercase letters and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('/login.html', STATE=state)

@app.route('/login', methods=['POST'])
def postLogin():
    email = request.form['email']
    password = request.form['password']

    successful_login = models.UsersModel.login(email, password)

    #if we were able to validate the user
    #login the user and direct them to the main page
    #refers to the login handler function
    #you can also tell by the parameters
    if successful_login:
        #set session
        login_session['provider'] = 'watchlist'
        login_session['username'] = successful_login.username
        login_session['email'] = successful_login.email
        #set cookie
        #we need to set the cookie in here or else it will not set properly
        response = make_response(redirect('/'))
        cookie_val = functions.make_secure_val(successful_login.id)
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=90)
        response.set_cookie(
            'Watchlist-login',
            '%s=%s' % ('user_id', cookie_val),
            expires=expire_date)
        return response

    #else, spit out the errors
    if not successful_login:
        flash('That username and/or password is invalid')
        return render_template('/login.html')

@app.route('/register', methods=['GET'])
def getRegister():
    return render_template('/register.html')

@app.route('/register', methods=['POST'])
def postRegister():
    #assume no error
    have_error = False
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    email = request.form['email']

    notUniqueUser = models.UsersModel.checkUserName(username)

    params = dict(username = username,
                      email = email)

    if not functions.valid_username(username):
        params['error_username'] = "That's not a valid username."
        have_error = True

    if not functions.valid_password(password):
        params['error_password'] = "That wasn't a valid password."
        have_error = True
    elif password != verify:
        params['error_verify'] = "Your passwords didn't match."
        have_error = True

    if not functions.valid_email(email):
        params['error_email'] = "That's not a valid email."
        have_error = True

    if notUniqueUser:
        params['user_conflict'] = "That user already exists. Please pick another username"
        have_error = True

    if have_error:
        return render_template('/register.html', params = params)
    else:
        user = models.UsersModel.register(username, password, email)
        models.UsersModel.login(user.username, password)
        return redirect ('/login')
#routing
#notice status codes are no longer needed
# the @ means decorator function in python
#decorators basically mean that we access functions in an outer scope of nested functions and are able to alter them
@app.route('/')

#leanve the trailing slash because flask renders even when not there
@app.route('/watchlists/')



def homePage():

    uid = functions.read_secure_cookie('user_id')
    user = uid and models.UsersModel.getUserById(int(uid))

    if models.UsersModel.isLoggedIn(login_session):
        user = models.UsersModel.getUserInfo(models.UsersModel.getUserID(login_session['email']))
    else:
        user = None
    '''if 'username' not in login_session:
        username = "Sign in"
        provider = ''
    else:
        username = login_session['username']
        provider = login_session['provider']
        '''
    watchlists = models.WatchlistModel.getAllWatchlists()
    #TODO login session is test code
    return render_template('/index.html', watchlists = watchlists, user = user, login_session = login_session)



@app.route('/watchlists/new/', methods=['GET', 'POST'])
def getNewWatchlist():
    #if user is logged in
    if 'username' not in login_session:
        return redirect ('/login')
    else:
        user_email = login_session['email']
        user_id = models.UsersModel.getUserID(user_email)
    if request.method =='POST':
        models.WatchlistModel.postNewWatchlist(request.form['name'],
                        request.form['user_id']
                        )
        flash("%s has been created" % request.form['name'])
    return render_template('newWatchlist.html', user_id = user_id)

@app.route('/watchlists/<int:watchlist_id>/')

def getWatchlist(watchlist_id):
    #get watchlist
    watchlist = models.WatchlistModel.getWatchlistByID(watchlist_id)
    media = models.MediaModel.getAllMediaItems(watchlist_id)
    return render_template('watchlist.html', watchlist = watchlist, items = media)


@app.route('/watchlists/<int:watchlist_id>/newMedia/', methods=['GET'])

def newMedia(watchlist_id):
    #if user is logged in
    if 'username' not in login_session:
        return redirect ('/login')
    else:
        user_email = login_session['email']
        user_id = models.UsersModel.getUserID(user_email)
    if request.method =='GET':
        #for a get variable, it's a lot easier to tell if it exists
        if request.args.get('id') and request.args.get('title') and request.args.get('art'):
            imdb_id = request.args.get('id')
            imdb_title = request.args.get('title')
            imdb_art = request.args.get('art')
        else:
            imdb_id = ''
            imdb_title = ''
            imdb_art = 'http://placehold.it/350x150'
        flash("%s has been created" % request.form['name'])
    return render_template('newMedia.html', watchlist_id = watchlist_id, user_id = user_id, imdb_id = imdb_id, imdb_title = imdb_title, imdb_cover = imdb_art)

@app.route('/watchlists/<int:watchlist_id>/newMedia/', methods=['POST'])
def postNewMedia(watchlist_id):
    if request.method =='POST':
        models.MediaModel.postNewMedia(watchlist_id,
                        request.form['name'],
                        request.form['imdb_id'],
                        request.form['imdb_art'],
                        request.form['rating'],
                        request.form['comments'],
                        request.form['type'],
                        request.form['user_id']
                        )
    return redirect("/watchlists/%s" % watchlist_id, code=200)

@app.route('/watchlists/<int:watchlist_id>/newMedia/search', methods=['GET'])
def getNewSearchMedia(watchlist_id):
    return render_template('newSearchMedia.html', watchlist_id = watchlist_id)

@app.route('/watchlists/<int:watchlist_id>/newMedia/search', methods=['POST'])
def postNewSearchMedia(watchlist_id):
    movieID = models.MediaModel.searchIMDBbyMovie(request.form['title'], int(request.form['searchInt']))
    movieInfo = models.MediaModel.getIMDBbyID(int(movieID))
    return jsonify({
        'title': movieInfo['title'],
        'cover': movieInfo['cover'],
        'id': movieID,
        'description': movieInfo['plot summary']
    })

@app.route('/media/<int:watchlist_id>/<int:media_id>/edit/', methods=['GET', 'POST'])

def editMedia(media_id, watchlist_id):
    media = models.MediaModel.getMediaByID(media_id)
    if request.method =='POST':
        models.MediaModel.postEditMedia(watchlist_id,
                        media_id,
                        request.form['name'],
                        request.form['rating'],
                        request.form['comments']
                        )
        flash("%s has been Updated" % media.name)
    return render_template('editMedia.html', watchlist_id = watchlist_id, media=media)

@app.route('/media/<int:watchlist_id>/<int:media_id>/delete/', methods=['GET', 'POST'])

def deleteMedia(media_id, watchlist_id):
    media = models.MediaModel.getMediaByID(media_id)
    if request.method =='POST':
        if request.form['response'] =='yes':
            models.MediaModel.deleteMedia(media_id)


        flash("%s has been deleted" % media.name)
        return redirect("/watchlists/%s" % watchlist_id, code=200)
    return render_template('deleteMedia.html', watchlist_id = watchlist_id, media=media)
if __name__ == "__main__":
    app.secret_key = secure.secret
    #enabling debug mode allows the server to reload itself each time it notices a change in its code
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
