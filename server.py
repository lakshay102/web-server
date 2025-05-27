from http.server import BaseHTTPRequestHandler, HTTPServer

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
        page = self.create_page()
        self.send_page(page)

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