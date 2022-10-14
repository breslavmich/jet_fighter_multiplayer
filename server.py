# Michael Breslavsky - 12A
# 14.10.2022
# File: server.py
# Description: Server side for managing the 'Jet Fighter' game
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
        """Setting up the socket for the server"""
        try:
            address = (self.listen_ip, self.port)
            self.__server_socket.bind(address)
            self.__server_socket.listen()
            print("[SERVER] Listening for connections...")
        except socket.error as e:
            print("[SERVER] An error occurred:", str(e))
            exit()

    def build_and_send_message(self, client_socket: socket.socket, command: str, data: str) -> None:
        """Building a message according to the protocol and sending it to the client"""
        message = chatlib.build_message(command, data) + chatlib.END_OF_MESSAGE
        self.messages_to_send.append((client_socket, message))
        print("[SERVER] -> [{}]:  {}".format(client_socket.getpeername(), message))

    def recv_message_and_parse(self, client_socket: socket.socket) -> tuple:
        """Receiving a message from the client and parsing it according to the protocol"""
        try:
            full_msg = ''
            while True:  # Receiving a message in a loop a character at a time until message end character appears
                char = client_socket.recv(1).decode()
                if char == chatlib.END_OF_MESSAGE:
                    break
                full_msg += char
            cmd, data = chatlib.parse_message(full_msg)
            print("[{}] -> [SERVER]:  {}".format(client_socket.getpeername(), full_msg))
            return cmd, data
        except:
            return None, None

    def disconnected_player(self, disconnected_socket: socket.socket) -> None:
        """Disconnecting a player from the server"""
        if not self.winner:  # If the disconnected plater left before the game ended, the second player wins
            winner_id = 1 - self.players.index(disconnected_socket)
            self.winner = winner_id
        self.players.remove(disconnected_socket)
        disconnected_socket.close()  # Closing the player's socket
        if len(self.players) == 0:  # If the last player left, restarting the server
            self.__server_socket.close()
            self.__init__()
            self.start()

    def handle_client_key_down(self, client_socket: socket.socket, data: str) -> None:
        """Handling message that client pressed a key"""
        try:
            data = int(data)  # Key should be in int format
        except:
            return
        plane_num = self.players.index(client_socket)  # Getting player's index
        if plane_num == 0:  # If the player is white
            if data == pygame.K_LEFT:
                self.game.planes[plane_num].rotate_amount = ROTATE_AMOUNT
            elif data == pygame.K_RIGHT:
                self.game.planes[plane_num].rotate_amount = -ROTATE_AMOUNT
        elif plane_num == 1:  # If the player is black
            if data == pygame.K_a:
                self.game.planes[plane_num].rotate_amount = ROTATE_AMOUNT
            elif data == pygame.K_d:
                self.game.planes[plane_num].rotate_amount = -ROTATE_AMOUNT
        if data == pygame.K_SPACE:  # Space key is valid for both colors
            if plane_num == 0:
                if time.time() - self.last_shot_white < 1.5:  # Checking if the player can already shoot again
                    return
                else:
                    self.last_shot_white = time.time()
            elif plane_num == 1:
                if time.time() - self.last_shot_black < 1.5:  # Checking if the player can already shoot again
                    return
                else:
                    self.last_shot_black = time.time()
            self.game.planes[plane_num].shoot()  # Shooting a bullet

    def handle_client_key_up(self, client_socket: socket.socket, data: str) -> None:
        """Handling message that client released a key"""
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
        """Sending the current game status to the client"""
        if self.winner == 0 or self.winner == 1:  # If there is a winner sending a winner message
            self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['winner_msg'], str(self.winner))
        else:
            game_str = json.dumps(self.game.up_to_date_game_data())
            # Getting game data in the form of a dictionary dumped into string format and sending it to the client
            self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['game_status_response'], game_str)

    def handle_game_init_request(self, client_socket: socket.socket):
        """Handling initial game data request"""
        initial_data = json.dumps(self.game.get_init_data())
        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['initial_data_response'], initial_data)

    def handle_message(self, client_socket: socket.socket, command: str, data: str) -> None:
        """Calling appropriate function for each request"""
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
        """Updating game data"""
        while self.game_running:
            self.game.update()
            self.game.clock.tick(FPS)

    def start(self) -> None:
        """Starting the server and listening for connections and requests"""
        pygame.init()  # Initialising pygame
        threading.Thread(target=self.update_game).start()  # Updating game in separate thread
        while True:
            if self.game.hits:  # If any of the bullets hit a plane updating the score
                for bullet in self.game.hits:
                    if bullet.is_white:
                        self.game.score_0 += 1
                    else:
                        self.game.score_1 += 1
                    self.game.hits.remove(bullet)
            # Checking if a player has won
            if self.game.score_0 == 5:
                self.winner = 0
            elif self.game.score_1 == 5:
                self.winner = 1
            # Checking if there are messages available of players that try to connect
            read_list, write_list, error_list = select.select([self.__server_socket] + self.players, self.players, [])
            for current_socket in read_list:
                if current_socket is self.__server_socket:  # If a new client is trying to connet
                    client_socket, client_address = self.__server_socket.accept()
                    if len(self.players) >= 2:  # Checking if the max amount of clients is reached
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connection_limit'], '')
                        client_socket.close()
                    else:
                        # Connecting the player
                        player_id = len(self.players)  # Getting the player's ID
                        self.build_and_send_message(client_socket, chatlib.PROTOCOL_SERVER['connected_successfully'],
                                                    str(player_id))  # Sending the connection successful message
                        self.players.append(client_socket)
                        if player_id == 1:
                            # If the second player connected, sending the first player a game start message
                            self.build_and_send_message(self.players[0],
                                                        chatlib.PROTOCOL_SERVER['game_starting_message'], '')
                else:  # If a player sent a request
                    command, data = self.recv_message_and_parse(current_socket)  # Receiving the request
                    if command is None:  # If there was an error with the message
                        self.disconnected_player(current_socket)  # Disconnecting the client
                    try:
                        self.handle_message(current_socket, command, data)  # Handling the client's message
                    except socket.error:
                        self.disconnected_player(current_socket)  # If an error occurs disconnecting client

            # Sending all the messages which can be sent
            for message in self.messages_to_send:
                current_socket, data = message
                if current_socket in write_list:
                    if current_socket in self.players:
                        current_socket.send(data.encode())
                        self.messages_to_send.remove(message)


if __name__ == '__main__':
    server = Server()
    server.start()
