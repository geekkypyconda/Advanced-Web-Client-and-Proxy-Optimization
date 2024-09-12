import socket                                       # Importing Socket 
from bs4 import BeautifulSoup                       # Importing Library for Parsing the HTML files 
from PIL import Image, UnidentifiedImageError       # Importing Library for handling Images
from io import BytesIO                              # Importing Library for showing Images
import os                                           # Importing os library
import ssl                                          # Importing ssl library for making secure connections
import sys                                          # Importing the sys library for taking command line arguments
from concurrent.futures import ThreadPoolExecutor   # Importing library for making Parallel TCP Connections
import time                                         # Importing library for capturing time


# Variables to keep track whether the user has entered IP address or he wants to connect to PORT 443
globalIP = False
globalSSL = False


# Function to print next line with print(object)
def println(o):
    print(o)
    print("\n")


# Function for forming the GET request
def getStringUrl(Host,PORT,path):
    # Forming the GET reuqest
    url = (
        f"GET http://{Host}{path} HTTP/1.0\r\n"
        f"Host: {Host}:{PORT}\r\n"
        "\r\n"
    )


    # returning the GET request
    return url


# Function for printing the list
def printList(lst):
    c = 0
    for object in lst:
        c += 1        
        if(isinstance(object,list)):
            printList(object)
        else:
            println(str(c) + ". " + str(object))


# Function for Checking range of number
def checkRange(n):
    if n >= 0 and n <= 255:
        return True

    return False

# Function to check whether user has entered IP address instead of host name
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


# Function to get the type of file
def getFileType(file):
    fl = file.split("/")[-1]
    return fl

# Function to save a file
def saveFile(byteFile,filePath):
    filePath = "Parallel_Downloads/" + filePath
    if(os.path.isdir("Parallel_Downloads") == False):
       os.mkdir("Parallel_Downloads")

    file = open(filePath,"wb")
    file.write(byteFile)
    file.close()


# Function to save the icon
def saveIcon(byteData,loop):
    iconPath = f"icon_{loop}.ico"

    iconPath = "Parallel_Downloads/" + iconPath
    if(os.path.isdir("Parallel_Downloads") == False):
       os.mkdir("Parallel_Downloads")

    iconFile = open(iconPath,"wb")
    iconFile.write(byteData)
    iconFile.close()


# Function to process the error codes
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


# Function to remove the header
def removeHeader(bytesResponse):
    # Removing the header
    byteHeader = bytesResponse.split(b'\r\n\r\n')[0]
    byteDataWithOutHeader = bytesResponse[(len(byteHeader) + 4):]

    # Returning Hader and data
    return byteHeader, byteDataWithOutHeader

# Function to get The status code
def getStatusCode(byteResponse):
    # Seperating header and data
    byteHeader, byteData = removeHeader(bytesResponse=byteResponse)
    statusCode = byteHeader.decode().split(" ")[1]

    # returning the status code
    return statusCode

# Function to query the sever using SSL
def queryServerUsingSSL(Host,PORT,Url):
    # Making the SSL connections
    sslContext = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # Making the SSL socket
    sslSocket = sslContext.wrap_socket(sock,server_hostname=Host)
    sslSocket.connect((Host,PORT))

    # Sending the GET request
    sslSocket.send(Url.encode())

    # Making a variable for storing the response from the server
    byteResponse = b""

    while True:
        data = sslSocket.recv(4096)
        if not data:
            break
        byteResponse += data
    
    sslSocket.close()

    return byteResponse


# Function to send the GET request to the server and get the response
def queryServer(Host,PORT,Url):
    global globalSSL

    # Checking whether the user wants to connect to PORT 443
    if(globalSSL == True):
        return queryServerUsingSSL(Host,PORT,Url)

    # Making a socket
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((Host,PORT))

    # Sending the GET request
    sock.send(Url.encode())

    byteResponse = b""

    while True:
        data = sock.recv(4096)
        if not data:
            break
        byteResponse += data
    
    sock.close()

    return byteResponse


# Function to download the object
def downloadObjects_Util(Host,PORT,Url,ref):
    try:
        print("Sending Get Request to the server for object : " + str(ref))

        # Getting the response from the server
        byteResponse = queryServer(Host=Host,PORT=PORT,Url=Url)
        statusCode = getStatusCode(byteResponse=byteResponse)

        println("The Status code is : " + str(statusCode) + ", for object : " + str(ref))

        # Checking the status code
        if(statusCode == "200"):
            byteHeader, byteData = removeHeader(bytesResponse=byteResponse)
            
            saveFile(byteData,getFileType(ref))
        else:
            print("Error in downloading Object, Error : " + str(statusCode) + " : " + processErrorCode(statusCode))
            println("Object : " + str(Url))
    except Exception as e:
        println(f"Exception Occured! : {e}")
    

