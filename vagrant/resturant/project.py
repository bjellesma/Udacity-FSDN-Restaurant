from flask import Flask, request, redirect, render_template
#create instance of flask class with the name of the app
app = Flask(__name__)

#app imports
import models

#sqlalchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#sqlalchemy code
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#routing
#notice status codes are no longer needed
# the @ means decorator function in python
#decorators basically mean that we access functions in an outer scope of nested functions and are able to alter them
@app.route('/')
#leanve the trailing slash because flask renders even when not there
@app.route('/restaurants/')



def homePage():
    restaurants = models.RestaurantModel.getAllRestaurants()
    return render_template('/index.html', restaurants = restaurants)


@app.route('/restaurants/<int:restaurant_id>/')

def getRestaurants(restaurant_id):
    #get restaurant
    restaurant = models.RestaurantModel.getRestaurantByID(restaurant_id)
    items = models.MenuItemModel.getAllMenuItems(restaurant_id)
    return render_template('restaurants.html', restaurant = restaurant, items = items)


@app.route('/restaurants/<int:restaurant_id>/newMenuItem/', methods=['GET', 'POST'])

def newMenuItem(restaurant_id):

    if request.method =='POST':
        models.MenuItemModel.postNewMenuItem(request.form['restaurant_id'],
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price']
                        )
    return render_template('newMenuItem.html', restaurant_id = restaurant_id)

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
    return render_template('deleteMenuItem.html', restaurant_id = restaurant_id, menuItem=menuItem)
if __name__ == "__main__":
    #enabling debug mode allows the server to reload itself each time it notices a change in its code
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
