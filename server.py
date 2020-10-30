import selectors
import socket
import sys

def get_host_port():
    host = "127.0.0.1"
    port = 1500
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    return host, port


def accept(sock, mask, clients):
    conn, addr = sock.accept()
    host, port = addr
    clients[conn.fileno()] = conn
    print("Accepted connection from", addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask, clients):
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
    sel = selectors.DefaultSelector()

    address = get_host_port()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(address)
    sock.listen()
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)
    _, port = address
    print(f"Server waiting for Clients on port {port}")

    clients = {}

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask, clients)


