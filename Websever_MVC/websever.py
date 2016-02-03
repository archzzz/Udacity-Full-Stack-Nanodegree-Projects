from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
from RestaurantController import RestaurantController

import cgi

class webseverHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.restaurantController = RestaurantController()
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        
    def do_GET(self):
        request = urlparse(self.path)
        urlpath = urlparse(self.path).path

        if urlpath.endswith("/restaurants"):
            self.restaurantController.getRestaurants(self.rfile, self.wfile)
            return

        if urlpath.endswith("/restaurant"):
            self.restaurantController.getRestaurant(request,self.wfile)
            return 

        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            output = ""
            output += "<html><body>"
            output += "Hello!"
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'><form>"
            output += "</body></html>" 

            self.wfile.write(output)
            print output
            return
        if self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            output = ""
            output += "<html><body>"
            output += "Hola! <a href = '/hello'>Back to hello </a>"
            output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'><form>"
            output += "</body></html>" 

            self.wfile.write(output)
            print output
            return
        else:
            self.send_error(404, 'File not found %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(
                self.headers.getheader('Content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

            if self.path.endswith("/update_restaurant"):
                location = self.restaurantController.updateRestaurant(fields, self.wfile)
                self.redirect("localhost:8080" + location)

        except Exception as e:
        	print e

    def redirect(self, location):
        self.send_response(301)
        self.send_header('Location', location)
        self.end_header()


def main():
    try:
        port = 8080
        sever = HTTPServer(('', port), webseverHandler)
        print "Web sever running on port %s" % port
        sever.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        sever.socket.close()

if __name__ == '__main__':
    main()
