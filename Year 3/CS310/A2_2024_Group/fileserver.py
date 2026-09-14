# CS310 Assignment 1 - File Transfer Server (TCP)
# Rohan Nandan - S11234883
# Zhixian Chen - S11230686

from socket import *
import os

#Server configurations
HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
REQUEST_PREFIX = "FILE_REQUEST"
RESPONSE_OK_PREFIX = "STATUS|OK"
RESPONSE_ERROR_PREFIX = "STATUS|ERROR"

#Handle the connection with client
def handle_client(conn, addr):

    with conn:
        print(f"\n--- Connected by {addr}, ready for communication---\n")

        try:
            #Receive the custom request header from the client
            request = conn.recv(1024).decode('utf-8').strip()

            #Parses the client request and validates file existence
            is_valid, filename, file_size, err_msg = validate_file_request(request)

            if is_valid:
                #Construct and send the custom ACK header with file size
                print(f"Requested file: {filename} (Valid)")
                header = f"{RESPONSE_OK_PREFIX}|{filename}|{file_size}\n"
                conn.sendall(header.encode("utf-8"))

                #Send file
                send_file_data(conn, filename)

            else:
                #Construct and send the custom ERROR header
                print(f"Error: {err_msg}")
                error_header = f"{RESPONSE_ERROR_PREFIX}|{err_msg}\n"
                conn.sendall(error_header.encode("utf-8"))


        #Error handling
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError) as e:
            # Capture connection error
            print(f"A connection error happened: {e}")
        except OSError as e:
            # Capture file accessing error
            print(f"Server local file/system error {e}")
            #Capture other errors
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print(f"Connection with client {addr} closed.")

#Handle the client request and validates file existence.
def validate_file_request(request_text):

    #Check protocol format
    if not request_text.startswith(REQUEST_PREFIX):
        return False, None, 0, "Invalid request protocol"

    #Extract filename and prevent Path Traversal attacks
    raw_filename = request_text.split("|", 1)[1].strip()
    filename = os.path.basename(raw_filename)

    #Validate file existence
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return False, filename, 0, "File does not exist"

    #Get file size
    file_size = os.path.getsize(filename)

    #Return success status and file info
    return True, filename, file_size, ""

#Handle file transmission
def send_file_data(conn, filename):

    #Extract and send the file in 4096-byte chunks
    with open(filename, 'rb') as file:
        chunk = file.read(BUFFER_SIZE)
        while chunk:
            conn.sendall(chunk)
            chunk = file.read(BUFFER_SIZE)

    print("File sent successfully.")

#Start server
def main():

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server is listening on port {PORT}, waiting for connection...")

        while True:

            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    main()