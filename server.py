import socket
import select
import pickle


HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# -------------------- CREATE SERVER SOCKET -------------------- #
# AF_INET => IPv4
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]  # All sockets
clients_list = {}               # client sockets

print(f'Listening for connections on {IP}:{PORT}...')


# -------------------- RECEIVE MESSAGE -------------------- #
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # not get any data
        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {
            "header": message_header,
            "data":client_socket.recv(message_length)
        }

    except:
        return False

# -------------------- SERVER CONNECT TO CLIENT -------------------- #


while True:

    # select.select(read list, write list, excption list)
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # ------------- NEW CLIENT CONNECTION ------------- #
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients_list[client_socket] = user

            print(f"Accept new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")

        # ------------- EXISTING CLIENT ------------- #
        else:
            message = receive_message(notified_socket)
            #print(f"message: {message}")

            # ---------- DISCONNECT ---------- #
            if message is False:
                print(f"Closed connection from {clients_list[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients_list[notified_socket]
                continue

            # ---------- RECEIVE MESSAGE ---------- #

            user = clients_list[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients_list:
                if client_socket != notified_socket:
                    client_socket.send(user['header']+user['data']+message['header']+message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients_list[notified_socket]

# socket.error: [Errno 48] Address already in use:
# ps -fA | grep python
# kill (third number)


# Reference: https://www.youtube.com/watch?v=Lbfe3-v7yE0&list=PLQVvvaa0QuDdzLB_0JSTTcl8E8jsJLhR5