import json
import socket
import threading
import time

import pygame
import select
from game import Game
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_LISTEN_IP, SERVER_PORT, ROTATE_AMOUNT, FPS
import chatlib


class Server:
    def __init__(self):
        self.players_status = []
        self.game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__status_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_ip = SERVER_LISTEN_IP
        self.port = SERVER_PORT
        self.messages_to_send = []
        self.players = []
        self.setup_socket()
        self.game_running = True
        self.last_shot_white = 0
        self.last_shot_black = 0
        self.winner = None

    def setup_socket(self):
        try:
            print(self.__server_socket)
            address = (self.listen_ip, self.port)
            self.__server_socket.bind(address)
            self.__server_socket.listen()
            # self.__status_socket.bind((self.listen_ip, 5555))
            # self.__status_socket.listen()
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
        if not self.winner:
            winner_id = 1 - self.players.index(disconnected_socket)
            self.winner = winner_id
        self.players.remove(disconnected_socket)
        disconnected_socket.close()
        if len(self.players) == 0:
            exit()

    def handle_shoot_message(self, client_socket: socket.socket) -> None:
        player_id = self.players.index(client_socket)
        self.game.planes[player_id].shoot()

    def handle_client_key_down(self, client_socket: socket.socket, data: str) -> None:
        try:
            data = int(data)
        except:
            return
        plane_num = self.players.index(client_socket)
        if plane_num == 0:
            if data == pygame.K_LEFT:
                self.game.planes[plane_num].rotate_amount = ROTATE_AMOUNT
            elif data == pygame.K_RIGHT:
                self.game.planes[plane_num].rotate_amount = -ROTATE_AMOUNT
        elif plane_num == 1:
            if data == pygame.K_a:
                self.game.planes[plane_num].rotate_amount = ROTATE_AMOUNT
            elif data == pygame.K_d:
                self.game.planes[plane_num].rotate_amount = -ROTATE_AMOUNT
        if data == pygame.K_SPACE:
            if plane_num == 0:
                if time.time() - self.last_shot_white < 2:
                    return
                else:
                    self.last_shot_white = time.time()
            elif plane_num == 1:
                if time.time() - self.last_shot_black < 2:
                    return
                else:
                    self.last_shot_black = time.time()
            self.game.planes[plane_num].shoot()

    def handle_client_key_up(self, client_socket: socket.socket, data: str) -> None:
        try:
            data = int(data)
        except:
            return
        plane_num = self.players.index(client_socket)
        if plane_num == 0:
            if data == pygame.K_LEFT or data == pygame.K_RIGHT:
                self.game.planes[plane_num].rotate_amount = 0
        elif plane_num == 1:
            if data == pygame.K_a or data == pygame.K_d:
                self.game.planes[plane_num].rotate_amount = 0

    def handle_status_message(self, client_socket: socket.socket):
        if self.winner == 0 or self.winner == 1:
            self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['winner_msg'], str(self.winner))
        else:
            game_str = json.dumps(self.game.up_to_date_game_data())
            self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['game_status_response'], game_str)

    def handle_game_init_request(self, client_socket: socket.socket):
        initial_data = json.dumps(self.game.get_init_data())
        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['initial_data_response'], initial_data)

    def handle_message(self, client_socket: socket.socket, command: str, data: str) -> None:
        if command == chatlib.PROTOCOL_CLIENT['disconnect_msg']:
            self.disconnected_player(client_socket)
        elif command == chatlib.PROTOCOL_CLIENT['key_down_msg']:
            self.handle_client_key_down(client_socket, data)
        elif command == chatlib.PROTOCOL_CLIENT['game_status_request']:
            self.handle_status_message(client_socket)
        elif command == chatlib.PROTOCOL_CLIENT['initial_details']:
            self.handle_game_init_request(client_socket)
        elif command == chatlib.PROTOCOL_CLIENT['key_up_msg']:
            self.handle_client_key_up(client_socket, data)

    def update_game(self):
        while self.game_running:
            self.game.update()
            self.game.clock.tick(FPS)

    def start(self) -> None:
        pygame.init()
        threading.Thread(target=self.update_game).start()
        while True:
            if self.game.hits:
                for bullet in self.game.hits:
                    if bullet.is_white:
                        self.game.score_0 += 1
                    else:
                        self.game.score_1 += 1
                    self.game.hits.remove(bullet)
            if self.game.score_0 == 5:
                self.winner = 0
            elif self.game.score_1 == 5:
                self.winner = 1
            read_list, write_list, error_list = select.select([self.__server_socket] + self.players, self.players, [])
            for current_socket in read_list:
                if current_socket is self.__server_socket:
                    client_socket, client_address = self.__server_socket.accept()
                    # client_status, client_status_address = self.__status_socket.accept()
                    if len(self.players) >= 2:
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connection_limit'], '')
                        client_socket.close()
                        # client_status.close()
                    else:
                        player_id = len(self.players)
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connected_successfully'],
                                                    str(player_id))
                        self.players.append(client_socket)
                        # self.players_status.append(client_status)
                        if player_id == 1:
                            self.build_and_send_message(self.players[0],
                                                        chatlib.PROTOCOL_SERVER['game_starting_message'], '')
                else:
                    command, data = self.recv_message_and_parse(current_socket)
                    if command is None:
                        self.disconnected_player(current_socket)
                    try:
                        self.handle_message(current_socket, command, data)
                    except socket.error:
                        self.disconnected_player(current_socket)

            for message in self.messages_to_send:
                current_socket, data = message
                if current_socket in write_list:
                    if current_socket in self.players:
                        current_socket.send(data.encode())
                        self.messages_to_send.remove(message)


server = Server()
server.start()
