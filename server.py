from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import os
import subprocess

class ServerException(Exception):
    """For internal error reporting."""
    pass

class case_cgi_file(object):
    '''Something runnable.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')
    
    def act(self, handler):
        handler.run_cgi(handler.full_path)

class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
    
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(object):
    '''Serve listing for a directory without an index.html page.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_no_file(object):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)
    
    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))
    
class case_existing_file(object):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)
    
    def act(self, handler):
        handler.handle_file(handler.full_path)

class case_always_fail(object):
    '''Base case if nothing else worked.'''

    def test(self, handler):
        return True
    
    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

class RequestHandler(BaseHTTPRequestHandler):
    # '''Handle HTTP requests by returning a fixed 'page'.'''
    '''
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    '''

    Cases = [
            case_no_file,
            case_cgi_file,
            case_existing_file,
            case_directory_index_file,
            case_directory_no_index_file,
            case_always_fail
        ]

#     # Page to send back.
#     Page = '''\
# <html>
# <body>
# <table>
# <tr>  <td>Header</td>           <td>Value</td>          </tr>
# <tr>  <td>Date and time</td>    <td>{date_time}</td>    </tr>
# <tr>  <td>Client host</td>      <td>{client_host}</td>  </tr>
# <tr>  <td>Client port</td>      <td>{client_port}s</td> </tr>
# <tr>  <td>Command</td>          <td>{command}</td>      </tr>
# <tr>  <td>Path</td>             <td>{path}</td>         </tr>
# </table>
# </body>
# </html>
# '''

    # Handle a GET request.
    def do_GET(self):
        # page = self.create_page()
        # self.send_page(page)
        try:
            # Figure out what exactly is being requested .
            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

        #     # It doesn't exist...
        #     if not os.path.exists(full_path):
        #         raise ServerException("'{0}' not found".format(self.path))
            
        #     # ...it's a file...
        #     elif os.path.isfile(full_path):
        #         self.handle_file(full_path)

        #     # ...it's something we don't handle.
        #     else:
        #         raise ServerException("Unknown object '{0}'".format(self.path))
            
        # # Handle errors.
        # except Exception as msg:
        #     self.handle_error(msg)
        
    def run_cgi(self, full_path):
    
        try:
            print("Running CGI:", full_path)
            result = subprocess.run(
                ["python", full_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("CGI stdout:", result.stdout)
            print("CGI stderr:", result.stderr)
            if result.returncode == 0:
                self.send_content(result.stdout)
            else:
                self.handle_error(result.stderr)
        except Exception as e:
            self.handle_error(str(e))

        
        # child_stdin, child_stdout = os.popen2(cmd)
        # child_stdin.close()
        # data = child_stdout.read()
        # child_stdout.close()
        # self.send_content(data)

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
        self.send_header("Content-type", content_type)
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

    # How to display a directory listing.
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''
    
    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = [f'<li><a href="{e}">{e}</a></li>'for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets)).encode('utf-8')
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)
            

#-----------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()