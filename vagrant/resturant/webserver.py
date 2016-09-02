from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#cgi is common gateway interface
import cgi

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/hello"):
            #status code 200 indicates successful get request
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = ""
            message += "<html><body>Hello!</body></html>"
            message += "<form method='Post' enctype='multipart/form-data' action='/hello'><h2>What do you want to post to the server?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
            self.wfile.write(message)
            #used for debugging
            print message
            return
        elif self.path.endswith("/hola"):
            #status code 200 indicates successful get request
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = ""
            message += "<html><body>Hola Mi Amigo</body></html>"
            message += "<form method='Post' enctype='multipart/form-data' action='/hello'><h2>What do you want to post to the server?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form></body></html>"
            self.wfile.write(message)
            #used for debugging
            print message
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
                messagecontent = fields.get('message')
            output = ""
            output += "<html><body>"
            output += " <h2>Here is the form data: </h2"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you want to post to the server?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
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
