	Simple implementation of HTTP server serving files relative to the current directory.

	If the request was mapped to a directory, the directory is checked for a file 
named index.html. If found, the file’s contents are returned; otherwise a 
directory listing is generated.
	
	If the request was mapped to a file, it is opened and the contents are returned.

	Server can be invoked with a port number argument:
	```python
	python main.py 8000
	```
	By default port 8000 is used.

	By default, server binds itself to all interfaces.
