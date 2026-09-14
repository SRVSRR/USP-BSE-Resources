# CS310 Assignment 1 - File Transfer Client (TCP)
# Rohan Nandan - S11234883
# Zhixian Chen - S11230686


import os
import socket

# Server settings
HOST = "127.0.0.1"
PORT = 5000

# Protocol settings
BUFFER_SIZE = 4096
MAX_HEADER_BYTES = 4096
REQUEST_PREFIX = "FILE_REQUEST|"
RESPONSE_OK_PREFIX = "STATUS|OK|"
RESPONSE_ERROR_PREFIX = "STATUS|ERROR|"

# Save as <name>_downloaded.ext by default
SAVE_WITH_SUFFIX = True
DOWNLOAD_SUFFIX = "_downloaded"


# Receive one newline-terminated protocol line from the server.
def recv_line(connection: socket.socket, max_bytes: int = MAX_HEADER_BYTES) -> str:
    received = bytearray()

    while len(received) < max_bytes:
        chunk = connection.recv(1)
        if not chunk:
            break
        received.extend(chunk)
        if chunk == b"\n":
            break

    if not received:
        raise ConnectionError("Server closed the connection without a response.")

    return received.decode("utf-8", errors="replace").rstrip("\r\n")


# Parse STATUS|OK or STATUS|ERROR response headers.
def parse_server_response(response_line: str):
    if response_line.startswith(RESPONSE_ERROR_PREFIX):
        message = response_line[len(RESPONSE_ERROR_PREFIX) :].strip()
        return "error", (message or "Unknown server error"), "", 0

    if response_line.startswith(RESPONSE_OK_PREFIX):
        payload = response_line[len(RESPONSE_OK_PREFIX) :]
        try:
            file_name, size_text = payload.rsplit("|", 1)
            file_size = int(size_text)
        except ValueError as parse_error:
            raise ValueError("Malformed success header received from server.") from parse_error

        if not file_name:
            raise ValueError("Server response did not include a file name.")
        if file_size < 0:
            raise ValueError("Server response had a negative file size.")

        return "ok", "", file_name, file_size

    raise ValueError("Unknown response format from server.")


# Build a safe destination file name in the client directory.
def build_output_filename(original_name: str) -> str:
    safe_name = os.path.basename(original_name)
    if not safe_name:
        safe_name = "downloaded_file"

    if not SAVE_WITH_SUFFIX:
        return safe_name

    name, extension = os.path.splitext(safe_name)
    return f"{name}{DOWNLOAD_SUFFIX}{extension}"


# Receive file bytes, write output, and print progress.
def receive_file_bytes(connection: socket.socket, output_name: str, file_size: int) -> int:
    received_bytes = 0
    last_bucket = -1

    with open(output_name, "wb") as output_file:
        if file_size == 0:
            print("Downloading... 100%")
            return 0

        while received_bytes < file_size:
            remaining = file_size - received_bytes
            chunk = connection.recv(min(BUFFER_SIZE, remaining))
            if not chunk:
                raise ConnectionError("Connection closed before file download completed.")

            output_file.write(chunk)
            received_bytes += len(chunk)

            percent = int((received_bytes * 100) / file_size)
            bucket = percent // 5
            if bucket != last_bucket or percent == 100:
                print(f"\rDownloading... {percent:3d}%", end="", flush=True)
                last_bucket = bucket

    print()
    return received_bytes


# Connect to server, request file, and save it.
def request_file(connection: socket.socket,file_name: str) -> None:
    request_line = f"{REQUEST_PREFIX}{file_name}\n".encode("utf-8")

    connection.sendall(request_line)
    print(f"Requested: {file_name}")

    response_line = recv_line(connection)
    status, message, server_file_name, server_file_size = parse_server_response(response_line)

    if status == "error":
        print(f"Server: {message}")
        return

    output_name = build_output_filename(server_file_name)
    print(f"Download approved ({server_file_size} bytes)")
    print(f"Saving as: {output_name}")

    received = receive_file_bytes(connection, output_name, server_file_size)
    if received != server_file_size:
        raise IOError("Downloaded byte count does not match expected file size.")

    print("Download complete.")
    print("File transfer successful.")


# Prompt user and run one download request.
def main() -> None:
    print(f"Server: {HOST}:{PORT}")

    try:
        # Create Socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            print(f"Connected to {HOST}:{PORT}")

            #Prompt the user to enter a filename
            requested_file = input("Enter file name to download: ").strip()

            #Validate file existence
            if not requested_file:
                print("No file name provided.")
                return

            request_file(client_socket,requested_file)

    except ConnectionRefusedError:
        print("Could not connect. Start fileserver.py first.")
    except (ValueError, ConnectionError, OSError, IOError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()