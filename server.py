from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import os

class ServerException(Exception):
    """For internal error reporting."""
    pass

class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a fixed 'page'.'''

    # Page to send back.
    Page = '''\
<html>
<body>
<table>
<tr>  <td>Header</td>           <td>Value</td>          </tr>
<tr>  <td>Date and time</td>    <td>{date_time}</td>    </tr>
<tr>  <td>Client host</td>      <td>{client_host}</td>  </tr>
<tr>  <td>Client port</td>      <td>{client_port}s</td> </tr>
<tr>  <td>Command</td>          <td>{command}</td>      </tr>
<tr>  <td>Path</td>             <td>{path}</td>         </tr>
</table>
</body>
</html>
'''

    # Handle a GET request.
    def do_GET(self):
        # page = self.create_page()
        # self.send_page(page)
        try:
            # Figure out what exactly is being requested .
            full_path = os.getcwd() + self.path

            # It doesn't exist...
            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))
            
            # ...it's a file...
            elif os.path.isfile(full_path):
                self.handle_file(full_path)

            # ...it's something we don't handle.
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))
            
        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)
        
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()

            # Guess the MIME type based on file extension
            content_type, _ =  mimetypes.guess_type(full_path)
            if content_type is None:
                content_type = "application/octet-stream"

            self.send_content(content, content_type=content_type)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    Error_Page = """/
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """
    
    # Handle unknown objects.
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg).encode('utf-8')
        self.send_content(content, status=404)

    # Send actual content.
    def send_content(self, content, content_type="text/html", status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


    def create_page(self):
        # print("doing something")
        values = {
            'date_time'     : self.date_time_string(),
            'client_host'   : self.client_address[0],
            'client_port'   : self.client_address[1],
            'command'       : self.command,
            'path'          : self.path
        }
        page = self.Page.format(**values)
        return page

    def send_page(self, page):
        encoded = page.encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

#-----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()