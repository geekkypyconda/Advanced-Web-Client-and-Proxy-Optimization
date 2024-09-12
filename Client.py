import socket      #Socket library for python
from bs4 import BeautifulSoup        #Library for Parsing HTML file
from PIL import Image, UnidentifiedImageError        #Library for showing image
from io import BytesIO                              #Library for showing image
import os                                           #Library for os
import ssl                                          #Library for making SSL connections
import sys                                          #Library for SYS
import time                                         #Library for measuring time

# cse.iith.ac.in -> 35.185.44.232, Port = 443
# giaa -> 128.119.245.12
# www.httpbin.org


#Variable for checking whether user has entered IP or not.
globalIP = False
#Variable for checking whether user wants to connect to PORT 443
globalSSL = False
#Variable for checking that whether the user wants to connect ot the proxy server or not
globalProxy = False

# Function for printing objects
def println(o):
    print(o)
    print("\n")

#Function for encoding objects
def encode(object):
    return object.encode('utf-8')

#Function for decoding objects
def decode(object):
    return object.decode('utf-8')

#Function for getting the GET request
def getStringUrl(Host,PORT,path):
    url = (
        f"GET http://{Host}{path} HTTP/1.0\r\n"
        f"Host: {Host}:{PORT}\r\n"
        "\r\n"
    )

    return url



#Utility function for checking range
def checkRange(n):
    if n >= 0 and n <= 255:
        return True

    return False

#Function to check whether the user has entered the IP address or Host name
def checkIP(Host):
    s = str(Host).split(".")
    
    if(len(s) != 4):
        return False

    for i in s:
        if i.isnumeric() == False:
            return False
        elif checkRange(int(i)) == False:
            return False
        else:
            continue
    
    return True


# Function to get the response on error codes
def processErrorCode(code):
    if(code == 400 or code == "400"):
        return "Bad Request!"
    elif(code == 401 or code == "401"):
        return "Authentication Error!"
    elif(code == 404 or code == "404"):
        return "File Not Found!"
    elif(code == 301 or code == "301"):
        return "Moved Permanently!"
    elif(code == 302 or code == "302"):
        return "Request source has moved but found!"
    elif(code == 304 or code == "304"):
        return "Request has not been Modified!"
    else:
        return "Unexpected Error code!"


# Function to remove the header from the data received from the server
def removeHeader(bytesResponse):
    byteHeader = bytesResponse.split(b'\r\n\r\n')[0]
    byteDataWithOutHeader = bytesResponse[(len(byteHeader) + 4):]

    return byteHeader, byteDataWithOutHeader

# Function for printing a list of objects
def printList(lst):
    c = 0
    for object in lst:
        c += 1        
        if(isinstance(object,list)):
            printList(object)
        else:
            println(str(c) + ". " + str(object))

# Function for getting the file type
def getFileType(file):
    fl = file.split("/")[-1]
    return fl


# Function for saving a file
def saveFile(byteFile,filePath):
    filePath = "Downloads/" + filePath
    if(os.path.isdir("Downloads") == False):
       os.mkdir("Downloads")

    file = open(filePath,"wb")
    file.write(byteFile)
    file.close()

# Funcion for sending GET request using SSL
def queryServerUsingSSL(Host,PORT,Url,proxyHost,proxyPORT):
    global globalProxy

    sslContext = ssl.create_default_context()               #making a SSL context
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)     # Making a Socket

    sslSocket = sslContext.wrap_socket(sock,server_hostname=Host)   # Making a SSL socket
    sslSocket.connect((Host,PORT))                                  # Connecting the socket

    print("Connection Made with server")

    sslSocket.send(Url.encode())                                # Sending the GET Request

    byteResponse = b""                                          # Variable for stroring the response fromt the server

    # Receiving data from the client
    while True:
        data = sslSocket.recv(4096)
        if not data:
            break
        byteResponse += data
    
    # Closing the socket
    sslSocket.close()

    return byteResponse

# Function for sending the GET request using normal connection
def queryServer(Host,PORT,Url,proxyHost,proxyPORT):
    global globalSSL
    global globalProxy

    #Checking that whether the connection is SSL or not
    if(globalSSL == True and globalProxy == False):
        return queryServerUsingSSL(Host,PORT,Url,proxyHost,proxyPORT)

    # Creating and connecting socket
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    if globalProxy is True:
        sock.connect((proxyHost, proxyPORT))
    else:
        #Connecting to the server
        sock.connect((Host,PORT))

    print("Connection Made with server")

    # Sending the GET request
    sock.send(Url.encode())

    # Variable for storing the response from the server
    byteResponse = b""

    # Storing the response from the server
    while True:
        data = sock.recv(4096)
        if not data:
            break
        byteResponse += data
    

    # Closing the connection
    sock.close()

    #Returning the response 
    return byteResponse

# Function for getting the status code from the server response
def getStatusCode(byteResponse):
    # Seperating the header and data from the server response
    byteHeader, byteData = removeHeader(bytesResponse=byteResponse)

    # Extracting the status code
    statusCode = byteHeader.decode().split(" ")[1]


    return statusCode

