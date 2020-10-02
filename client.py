import socket
import sys
import threading


motd = """Hello.! Welcome to the chatroom.
Instructions:
1. Simply type the message to send broadcast to all active clients
2. Type '@username<space>yourmessage' without quotes to send message to desired client
3. Type 'WHOISIN' without quotes to see list of active clients
4. Type 'LOGOUT' without quotes to logoff from server
"""


def get_host_port():
    if len(sys.argv) != 3:
        raise Exception("2 arguments required: [server host] [port number]")
    return sys.argv[1], int(sys.argv[2])


def get_server_socket(host, port):
    # Create an INET, STREAM (TCP) socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, port))
    print(f"Connection accepted {host}:{port}\n")
    return server


def login(server, username):
    server.send(str.encode(username + "\n"))
    print(motd, end="")


def listen_fn(name, server):
    while data := server.recv(1024).decode("utf-8"):
        # Tokenize and remove all empty lines.
        lines = (l for l in data.split("\n") if l != '')
        # Pretty print lines
        for line in lines:
            print(f"{line}\n")


def who_is_in(server):
    server.send(b"users\n")


def logout(server):
    server.send(b"exit\n")
    print("*** Server has closed the connection ***")


def broadcast(server, sender, message):
    payload = f"msg{message}\n"
    server.send(str.encode(payload))


def private_message(server, sender, recipient, message):
    """
    While this method may seem redundant, we want to ensure
    modularity and document all behaviours clearly in code.
    """
    payload = f"msg@{recipient} {message}\n"
    server.send(str.encode(payload))


def handle_input(server):
    """
    Returns True if the program should continue execution.
    Otherwise, returns False.
    """
    command = input()
    # Ignore empty commands
    if command == "":
        return True

    if command == "WHOISIN":
        who_is_in(server)
    elif command == "LOGOUT":
        logout(server)
        return False
    elif command.startswith("@"):
        tokens = command[1:].split(" ", maxsplit=1)
        if len(tokens) != 2:
            return
        recipient, message = tokens
        private_message(server, username, recipient, message)
    else:
        broadcast(server, username, command)

    return True


if __name__ == "__main__":
    host, port = get_host_port()
    username = input("Enter the username:\n")
    server = get_server_socket(host, port)

    # Server initialized.
    login(server, username)
    # Listen for messages from the server.
    listen_thread = threading.Thread(target=listen_fn, args=(1, server))
    listen_thread.start()
    # Listen for keyboard events to send to the server.
    while handle_input(server):
        pass

