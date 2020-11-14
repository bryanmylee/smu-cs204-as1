# Networking Assignment 1

`client.py` and `server.py` contain my implementation of the required server and client for the application.

`sample/` contains the prebuilt server and client that was to be emulated. Either server and client should be compatible with each other, as they should in principle adopt the same protocol as reverse engineered in `meta/PROTOCOL.md`.

## Running the client

To run the client, simply run:

```bash
python3 client.py {server host} {server port}
```

Make sure to use Python 3.7 or above.

## Running the server

To run the server, simply run:

```bash
python3 server.py [{server port}]
```

