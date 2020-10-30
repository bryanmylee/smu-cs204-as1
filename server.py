from datetime import datetime
import selectors
import socket
import sys


class Client:
    def __init__(self, conn):
        self.conn = conn
        self.username = None
        self.is_logged_in = False


def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")


def get_host_port():
    host = "127.0.0.1"
    port = 1500
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    return host, port


def create_async_server_socket(host, port):
    # Create an INET, STREAM (TCP) socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.setblocking(False)
    print(f"{get_timestamp()} Server waiting for Clients on port {port}.")
    return server


def accept_fn(server, mask, clients):
    conn, addr = server.accept()
    host, port = addr
    clients[conn.fileno()] = Client(conn)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, listen_fn)


def listen_fn(conn, mask, clients):
    # Get the matching Client object for the given connection.
    client = clients[conn.fileno()]
    # Non-blocking conn should be ready for just one recv.
    data_bytes = conn.recv(1024)
    if not data_bytes:
        # Connection was forcibly closed.
        print(f"{get_timestamp()} Closing {conn}")
        sel.unregister(conn)
        conn.close()
        clients.pop(conn.fileno(), None)
        return

    data = data_bytes.decode("utf-8")
    if not client.is_logged_in:
        username = data[:-1]
        login(client, username, clients)
        return

    print(f"{get_timestamp()} Echoing {data[:-1]} to {conn}")
    for key, client in clients.items():
        if key != conn.fileno():
            client.conn.send(data_bytes)


def login(client, username, clients):
    global port
    client.is_logged_in = True
    client.username = username
    print(f"{get_timestamp()} *** {username} has joined the chat room. ***")
    print(f"{get_timestamp()} Server waiting for Clients on port {port}.")


if __name__ == "__main__":
    global port
    host, port = get_host_port()
    server = create_async_server_socket(host, port)
    # Create a selector with socket object key and a function value that
    # accepts a socket, mutex mask, and a map from socket file number to socket.
    sel = selectors.DefaultSelector()
    sel.register(server, selectors.EVENT_READ, accept_fn)

    # A map from a socket file number key to a Client object.
    clients = {}
    while True:
        # Get all socket object keys in the selector.
        for key, mask in sel.select():
            # Either the accept_fn or listen_fn.
            fn = key.data
            conn = key.fileobj
            fn(conn, mask, clients)


