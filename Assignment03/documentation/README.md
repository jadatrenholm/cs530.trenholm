# Assignment03 - TCP Client/Server

## Overview
A TCP server accepts register/unregister messages:
- "R <id>" registers a client
- "U <id>" unregisters a client

The server broadcasts a timestamp to registered clients every 5–30 seconds.
Clients write received timestamps to a text file. The server logs events to server.log.

## Run Instructions (localhost)
Open two terminals in Assignment03/code.

### Terminal 1 (Server)
python server.py --host 127.0.0.1 --port 5000 --client-port 5001 --log server.log

### Terminal 2 (Client)
python client.py --id 1 --server-host 127.0.0.1 --server-port 5000 --listen-host 127.0.0.1 --listen-port 5001

## Output Files
- server.log
- client_<id>.txt