import selectors
import socket
import sys

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
    print(f"Server waiting for Clients on port {port}")
    return server


def accept_fn(server, mask, clients):
    conn, addr = server.accept()
    host, port = addr
    clients[conn.fileno()] = conn
    print("Accepted connection from", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, listen_fn)


def listen_fn(conn, mask, clients):
    data_bytes = conn.recv(1024)
    if data_bytes:
        print("Echoing", data_bytes.decode("utf-8"), "to", conn)
        for key, other_conn in clients.items():
            if key != conn.fileno():
                other_conn.send(data_bytes)
    else:
        print("Closing", conn)
        sel.unregister(conn)
        conn.close()
        clients.pop(conn.fileno(), None)


if __name__ == "__main__":
    host, port = get_host_port()
    server = create_async_server_socket(host, port)
    # Create a selector with socket object key and a function value that
    # accepts a socket, mutex mask, and a map from socket file number to socket.
    sel = selectors.DefaultSelector()
    sel.register(server, selectors.EVENT_READ, accept_fn)

    clients = {}
    while True:
        # Get all socket object keys in the selector.
        for key, mask in sel.select():
            # Either the accept_fn or listen_fn.
            fn = key.data
            conn = key.fileobj
            fn(conn, mask, clients)


