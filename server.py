from datetime import datetime
import selectors
import socket
import sys


class Client:
    def __init__(self, conn):
        self.conn = conn
        self.username = None
        self.is_logged_in = False
        self.since = None


def get_timestamp(now=datetime.now()):
    return now.strftime("%H:%M:%S")


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
    global sel
    conn, addr = server.accept()
    host, port = addr
    clients[conn.fileno()] = Client(conn)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, listen_fn)


def listen_fn(conn, mask, clients):
    global sel
    # Get the matching Client object for the given connection.
    client = clients[conn.fileno()]
    # Non-blocking conn should be ready for just one recv.
    data_bytes = conn.recv(1024)
    if not data_bytes:
        logout(client, clients, proper=False)
        return

    data = data_bytes.decode("utf-8")[:-1]
    if not client.is_logged_in:
        username = data
        login(client, username, clients)
        return
    if data.startswith("users"):
        whoisin(client, clients)
        return
    if data.startswith("exit"):
        logout(client, clients)
        return
    if data.startswith("msg@"):
        recipient_name, message = data[4:].split(" ", maxsplit=1)
        private_message(client, clients, recipient_name, message)

    print(f"{get_timestamp()} Echoing {data[:-1]} to {conn}")
    for key, client in clients.items():
        if key != conn.fileno():
            client.conn.send(data_bytes)


def broadcast(sender: Client, message, clients):
    for client in clients.values():
        if sender.conn != client.conn:
            client.conn.send(str.encode(message))


def login(client: Client, with_username, clients):
    global port
    now = datetime.now()
    client.is_logged_in = True
    client.username = with_username
    client.since = now
    print(f"{get_timestamp(now)} *** {client.username} has joined the chat room. ***")
    print(f"{get_timestamp(now)} Server waiting for Clients on port {port}.")
    message = f"{get_timestamp(now)} *** {client.username} has joined the chat room. ***\n\n"
    broadcast(client, message, clients)


def whoisin(asker: Client, clients):
    lines = [f"List of the users connected at {get_timestamp()}"]
    client_list = list(clients.values())
    client_list.sort(key=lambda c: c.since)
    for i, client in enumerate(client_list):
        timestamp = client.since.strftime("%a %b %d %H:%M:%S SGT %Y")
        lines.append(f"{i + 1}) {client.username} since {timestamp}")
    response = "\n\n".join(lines) + "\n\n"
    asker.conn.send(str.encode(response))


def logout(asker: Client, clients, proper=True):
    global sel
    if proper:
        print(f"{get_timestamp()} {asker.username} disconnected with a LOGOUT message.")
    else:
        print(f"{get_timestamp()} {asker.username} disconnected badly.")
    asker.conn.send(b"*** Server has closed the connection ***")
    asker.conn.close()
    clients.pop(asker.conn.fileno(), None)
    sel.unregister(asker.conn)


def private_message(sender, clients, recipient_name, message):
    formatted_message = f"{get_timestamp()} {sender.username}:{message}\n\n"
    for client in clients.values():
        if client.username == recipient_name:
            client.conn.send(str.encode(formatted_message))


if __name__ == "__main__":
    global port
    global sel
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