# Function for downloading the images
def parseImages(imageRefList,Host,PORT,proxyHost,proxyPORT):
    loop = 0
    for ref in imageRefList:
        loop += 1
        println("Making connection for getting image : " + str(loop))

        # Forming the GET Request
        Url = getStringUrl(Host,PORT,f"{ref}")

        # Getting the response the the server
        bytesResponse = queryServer(Host,PORT,Url,proxyHost,proxyPORT)
        byteHeader, byteData = removeHeader(bytesResponse=bytesResponse)

        # Getting the status code
        statusCode = getStatusCode(byteResponse=bytesResponse)

        # If the status code is 200 then save the file else return error
        if(statusCode == "200"):
            imagePath = getFileType(ref)
            saveFile(byteData,imagePath)
        else:
            println("Error in getting Image, Status Code : " + str(statusCode) + ", " + processErrorCode(statusCode))
        
        println("Closing connection for image : " + str(loop))


# Function for parsing the scripts
def parseScripts(scriptList,Host,PORT,proxyHost,proxyPORT):
    loop = 0

    for ref in scriptList:
        loop += 1
        println("Making Connection for getting the script : " + str(loop))
        Url = getStringUrl(Host,PORT,f"{ref}")
        
        # Getting the response from the server
        bytesResponse = queryServer(Host,PORT,Url,proxyHost,proxyPORT)
        byteHeader, byteData = removeHeader(bytesResponse=bytesResponse)

        # Checking whether the status is 200 OK or not
        statusCode = getStatusCode(byteResponse=bytesResponse)

        # If the status code is 200 then save the file else return error

        if(statusCode == "200"):
            imagePath = getFileType(ref)
            saveFile(byteData,imagePath)
        else:
            println("Error in getting Script, Status Code : " + str(statusCode) + ", " + processErrorCode(statusCode))
        
        println("Closing connection for Script : " + str(loop))

# Function for saving the icon
def saveIcon(byteData,loop):
    iconPath = f"icon_{loop}.ico"

    iconPath = "Downloads/" + iconPath
    if(os.path.isdir("Downloads") == False):
       os.mkdir("Downloads")

    iconFile = open(iconPath,"wb")
    iconFile.write(byteData)
    iconFile.close()

# Function for getting the icons
def getIcons(iconUrls,Host,PORT,proxyHost,proxyPORT):
    loop = 0

    for ref in iconUrls:
        loop += 1
        print(f"Making Connection for getting icon : {loop}")

        # Getting the GET request
        Url = getStringUrl(Host=Host,PORT=PORT,path = f"{ref}")
        print("Get Reuqest for Icon : " + Url)

        # Sending the request
        byteResponse = queryServer(Host,PORT,Url,proxyHost,proxyPORT)
        byteHeader, byteData = removeHeader(bytesResponse=byteResponse)

        # Getting the status code
        stausCode = getStatusCode(byteResponse=byteResponse)


        # Checking the status code
        if(stausCode == "200"):
            print(f"Parsing icon. {loop}")
            # saveIcon
            saveFile(byteFile=byteData,filePath=getFileType(ref))
        else:
            print("Error in getting icon : " + str(loop) + ", Error Code : " + str(stausCode))
            println(processErrorCode(stausCode))


# Function for parsing the icons
def parseIcons(iconList,Host,PORT, proxyHost,proxyPORT):
    iconUrls = []
    for icon in iconList:
        if icon.has_attr('href'):
            path = icon.get('href')
            if "http" in path:
                pathList = path.split(Host)
                if len(pathList) > 1:
                    realPath = pathList[1]
                    if realPath[0] != '/':
                        realPath = '/' + realPath
                    iconUrls.append(realPath)
            else:
                if path[0] != '/':
                    path = '/' + path
                iconUrls.append(path)
    
    getIcons(iconUrls,Host,PORT, proxyHost, proxyPORT)

