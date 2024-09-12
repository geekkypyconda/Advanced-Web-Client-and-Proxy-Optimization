# Advanced-Web-Client-and-Proxy-Optimization

## Project Overview
-------------------

This assignment is entirely based on the Python programming language. The project is divided into four parts: Client, Proxy, Server, and Extended Client.

### How to Run the Client.py
---------------------------

#### Connecting through normal web server:

1. Run the command: `python3 Client.py {hostname/IP of website} {Port number of the website} {Path}`
2. The client will send a GET request for the base HTML file.
3. After receiving the HTML file, the client will send a GET request one by one for all objects (except links) in the HTML file.
4. For each object, the client will check the status code in the response from the server. If the status code is 200, the client will save the object. Otherwise, it will handle the status code and print the respective comment.
5. The client saves the downloaded objects in the `download` folder.

#### Connecting through proxy:

1. Run the proxy program in a terminal by executing: `python3 Proxy.py`
2. Run the client on another terminal by executing: `python3 Client.py {hostname/IP of website} {Port number of the website} {IP of Proxy server} {Port of Proxy server} {Path}`
3. The client will send a GET request for the base HTML file through the proxy server.
4. After receiving the HTML file, the client will send a GET request one by one for all objects (except links) in the HTML file by establishing a connection through the proxy each time.
5. For each object, the client will check the status code in the response from the server. If the status code is 200, the client will save the object. Otherwise, it will handle the status code and print the respective comment.
6. The client saves the downloaded objects in the `download` folder.

### How to Run the Proxy.py
---------------------------

1. Run the proxy program in a terminal by executing: `python3 Proxy.py`
2. The proxy will create a socket and start listening on PORT 12002.
3. When a client connects to the proxy, the proxy creates a new thread for each client connection.
4. When the proxy receives a request from the client, it parses the request and gets the hostname and port number of the web server hosting the required file and also the path to that file.
5. The proxy creates a new socket to establish a connection between the proxy and web server using the hostname and port number it parsed earlier. The proxy sends the request to the web server through this connection.
6. When the proxy receives a response from the web server, it parses the response and modifies the header by adding a new header line containing the IP address of the proxy.
7. The proxy sends this new modified response to the client.
8. When the proxy receives no further response from the web server, it closes the connection with both the web server and client.

### How to Run the Server.py
---------------------------

1. Run the command: `python3 Server.py`
2. The server will start listening on PORT 12001.
3. When a client connects to the web server, the web server makes a new thread for each client and serves each client in a new thread.
4. If the file requested by the client is present, the server will send the file to the client with headers (including the 200 OK response).
5. If the file is not present, the server will send a "404 NOT FOUND" response to the client.
6. After this, the connection to the server from the client is closed.

### How to Run the ExtendedClient.py
-----------------------------------

1. Run the command: `python3 ExtendedClient.py {hostname/IP of website} {Port number of the website} {Path}`
2. The client will send a GET request for the base HTML file.
3. After receiving the HTML file, the client will send a GET request one by one for all objects (except links) in the HTML file. The client will use parallel TCP connections to get the objects.
4. For each object, the client will check the status code in the response from the server. If the status code is 200, the client will save the object. Otherwise, it will handle the status code and print the respective comment.
5. The client saves the downloaded objects in the `Parallel_download` folder.