# Function to make thread for download objects
def downloadObjects(Host,PORT,downloadRefList):
    println("All Downloadable content : ")
    printList(downloadRefList)
    println("Now downloading all objects using Parallel TCP Connections!")

    # Making parallel TCP Connections for downloading the objects
    with ThreadPoolExecutor() as downloadExecuter:
        for ref in downloadRefList:
            Url = getStringUrl(Host=Host,PORT=PORT,path=ref)
            downloadExecuter.submit(downloadObjects_Util,Host,PORT,Url,ref)


# Function to parse the HTML file
def parseHTML(byteResponse,Host,PORT,Path):
    println("The received file is a HTML file")
    stringResponse = byteResponse.decode()
    baseHtml = BeautifulSoup(stringResponse,'html.parser')

    #-------Getting the title-------------------

    title = str(baseHtml.title)
    title = title[7:len(title) - 8]
    print("The Tile of the HTML file is : " + title)

    htmlHeader,htmlData = removeHeader(bytesResponse=byteResponse)


    #--------Saving the HTML--------------------
    htmlPath = ""

    if Path == "/":
        htmlPath = "baseHTML.html"
    else:
        htmlPath = getFileType(Path)
        
    saveFile(htmlData,htmlPath)


    #--------Parsing Images-------------------
    println("Parsing images")
    imageTags = baseHtml.find_all('img')
    imageRefList = []
    downloadRefList = []

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
                    downloadRefList.append(realSrc)
            else:
                if src[0] != '/':
                    src = '/' + src
                imageRefList.append(src)
                downloadRefList.append(src)
    
    if(len(imageRefList) > 0):
        println("Image References list")
        printList(imageRefList)
        # parseImages(imageRefList=imageRefList,Host=Host,PORT=PORT)
    else:
        println("No Images Found!")
    

    #--------Parsing Icons---------------

    println("\nParsing Icons Now!")
    iconList = baseHtml.findAll('link', rel = 'icon') or baseHtml.findAll('link', rel = 'shortcut icon')
    if(len(iconList) > 0):
        printList(iconList)
        for ic in iconList:
            path = ic.get('href')
            if "http" in path:
                pathList = path.split(Host)
                if len(pathList) > 1:
                    realPath = pathList[1]
                    if realPath[0] != '/':
                        realPath = '/' + realPath
                    downloadRefList.append(realPath)
            else:
                if path[0] != '/':
                    path = '/' + path
                downloadRefList.append(path)
        # parseIcons(iconList,Host,PORT)
    else:
        println("No Icons Found!")


    #-------Parsing Links---------------

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


    #---------Parsing Scripts----------

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
                    downloadRefList.append(realSrc)
            else:
                if src[0] != '/':
                    src = '/' + src
                scriptList.append(src)
                downloadRefList.append(src)
    
    if(len(scriptList) > 0):
        println("Parsing Scripts now!")
        printList(scriptList)
        # parseScripts(scriptList,Host,PORT)
    else:
        println("No Scripts Found!")
    

    #----------Now downloading objects
    if(len(downloadRefList) > 0):
        downloadObjects(Host,PORT,downloadRefList)
    else:
        println("No Downloadable Objecs found!")


# Function to connect to the webserver
def connectToWebServer(Host,PORT,Path):
    # Getting the GET request
    Url = getStringUrl(Host=Host,PORT=PORT,path=Path)

    # getting the response for the GET request
    print("Making connection with the server")
    bytesResponse = queryServer(Host=Host,PORT=PORT,Url=Url)
    statusCode = getStatusCode(byteResponse=bytesResponse)

    # Checking the status code
    print("The Status Code is : " + statusCode)
    if(statusCode == "200"):
        pathList = Path.split(".")
        if Path == '/' or (pathList != None and len(pathList) > 0 and (pathList[-1] == "HTML" or  pathList[-1] == "html")):
            parseHTML(bytesResponse,Host,PORT,Path)
        else:
            println("File Downloaded")
            byteHeader, byteData = removeHeader(bytesResponse=bytesResponse)
            filePath = getFileType(Path)

            saveFile(byteFile=byteData,filePath=filePath)
    else:
        print("Error in receiving file!")
        println("Error : " + str(statusCode) + " : " + processErrorCode(statusCode))


# Main function
def main():
    global globalIP
    global globalSSL

    lenght = len(sys.argv)

    println(f"Total Number of Arguments entered! : {lenght}")

    # Checking whether the use has entered the correct arguments or not

    if(lenght == 0):
        println("No Arguments entered!")
    elif(lenght == 4):
        println("Connection through webserver")
        Host = sys.argv[1]
        PORT = int(sys.argv[2])
        path = sys.argv[3]

        # Checking whether the user has entered IP instead of host name
        if checkIP(Host) == True:
            globalIP = True
        
        # Checking whether the PORT is 443 or not
        if(PORT == 443):
            globalSSL = True

        # Forming the GET request
        Url = getStringUrl(Host,PORT,path)
        println("Url is : " + Url)

        # Calculating the time
        startTime = time.time()
        connectToWebServer(Host=Host,PORT=PORT,Path = path)
        endTime = time.time()

        # Calculating the delay
        delay = endTime - startTime


        println("The total time taken is : " + str(delay) + " seconds")

    else:
        println("Wrong number of arguments entered!")


#Calling Main Function
main()