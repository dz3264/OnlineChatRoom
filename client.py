import socket
import select
import pickle
import errno
import sys

HEADER_LENGTH = 10

class Client():

    def __init__(self, ip, port, username, show_error):

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            client_socket.setblocking(False)

            username = username.encode('utf-8')
            username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(username_header + username)

            self.client_socket = client_socket

        except Exception as e:
            self.client_socket = None
            show_error(str(e))
            # sys.exit()

    def client_listening(self, incoming_message, show_error):

        try:
            username_header = self.client_socket.recv(HEADER_LENGTH)

            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())
            username = self.client_socket.recv(username_length).decode('utf-8')

            message_header = self.client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = self.client_socket.recv(message_length).decode('utf-8')

            incoming_message(username, message)


        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: ', str(e))
                show_error(str(e))
                # sys.exit()

        except Exception as e:

            print("General error: ", str(e))
            show_error(str(e))
            # sys.exit()


    # -------------------- MESSAGE COMMUNICATION -------------------- #
    def client_send(self, message):

        # ----------------- SEND MESSAGE ----------------- #
        # message = input(' >> ')
        # Automatic reader
        # message = ""
        if message and isinstance(message, str):
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)


"""
IP = "127.0.0.1"
PORT = 1234
my_username = 'Client Diana'

def show_error():
    return 1

def incomming_message(username, message):
    print(f"{username} > {message}")

my_client = Client(IP, PORT, my_username, show_error)
my_client.client_listening(incomming_message, show_error)
my_client.client_send("my message")
"""
