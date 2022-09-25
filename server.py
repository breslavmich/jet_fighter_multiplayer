import socket

import pygame
import select
from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_LISTEN_IP, SERVER_PORT, ROTATE_AMOUNT
import chatlib


class Server:
    def __init__(self):
        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_ip = SERVER_LISTEN_IP
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

    def disconnected_player(self, disconnected_socket: socket.socket) -> None:
        winner_id = 1 - self.players.index(disconnected_socket)
        self.build_and_send_message(self.players[winner_id], chatlib.PROTOCOL_SERVER['winner_msg'], str(winner_id))
        self.players.remove(disconnected_socket)
        disconnected_socket.close()

    def handle_shoot_message(self, client_socket: socket.socket) -> None:
        player_id = self.players.index(client_socket)
        self.game.planes[player_id].shoot()

    def handle_client_key_down(self, client_socket: socket.socket, data: str) -> None:
        try:
            data = int(data)
        except:
            return
        plane_num = self.game.planes.index(client_socket)
        if plane_num == 0:
            if data == pygame.K_LEFT:
                self.game.planes[plane_num].rotate_amount = ROTATE_AMOUNT
            elif data == pygame.K_RIGHT:
                self.game.planes[plane_num].rotate_amount = -ROTATE_AMOUNT
        elif plane_num == 1:
            pass

    def handle_message(self, client_socket: socket.socket, command: str, data: str) -> None:
        if command == chatlib.PROTOCOL_CLIENT['disconnect_msg']:
            self.disconnected_player(client_socket)
        elif command == chatlib.PROTOCOL_CLIENT['shoot_command']:
            self.handle_shoot_message(client_socket)
        elif command == chatlib.PROTOCOL_CLIENT['key_down_msg']:
            self.handle_client_key_down(client_socket, data)

    def start(self) -> None:
        while True:
            read_list, write_list, error_list = select.select([self.__server_socket] + self.players, self.players, [])
            for current_socket in read_list:
                if current_socket is self.__server_socket:
                    client_socket, client_address = self.__server_socket.accept()
                    if len(self.players) >= 2:
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connection_limit'], '')
                        client_socket.close()
                    else:
                        player_id = len(self.players)
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connected_successfully'],
                                                    str(player_id))
                else:
                    command, data = self.recv_message_and_parse(current_socket)
                    try:
                        self.handle_message(current_socket, command, data)
                    except socket.error:
                        self.disconnected_player(current_socket)

            for message in self.messages_to_send:
                current_socket, data = message
                if current_socket in write_list:
                    if current_socket in self.players:
                        current_socket.send(data.encode())
                        self.messages_to_send.remove(current_socket)
