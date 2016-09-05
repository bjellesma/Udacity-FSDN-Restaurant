from flask import Flask
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
@app.route('/restaurants')



def homePage():
    restaurants = session.query(Restaurant).all()
    #must initialize output
    output = initPage()
    for restaurant in restaurants:
        output += "<a href='/restaurants/%s'><h1>%s</h1></a>" % (restaurant.id, restaurant.name)

    output += endPage()
    return output

def initPage():
    output = '''<html><head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    </head><body><div class=container>'''
    return output

def endPage():
    output = "</div></body></html>"
    return output

@app.route('/restaurants/<int:restaurant_id>/')

def readRestaurant(restaurant_id):
    #get restaurant
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    output = initPage()
    output += '<h1>%s</h1>' % models.RestaurantModel.getRestaurantByID(restaurant_id).name
    for item in items:
        output += "<div class ='row'>"
        output += "<div class='col-md-9'><p>%s</p></div>" % item.name
        output += "<div class='col-md-3'><p>%s</p></div>" % item.price
        output += "</div>"
        output += "<p>%s</p>" % item.description
        output += '<br>'
    output += endPage()
    return output

if __name__ == "__main__":
    #enabling debug mode allows the server to reload itself each time it notices a change in its code
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
