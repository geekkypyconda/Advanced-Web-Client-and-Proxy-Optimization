from ast import Bytes       #Library for processig bytes in Python
import socket               # Library for using socket in python
import threading            # Library for using multithreading
import random               # Library for using random in python
import subprocess

# Function for printing an object
def println(object):
    # A Simple Function to print and going to the next line
    print(f"{object}\n")


# variables for Host,PORT and  client Number
host_addr_info = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
Host = host_addr_info.split()[0]
localHost = "127.0.0.1"
fixedPORT = 12001
clientNo = 0

#Creating the socket for the server
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind((Host,fixedPORT))
serverSocket.listen(5)

println(f"Server is listening on {Host}:{fixedPORT}")


# A new Thread for the client
def connectionWithClient(clientSocket,clientAddress,clientNumber):
  
    # Keep Listening from the client
    while True:
        byteMessage = clientSocket.recv(1024)       #Receiving message from the client
        println(f"Request Received from Client No . {clientNumber} with address : {clientAddress}")
        println(f"Request = : {byteMessage.decode()}")
        requestLines = byteMessage.decode().split("\n")

        # Check if you have not got a BAD request
        if requestLines is not None:
            url = requestLines[0].split()[1]
            if '//' in url:
                host_name = url.split('//')[1].split('/')[0]
                path = url.split(host_name)[1]
                path = path.strip()         #Getting the path that the user is requesting for
            else:
                path = url.strip()         #Getting the path that the user is requesting for

            print("The requested path is : " + path)

            # Now comparing that whether the path exists or not
            if  path == "/":
                print("Client Requested for HTML file")          
                try:
                    data = "HTTP/1.1 200 OK\n\n"
                    # data = "Content-Type:text/html\r\n"
                    data += "\r\n\r\n"
                    with open("HelloWorld.html","r") as file:
                        data += str(file.read())

                        clientSocket.send(data.encode())

                except FileNotFoundError as e:           #File requested by the client is not found
                    print("Internal Server Error! : Cannot Open File\n" + str(e))
                    clientSocket.send(b'HTTP/1.1 500 Internal Server Error\n\n<h1>500 Internal Server Error</h1>\r\n\r\n')
            elif path is not None:
                print(f"Client Requested for HTML file: {path[1:]}")          
                try:
                    data = "HTTP/1.1 200 OK\n\n"
                    # data = "Content-Type:text/html\r\n"
                    data += "\r\n\r\n"
                    with open(path[1:],"r") as file:
                        data += str(file.read())

                        clientSocket.send(data.encode())

                except FileNotFoundError as e:           #File requested by the client is not found
                    print("Internal Server Error! : Cannot Open File\n" + str(e))
                    clientSocket.send(b'HTTP/1.1 500 Internal Server Error\n\n<h1>500 Internal Server Error</h1>\r\n\r\n')       
            else:                                   #File not found
                print("Bad Request!")
                clientSocket.send(bytes("HTTP/1.1 404 Not Found\n\n<h1>404 Not Found</h1>\r\n\r\n","utf-8"))  
        else:           # Bad Request
            println("No Request Found, Termiating connection!")
            clientSocket.send(bytes("HTTP/1.1 400 Bad Request\n\n<h1>400 Bad Request</h1>\r\n\r\n","utf-8"))  
        
        clientSocket.close()
        break       

# This is the never ending while loop which keeps the server running and keep the server in the listening state

while True:
    #Accepting the server connection
    clientSocket, clientAddress = serverSocket.accept()

    #Incrementing the Client number to keep track of number of clients 
    clientNo += 1
    println("Connection Request came from Client No. : " + str(clientNo))

    println("Type : " + str(clientAddress))

    print(f"Now starting a new Thread for the Client No. {clientNo}")

    # Starting a new Thread for the Client
    threading._start_new_thread(connectionWithClient,(clientSocket,clientAddress,clientNo))

