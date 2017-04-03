import socket
import os
import sys
import signal


class Server:
    """ Class describing a simple HTTP server objects."""

    def __init__(self, port=8000):
        self.host = ''
        self.port = port
        self.directory = os.getcwd()
        self.serversocket = None

    def run_server(self):
        """ Attempts to get the socket and launch the server """
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:  # in case if provided in the __init__() port may be unavailable
            print("Launching HTTP server on port :", self.port)
            self.serversocket.bind((self.host, self.port))

        except socket.error as e:
            print("Warning: Could not use port:", self.port, "\n")
            print("Error: ", e)
            self.shutdown()
            sys.exit(1)

        print("Server successfully bound the socket with port:", self.port)
        print("Press Ctrl+C to shut down the server and exit.\n")
        self._wait_for_connections()

    def shutdown(self):
        """ Shut down the server """
        try:
            print("**********Shutting down the server**********")
            self.serversocket.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            print(e)

    def _gen_headers(self,  code, content=b''):
        """ Generates HTTP response Headers """
        # determine response code
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\n'
            h += 'Server: SimpleHTTPServer\n'
            h += 'Content-Length: {}'.format(len(content))
            h += 'Connection: close\n\n'  # signal that the connection wil be closed after completing the request
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\n'
            h += 'Server: SimpleHTTPServer\n'
            h += 'Connection: close\n\n'  # signal that the connection wil be closed after completing the request

        return h

    def _wait_for_connections(self):
        """ Main loop awaiting connections """
        while True:
            print("Awaiting New connection")
            self.serversocket.listen(5)  # maximum number of queued connections

            connection, address = self.serversocket.accept()

            print("Got connection from:", address)

            data = connection.recv(1024)  # receive data from client
            string = bytes.decode(data)   # decode it to string
            # determine request method
            request_method = self.get_url_and_request(string)[0]
            url = self.get_url_and_request(string)[1]
            print("Request:", string.split('\n')[0])
            path = self.directory + url

            if request_method == 'GET':
                if os.path.isdir(path):
                    response_content = self.list_directory(path, url)
                    response_headers = self._gen_headers(200, response_content)
                else:
                    # Load file content
                    try:
                        with open(path, 'rb') as file:
                                response_content = file.read()  # read file content
                        response_headers = self._gen_headers(200, response_content)

                    except FileNotFoundError as e:  # in case file was not found, generate 404 page
                        print("Warning, file not found. Serving response code 404\n", e)
                        response_headers = self._gen_headers(404)
                        response_content = b"<html><body><p>Error 404: File not found</p></body></html>"

                # Try to open index.html
                try:
                    with open(path + 'index.html', "rb") as index:
                        response_content = index.read()
                except FileNotFoundError:
                    pass
                except NotADirectoryError:
                    pass

                server_response = response_headers.encode()  # return headers for GET
                server_response += response_content

                connection.sendall(server_response)
                print("\n")
                connection.close()
            else:
                print("Unknown HTTP request method:", request_method)

    @staticmethod
    def get_url_and_request(line):
        try:
            request = line.split(' ')[0]
            url = line.split(' ')[1]
            return request, url
        except IndexError:
            return 'GET', '/'

    @staticmethod
    def list_directory(path, url):
        """ Produces a directory listing. """
        list = os.listdir(path)
        list.sort(key=lambda a: a.lower())
        result = []
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % url
        result.append('<!DOCTYPE html>')
        result.append('<html>\n<head>')
        result.append('<meta content="text/html; charset=%s">' % enc)
        result.append('<title>%s</title>\n</head>' % title)
        result.append('<body>\n<h1>%s</h1>' % title)
        result.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            result.append('<li><a href="{}">{}</a></li>'.format(linkname, displayname))
        result.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(result).encode(enc, 'surrogateescape')
        return encoded


if __name__ == '__main__':
    if len(sys.argv) == 2:
        server = Server(int(sys.argv[1]))
    else:
        server = Server()
    server.run_server()
    signal.signal(signal.SIGINT, Server.shutdown(server))  # Shutdown server if SIGINT captured

