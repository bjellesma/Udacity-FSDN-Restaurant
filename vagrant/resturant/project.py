from flask import Flask, request, redirect, render_template, flash, jsonify
#create instance of flask class with the name of the app


#app imports
import models
import secure

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
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

#open and read JSON file with client secrets
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token match on client and server side
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        #return says the function will not proceed if it gets this
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Exchange the authorization code for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        #return says the function will not proceed if it gets this
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
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    #data should now contain all of the values that we are interested in
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #check if user exists
    #if user does not exist, we will put them into the database
    if models.UsersModel.getUserID([login_session['email']]) is None:
        models.UsersModel.createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#diconnect user
@app.route('/gdisconnect')
def gdisconnect():
    #only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        #the token was received
    access_token = credentials.access_token
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['credentials']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

#sqlalchemy code
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#JSON route
#JSON allows applications to easily parse data with the html and css as extra bandwidth
#JSON is useful for creating APIs because it parses the pure data in a low bandwidth format
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = models.RestaurantModel.getRestaurantByID(restaurant_id)
    items = models.MenuItemModel.getAllMenuItems(restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menuItem_id>/JSON')
def menuItemJSON(restaurant_id, menuItem_id):
    item = models.MenuItemModel.getMenuItemByID(menuItem_id)
    return jsonify(MenuItems=[item.serialize])

@app.route('/login')

def showLogin():
    #the state variable will be 32 characters and be a mix of uppercase letters and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('/login.html', STATE=state)

#routing
#notice status codes are no longer needed
# the @ means decorator function in python
#decorators basically mean that we access functions in an outer scope of nested functions and are able to alter them
@app.route('/')
#leanve the trailing slash because flask renders even when not there
@app.route('/restaurants/')



def homePage():
    #TODO test code
    if 'username' not in login_session:
        username = "Sign in"
    else:
        username = login_session['username']
    restaurants = models.RestaurantModel.getAllRestaurants()
    return render_template('/index.html', restaurants = restaurants, username = username)


@app.route('/restaurants/<int:restaurant_id>/')

def getRestaurants(restaurant_id):
    #get restaurant
    restaurant = models.RestaurantModel.getRestaurantByID(restaurant_id)
    items = models.MenuItemModel.getAllMenuItems(restaurant_id)
    return render_template('restaurants.html', restaurant = restaurant, items = items)


@app.route('/restaurants/<int:restaurant_id>/newMenuItem/', methods=['GET', 'POST'])

def newMenuItem(restaurant_id):
    #if user is logged in
    if 'username' not in login_session:
        return redirect ('/login')
    else:
        user_email = login_session['email']
        user_id = models.UsersModel.getUserID(user_email)
    if request.method =='POST':
        models.MenuItemModel.postNewMenuItem(request.form['restaurant_id'],
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price'],
                        request.form['user_id']
                        )
        flash("%s has been created" % request.form['name'])
    return render_template('newMenuItem.html', restaurant_id = restaurant_id, user_id = user_id)

@app.route('/menuItem/<int:restaurant_id>/<int:menuItem_id>/edit/', methods=['GET', 'POST'])

def editMenuItem(menuItem_id, restaurant_id):
    menuItem = models.MenuItemModel.getMenuItemByID(menuItem_id)
    if request.method =='POST':
        models.MenuItemModel.postEditMenuItem(restaurant_id,
                        menuItem_id,
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price']
                        )
        flash("%s has been Updated" % menuItem.name)
    return render_template('editMenuItem.html', restaurant_id = restaurant_id, menuItem=menuItem)

@app.route('/menuItem/<int:restaurant_id>/<int:menuItem_id>/delete/', methods=['GET', 'POST'])

def deleteMenuItem(menuItem_id, restaurant_id):
    menuItem = models.MenuItemModel.getMenuItemByID(menuItem_id)
    if request.method =='POST':
        if request.form['response'] =='yes':
            models.MenuItemModel.deleteMenuItem(menuItem_id)
            redirect("/restaurants/%s" % restaurant_id, code=200)
        elif request.form['response'] == 'no':
            redirect("/restaurants/s" % restaurant_id, code=200)
        models.MenuItemModel.postEditMenuItem(restaurant_id,
                        menuItem_id,
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price']
                        )
        flash("%s has been deleted" % menuItem.name)
    return render_template('deleteMenuItem.html', restaurant_id = restaurant_id, menuItem=menuItem)
if __name__ == "__main__":
    app.secret_key = secure.secret
    #enabling debug mode allows the server to reload itself each time it notices a change in its code
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
