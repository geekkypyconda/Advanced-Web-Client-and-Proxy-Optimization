import socket             #Socket library for python
import threading          # Library for using multithreading
import ssl                #Library for making SSL connections
import subprocess
from datetime import datetime   #Module to get time
import pytz                     #Module to get time on different time zone

requests_list = {}

host_addr_info = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
host_address =   host_addr_info.split()[0]
port_number  = 12002


# Function to modify header
def response_modifier(status_code, response_header):

    # Creates first line of header based on status code
    modified_response_headers = b''
    if status_code == '200':
        modified_response_headers = f'HTTP/1.1 {status_code} OK '
    elif status_code == '206':
        modified_response_headers = f'HTTP/1.1 {status_code} Partial Content '
    elif status_code == '300':
        modified_response_headers = f'HTTP/1.1 {status_code} Multiple Choices '
    elif status_code == '301':
        modified_response_headers = f'HTTP/1.1 {status_code} Moved Permanently '
    elif status_code == '302':
        modified_response_headers = f'HTTP/1.1 {status_code} Found '
    elif status_code == '400':
        modified_response_headers = f'HTTP/1.1 {status_code} Bad Request '
    elif status_code == '404':
        modified_response_headers = f'HTTP/1.1 {status_code} Not Found '
    elif status_code == '408':
        modified_response_headers = f'HTTP/1.1 {status_code} Request Timeout '
    elif status_code == '502':
        modified_response_headers = f'HTTP/1.1 {status_code} Bad Gateway '
    else:
        return response_header
    
    response_header_list = response_header.split('\r\n')

    # Appends the remaining headers
    for headers in response_header_list[1:]:
        modified_response_headers += '\r\n'
        modified_response_headers += headers

    #Appends the header line with IP address of proxy server
    modified_response_headers += '\r\n'
    modified_response_headers += f'Proxy Host: {host_address}'
    modified_response_headers += '\r\n\r\n'

    print(f'Modified header: {modified_response_headers}')


    return modified_response_headers

# Function to parse the request
def parse_request(request):
    request_components = request.split('\r\n')    
    # Split and get the requested method
    request_method = request_components[0].split()[0]
    # Extract the requested URL
    request_url = request_components[0].split()[1]
    # Extract headers from the request
    headers = {}
    for line in request_components[1:]:
        if line.strip():  # Skip empty lines in the header
            header_parts = line.split(': ')
            header_name = header_parts[0]
            header_value = header_parts[1]
            headers[header_name] = header_value

    return request_method, request_url, headers

def parse_response(response):
    
    response_headers = response.split(b'\r\n\r\n')[0].decode()
    response_content = response[len(response_headers)+4:]
    status_code = response_headers.split('\r\n')[0].split()[1]

    modified_response_headers = response_modifier(status_code, response_headers)

    
    response = modified_response_headers.encode('utf-8', errors='ignore') + response_content

    return response, status_code

def queryServerUsingSSL(server_hostname, client_socket, decoded_request, PORT):
    sslContext = ssl.create_default_context()                                             
    # Socket to connect to the web server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sslSocket = sslContext.wrap_socket(server_socket,server_hostname=server_hostname)
    sslSocket.connect((server_hostname,PORT))

    print("Connection Made with server")

    sslSocket.send(decoded_request.encode())

    byteResponse = b""

    while True:
        data = sslSocket.recv(4096)
        if not data:
            break
        byteResponse += data

    byteResponse, status_code = parse_response(byteResponse)
    print(f"\nThe status code is {status_code} for server {server_hostname}")
        
    client_socket.send(byteResponse)
    
    server_socket.close()

def service_client_thread(client_socket):
    # Recieving the request from client
    request = client_socket.recv(10240)

     # Get the current date and time
    gmt_timezone = pytz.timezone('Etc/GMT')
    current_time = datetime.now(gmt_timezone)

    # Format the current time as a string
    request_time = current_time.strftime("%a, %d %b %Y %H:%M:%S %Z")

    # Decode the request sent by the client and if error, print it
    try:
        decoded_request = request.decode()
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        decoded_request = None

    print(f"\nRequest sent by client :\n{decoded_request}")

    if decoded_request is not None:
        # Parse the request and get back request method, the url and a list of headers
        parsed_method, parsed_url, headers = parse_request(decoded_request)
        print(f"Request method and url after parsing is {parsed_method}:{parsed_url}")

        if parsed_url in requests_list:
            modified_request = decoded_request[:-2] + f'If-Modified-Since: {requests_list[parsed_url]}\r\n'
            modified_request += '\r\n'
            print( f'\nModified request for condtional get:\n {modified_request} ')
            

        requests_list[parsed_url] = request_time

        server_port = '80'
        
        # If there is a header component with title Host, split it's #making a SSL contextvalue and get hostname and port number
        if 'Host' in headers:
            host_port_list = headers['Host'].split(':')
            server_hostname = host_port_list[0]
            if len(host_port_list) >= 2:
                server_port = headers['Host'].split(':')[1]

        print(f"Server hostname and Port number is {server_hostname}:{server_port}")

        # If the port number is 443, query to the server using SSL. 
        if server_port == '443':
            queryServerUsingSSL(server_hostname, client_socket, decoded_request, 443)
            client_socket.close()
            return
        else:
            # Socket to connect to the web server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_socket.connect((server_hostname, int(server_port)))

            except socket.error as e:
                print(f"Failed to connect to remote server with port 80: {e}")
                
                client_socket.close()
                return
            
            # Send the client's request to web server
            server_socket.send(decoded_request.encode())

            # Receive the required data from the web server and send it back to the client after parsing and modifying the response header. 
            header = True
            while True:
                response = server_socket.recv(10240)
                if header is True:
                    header = False
                    # Passing the response to 'parse_response_ function and getting back the response with modified header and status code
                    response, status_code = parse_response(response)
                    print(f"\nThe status code is {status_code} for server {server_hostname}")
                # Break the loop when proxy doesn't recieve any response from web server 
                if len(response) == 0:
                    break
                client_socket.send(response)

            server_socket.close()


    client_socket.close()


def main():
        
    # creating a socket for proxy server
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((host_address, port_number))
    proxy_socket.listen(1000)

    print(f"Proxy server is listening on {host_address}:{port_number}")
 
    while True:
        # Accept the connection request from client
        client_socket, addr = proxy_socket.accept()
        print(f"Connection established with client at {addr[0]}:{addr[1]}")
        
        # Creates a new thread and assigns it to the client-proxy connection
        client_handler = threading.Thread(target = service_client_thread, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
