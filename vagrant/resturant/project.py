from flask import Flask, request, redirect
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

'''
General functions
'''
def initPage():
    output = '''<html><head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    </head><body><div class=container>'''
    return output

def endPage():
    output = "</div></body></html>"
    return output
#routing
#notice status codes are no longer needed
# the @ means decorator function in python
#decorators basically mean that we access functions in an outer scope of nested functions and are able to alter them
@app.route('/')
#leanve the trailing slash because flask renders even when not there
@app.route('/restaurants/')



def homePage():
    restaurants = session.query(Restaurant).all()
    #must initialize output
    output = initPage()
    for restaurant in restaurants:
        output += "<a href='/restaurants/%s'><h1>%s</h1></a>" % (restaurant.id, restaurant.name)

    output += endPage()
    return output



@app.route('/restaurants/<int:restaurant_id>/')

def readRestaurant(restaurant_id):
    #get restaurant
    restaurant = models.RestaurantModel.getRestaurantByID(restaurant_id)
    items = models.MenuItemModel.getAllMenuItems(restaurant_id)
    output = initPage()
    output += '<h1>%s</h1>' % restaurant.name
    output += "<a href='/restaurants/%s/newMenuItem/'><button type='button'>Create New Menu Item</button></a>" % restaurant_id
    output += "<p>Click an item name to edit it</p>"
    for item in items:
        output += "<div class ='row'>"
        output += "<div class='col-md-9'><p><a href='/menuItem/%s/%s/edit'>%s</p></a></div>" % (restaurant_id, item.id, item.name)
        output += "<div class='col-md-3'><p>%s</p></div>" % item.price
        output += "</div>"
        output += "<p>%s</p>" % item.description
        output += "<a href='/menuItem/%s/%s/delete/'><button type='button'>Delete</button></a>" % (restaurant_id, item.id)
        output += '<br>'
    output += endPage()
    return output


@app.route('/restaurants/<int:restaurant_id>/newMenuItem/', methods=['GET', 'POST'])

def newMenuItem(restaurant_id):
    output = initPage()
    output += '''<form method='Post' enctype='multipart/form-data' action='/restaurants/%s/newMenuItem/'>
    <h2>New Menu Item</h2>
    <input name='restaurant_id' type='hidden' value='%s' >
    Name: <input name='name' type='text' > <br>
    Course: <input name='course' type='text' > <br>
    Price: <input name='price' type='text' > <br>
    Description: <textarea rows='9' cols='9' name='description'></textarea> <br>
    <input type='submit' value='Submit'>
    </form>
    <a href='/restaurants/%s'><button type='button'>Cancel</button></a>
    ''' % (restaurant_id, restaurant_id, restaurant_id)
    if request.method =='POST':
        models.MenuItemModel.postNewMenuItem(request.form['restaurant_id'],
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price']
                        )
    output += endPage()
    return output

@app.route('/menuItem/<int:restaurant_id>/<int:menuItem_id>/edit/', methods=['GET', 'POST'])

def editMenuItem(menuItem_id, restaurant_id):
    menuItem = models.MenuItemModel.getMenuItemByID(menuItem_id)
    output = initPage()
    output += '''<form method='Post' enctype='multipart/form-data' action='/menuItem/%s/%s/edit/'>
    <h2>Edit Menu Item</h2>
    Name: <input name='name' type='text' value='%s'> <br>
    Course: <input name='course' type='text' value='%s'> <br>
    Price: <input name='price' type='text' value='%s'> <br>
    Description: <textarea rows='9' cols='9' name='description'>%s</textarea> <br>
    <input type='submit' value='Submit'>
    </form>
    <a href='/restaurants/%s'><button type='button'>Cancel</button></a>
    ''' % (restaurant_id, menuItem_id, menuItem.name, menuItem.course, menuItem.price, menuItem.description, restaurant_id)
    if request.method =='POST':
        models.MenuItemModel.postEditMenuItem(restaurant_id,
                        menuItem_id,
                        request.form['name'],
                        request.form['course'],
                        request.form['description'],
                        request.form['price']
                        )
    output += endPage()
    return output

@app.route('/menuItem/<int:restaurant_id>/<int:menuItem_id>/delete/', methods=['GET', 'POST'])

def deleteMenuItem(menuItem_id, restaurant_id):
    menuItem = models.MenuItemModel.getMenuItemByID(menuItem_id)
    output = initPage()
    output += '''<form method='Post' enctype='multipart/form-data' action='/menuItem/%s/%s/delete/'>
    <h2>Delete Menu Item</h2>
    <h2>Are you sure that you want to delete %s?</h2>
    <input name='response' type='radio' value='yes'>Yes
    <input name='response' type='radio' value='no'>No
    <input type='submit' value='Submit'>
    </form>
    <a href='/restaurants/%s'><button type='button'>Cancel</button></a>
    ''' % (restaurant_id, menuItem_id, menuItem.name, restaurant_id)
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
    output += endPage()
    return output
if __name__ == "__main__":
    #enabling debug mode allows the server to reload itself each time it notices a change in its code
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
