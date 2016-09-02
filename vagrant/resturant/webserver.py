from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#cgi is common gateway interface
import cgi

"""
The follow is all the information for sqlalchemy
"""
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
"""
"""

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #splits path by ? so that url parameters are handled
        p = self.path.split("?")
        path = p[0]
        URLparams = {}
        if len(p) > 1:
            URLparams = p[1].split("&")
        if path == "/restaurants":
            #status code 200 indicates successful get request
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #create the restaurants to contain all of the restaurants in the db
            restaurants = session.query(Restaurant).all()

            message = ""
            message += "<html><title>Restaurants</title><body>"
            message += "<p>If you'd like, you may create a <a href='/restaurants/new'>new</a> Restaurant</p>"
            for restaurant in restaurants:
                message += "<br>"
                message += "<br>"
                message += "Restaurant Name: %s" % restaurant.name
                message += "<br>"
                message += "<a href='/restaurants/edit?%s'>Edit</a>" % restaurant.id
                message += "<br>"
                message += "<a href='/restaurants/delete?%s'>Delete</a>" % restaurant.id
                message += "<br>"
                message += "<br>"
            self.wfile.write(message)
            return
        elif self.path == "/restaurants/new":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #create the restaurants to contain all of the restaurants in the db
            restaurants = session.query(Restaurant).all()

            message = ""
            message += "<html><title>Create</title><body>"
            message += '''<form method='Post' enctype='multipart/form-data' action='/restaurants/new'>
            <h2>What would you like the name of the new Restaurant to be?</h2>
            <input name='name' type='text' >
            <input type='submit' value='Submit'>
            </form>
            '''

            self.wfile.write(message)
            return
        elif path == "/restaurants/edit":

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #so python doesn't complain
            name = ''

            if URLparams:
                if len(URLparams) == 1:
                    id = URLparams[0]
                elif len(URLparams) == 2:
                    idPair = URLparams[0].split('=')
                    id = idPair[1]
                    namePair = URLparams[1].split('=')
                    name = namePair[1]
                else:
                    self.send_error(403, 'Not Accessible: %s' % self.path)
            #create the restaurants to contain all of the restaurants in the db
            restaurant = session.query(Restaurant).filter_by(id = id).one()
            if name:
                restaurant.name = name
                session.add(restaurant)
                session.commit()
            message = ""
            message += "<html><title>Update</title><body>"
            message += '''<form method='get' enctype='multipart/form-data' action='/restaurants/edit'>
            <h2>What would you like the name of the new Restaurant to be now?</h2>
            <input name='id' type='hidden' value='%s'>
            <input name='name' type='text' >
            <input type='submit' value='Submit'>
            </form>
            ''' % id

            self.wfile.write(message)
            return
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:

            #status code 301 indicates successful get request
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #ctype is main values and pdict are a dictionary of parameters that we send
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            #if the main value is form-data
            if ctype == 'multipart/form-data':
                #use the fields variable to parse out the dictionary of parameters that we've sent
                #messagecontent will be an array
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('name')
            output = ""
            output += "<html><body>"
            output += " <h2>Here is the name of your restaurant: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += "Go back to <a href='/restaurants'>restaurants</a> to view it"
            restaurant = Restaurant(name = messagecontent[0])
            #addming new item to staging area
            session.add(restaurant)
            #commiting changes to database
            session.commit()
            self.wfile.write(output)
            print output
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        #serve_forever will keep there server constantly listening
        server.serve_forever()
    #triggered with ctrl+c
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
