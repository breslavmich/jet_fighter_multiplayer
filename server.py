import socket
from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_IP, SERVER_PORT
import chatlib


class Server(Game):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_ip = SERVER_IP
        self.port = SERVER_PORT
        self.messages_to_send = []
        self.players = []
        self.setup_socket()

    def setup_socket(self):
        try:
            self.__server_socket.bind((self.listen_ip, self.port))
            self.__server_socket.listen()
            print("[SERVER] Listening for connections...")
        except socket.error as e:
            print("[SERVER] An error occurred:", str(e))
            exit()

    def build_and_send_message(self, client_socket: socket.socket, command: str, data: str) -> None:
        message = chatlib.build_message(command, data)
        self.messages_to_send.append((client_socket, message))
        print("[SERVER] -> [{}]:  {}".format(client_socket.getpeername(), message))

    def recv_message_and_parse(self, client_socket: socket.socket) -> tuple:
        try:
            full_msg = client_socket.recv(1024).decode()
            cmd, data = chatlib.parse_message(full_msg)
            print("[{}] -> [SERVER]:  {}".format(client_socket.getpeername(), full_msg))
            return cmd, data
        except:
            return None, None

