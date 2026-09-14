# CS310 Assignment 1: TCP File Transfer Application

## Contributors
- Rohan Nand (S11234883)
- Zhixian Chen (S11230686)

## Overview
A simple TCP file transfer system in Python 3 with a custom, line-based application protocol. The client requests a file by name, the server validates the request, and the file is streamed in fixed-size chunks.

## Requirements
- Python 3.x
- Run fileserver.py, client.py, and the files to be transferred from the same directory

## Quick Start
1. Start the server:
	```
	python3 fileserver.py
	```
2. Start the client in another terminal:
	```
	python3 client.py
	```
3. Enter the file name when prompted.
4. The client saves the file and exits. The server keeps running until you stop it.

## Protocol Summary
- Client request: FILE_REQUEST|<filename>\n
- Server responses:
  - STATUS|OK|<filename>|<size>\n
  - STATUS|ERROR|<message>\n

## Features
- Custom request/response headers on top of TCP
- Server-side filename validation using basename to block path traversal
- Binary transfer in 4096-byte chunks
- Client-side progress reporting during download
- Connection and I/O error handling on both ends

## Output Files
By default, the client saves downloads as <name>_downloaded.<ext> in the current directory.