# Function for parsing HTML
def parseHTML(byteResponse,Host,PORT,proxyHost,proxyPORT,Path):
    println("The received file is a HTML file")
    stringResponse = byteResponse.decode()
    baseHtml = BeautifulSoup(stringResponse,'html.parser')

    #--------------Getting the Title------------------------------
    title = str(baseHtml.title)
    title = title[7:len(title) - 8]
    print("The Tile of the HTML file is : " + title)

    #--------------Seperating the Header and the data--------------

    htmlHeader,htmlData = removeHeader(bytesResponse=byteResponse)


    #-------------Saving the HTML file----------------------------
    htmlPath = ""

    if Path == "/":
        htmlPath = "baseHTML.html"
    else:
        htmlPath = getFileType(Path)

    saveFile(htmlData,htmlPath)


    #-------------Parsing Images---------------------------------
    println("Parsing images")
    imageTags = baseHtml.find_all('img')
    imageRefList = []

    for img in imageTags:
        src = img.get('src')
        if(src):
            if "http" in src:
                srcList = src.split(Host)
                if len(srcList) > 1:
                    realSrc = srcList[1]
                    if realSrc[0] != '/':
                        realSrc = '/' + realSrc
                    imageRefList.append(realSrc)
            else:
                if src[0] != '/':
                    src = '/' + src
                imageRefList.append(src)
    
    if(len(imageRefList) > 0):
        println("Image References list")
        printList(imageRefList)
        parseImages(imageRefList=imageRefList,Host=Host,PORT=PORT,proxyHost = proxyHost,proxyPORT = proxyPORT)
    else:
        println("No Images Found!")
    

    #---------------Parsing Icons----------------------

    println("\nParsing Icons Now!")
    iconList = baseHtml.findAll('link', rel = 'icon') or baseHtml.findAll('link', rel = 'shortcut icon')
    if(len(iconList) > 0):
        printList(iconList)
        parseIcons(iconList,Host,PORT,proxyHost,proxyPORT)
    else:
        println("No Icons Found!")


    #-------------------Finding Links--------------

    linkTags = baseHtml.find_all('a')

    linkList = []
    for link in linkTags:
        src = link.get('href')
        if(src):
            linkList.append(src)
    
    if(len(linkList) > 0):
        println("Parsing links")
        printList(linkList)
    else:
        println("No Links Found!")


    #---------------------Finding Scripts---------------------

    scriptTags = baseHtml.find_all('script')
    scriptList = []

    for spt in scriptTags:
        src = spt.get('src')
        if(src):
            if "http" in src:
                srcList = src.split(Host)
                if len(srcList) > 1:
                    realSrc = srcList[1]
                    if realSrc[0] != '/':
                        realSrc = '/' + realSrc
                    scriptList.append(realSrc)
            else:
                if src[0] != '/':
                    src = '/' + src
                scriptList.append(src)
    
    if(len(scriptList) > 0):
        println("Parsing Scripts now!")
        printList(scriptList)
        parseScripts(scriptList,Host,PORT,proxyHost,proxyPORT)
    else:
        println("No Scripts Found!")


# Function for connecting through the web server
def connectToWebServer(Host,Url,PORT,proxyHost,proxyPORT,Path):
    # Getting the Base HTML file
    bytesResponse = queryServer(Host,PORT,Url,proxyHost,proxyPORT)
    
    # Getting the status code
    statusCode = getStatusCode(byteResponse=bytesResponse)

    # Checking the status code
    print("The Status Code is : " + statusCode)
    if(statusCode == "200"):
        pathList = Path.split(".")
        if Path == '/' or (pathList != None and len(pathList) > 0 and (pathList[-1] == "HTML" or  pathList[-1] == "html")):
            parseHTML(bytesResponse,Host,PORT,proxyHost,proxyPORT,Path)
        else:
            println("File Downloaded")
            byteHeader, byteData = removeHeader(bytesResponse=bytesResponse)
            filePath = getFileType(Path)

            saveFile(byteFile=byteData,filePath=filePath)
    else:
        print("Error in receiving file!")
        println("Error : " + processErrorCode(statusCode))


# Main function
def main():
    # Globalising the global variables
    global globalIP
    global globalSSL

    lenght = len(sys.argv)

    println(f"Total Number of Arguments entered! : {lenght}")

    # Checking whether user has entered arguments correctly or not
    if(lenght == 0):
        println("No Arguments entered!")
    elif(lenght == 4):
        println("Connection through normal webserver")
        Host = sys.argv[1]                      # Getting the Host
        PORT = int(sys.argv[2])                 # Getting the PORT number
        path = sys.argv[3]                      # Getting the Path


        # Checking whether user has entered Host name or IP address
        if checkIP(Host) == True:
            globalIP = True
        
        # Checking whether the user wants to connect to the PORT 443 or not
        if(PORT == 443):
            globalSSL = True


        # Forming the get Request
        Url = getStringUrl(Host,PORT,path)
        println("Url is : " + Url)

        # Calculating Time
        startTime = time.time()
        connectToWebServer(Host=Host,Url = Url,PORT=PORT,proxyHost="Invalid", proxyPORT=-1,Path=path)
        endTime = time.time()

        # Calculating the delay
        delay = endTime - startTime

        print("The Total time taken is : " + str(delay) + " seconds")

    elif(lenght == 6):
        global globalProxy

        globalProxy = True

        println("Connection Through Proxy server")
        Host = sys.argv[1]                      # Getting the Host
        PORT = int(sys.argv[2])                 # Getting the PORT number
        proxy_host = sys.argv[3]
        proxy_port = int(sys.argv[4])
        path = sys.argv[5]                      # Getting the Path


        # Checking whether user has entered Host name or IP address
        if checkIP(Host) == True:
            globalIP = True
        
        # Checking whether the user wants to connect to the PORT 443 or not
        if(PORT == 443):
            globalSSL = True


        # Forming the get Request
        Url = getStringUrl(Host,PORT,path)
        println("Url is : " + Url)

        # Calculating Time
        startTime = time.time()
        connectToWebServer(Host=Host,Url = Url,PORT=PORT,proxyHost=proxy_host,proxyPORT=proxy_port,Path=path)
        endTime = time.time()

        # Calculating the delay
        delay = endTime - startTime

        print("The Total time taken is : " + str(delay) + " seconds")
    else:
        println("Wrong number of arguments entered!")


#Calling Main Function
main()