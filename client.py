import json
import socket
import threading
import time
import pygame.event
import game
from ImageLabel import ImageLabel
from constants import SERVER_IP, SERVER_PORT, LOADING_IMG, WHITE_CONTROLS, BLACK_CONTROLS
import chatlib
import tkinter as tk
from tkinter import messagebox
import ipaddress


class Client:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.__status_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = 0
        self.game = None
        self.server_ip = SERVER_IP
        self.server_port = SERVER_PORT

    def build_and_send_message(self, command: str, data: str) -> None:
        message = chatlib.build_message(command, data) + chatlib.END_OF_MESSAGE
        self.__socket.send(message.encode())
        print("[SERVER] -> [{}]:  {}".format(self.__socket.getpeername(), message))

    def recv_message_and_parse(self) -> tuple:
        try:
            full_msg = ''
            while True:
                char = self.__socket.recv(1).decode()
                if char == chatlib.END_OF_MESSAGE:
                    break
                full_msg += char
            cmd, data = chatlib.parse_message(full_msg)
            print("[{}] -> [SERVER]:  {}".format(self.__socket.getpeername(), full_msg))
            return cmd, data
        except:
            return None, None

    def connect(self):
        try:
            self.__socket.connect((self.server_ip, self.server_port))
            cmd, data = self.recv_message_and_parse()
            if cmd == chatlib.PROTOCOL_SERVER['error_msg']:
                raise Exception("ERROR: " + data)
            elif cmd == chatlib.PROTOCOL_SERVER['connected_successfully']:
                data = int(data)
                if data == 0 or data == 1:
                    self.id = data
            elif cmd == chatlib.PROTOCOL_SERVER['connection_limit']:
                raise Exception("Game is full.")
            else:
                raise Exception("Invalid connection message:", cmd, data)

        except Exception as e:
            return "Connection Error!!! " + str(e)

    def startup_screen(self):
        root = tk.Tk()
        root.title("Game Startup")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        startup_width = 400
        startup_height = 500
        root.geometry(f'{startup_width}x{startup_height}+{int(screen_width / 2 - startup_width / 2)}'
                      f'+{int(screen_height / 2 - startup_height / 2)}')
        root.protocol('WM_DELETE_WINDOW', exit)
        root.configure(bg='#fff')
        root.resizable(False, False)

        tk.Label(root, text='', bg='#fff').pack()
        heading = tk.Label(root, text="Jet Fighter", font=('Calibri Bold', 50), bg='#fff')
        heading.pack()

        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()
        ip = tk.Entry(root, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14))
        ip.insert(0, 'Server IP')
        ip.pack()

        def on_enter_ip(event):
            ip.delete(0, tk.END)

        def on_leave_ip(event):
            name = ip.get()
            if name == '':
                ip.insert(0, 'Server IP')

        ip.bind('<FocusIn>', on_enter_ip)
        ip.bind('<FocusOut>', on_leave_ip)

        tk.Frame(root, width=295, height=2, bg='black').pack()
        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()
        port = tk.Entry(root, width=25, fg='black', border=0, bg='white', font=('Microsoft YaHei UI Light', 14))
        port.insert(0, 'Server port')
        port.pack()

        def on_enter_port(event):
            port.delete(0, tk.END)

        def on_leave_port(event):
            name = port.get()
            if name == '':
                port.insert(0, 'Server port')

        port.bind('<FocusIn>', on_enter_port)
        port.bind('<FocusOut>', on_leave_port)

        tk.Frame(root, width=295, height=2, bg='black').pack()

        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()
        tk.Label(root, text='', bg='#fff').pack()

        def wait_start_msg(result: list):
            global destroy_screen
            cmd, data = self.recv_message_and_parse()
            if cmd != chatlib.PROTOCOL_SERVER['game_starting_message']:
                messagebox.showerror("Game Start Error", "Error while waiting for another player to connect.")
                result.append(True)
                connect_and_start()
            result.append(True)
            return 1

        def connect_and_start():
            ip_txt = ip.get()
            port_txt = port.get()
            try:
                ipaddress.ip_address(ip_txt)
            except:
                messagebox.showerror("Invalid IP", "This IP address is invalid")
                return
            self.server_ip = ip_txt
            if not port_txt.isnumeric() or port_txt == '' or port_txt is None or not 0 <= int(port_txt) <= 65535:
                messagebox.showerror("Type Error", "Port must be a number between 0 and 65,535")
                return
            self.server_port = int(port_txt)
            status = self.connect()
            if status:
                messagebox.showerror("Error", status)
                return

            root.destroy()
            if self.id == 0:
                waiting_screen = tk.Tk()
                waiting_screen.geometry("400x400")
                waiting_screen.overrideredirect(True)
                waiting_screen.eval('tk::PlaceWindow . center')
                waiting_screen.configure(bg='white')
                result = []
                wait = threading.Thread(target=wait_start_msg, args=[result])
                wait.start()
                tk.Label(text="Waiting for opponent to connect", font=('Calibri Bold', 20), background='white').pack()
                img = ImageLabel()
                img.pack()
                img.load(LOADING_IMG)
                while True:
                    waiting_screen.update()
                    waiting_screen.update_idletasks()
                    if result:
                        waiting_screen.destroy()
                        break
                    time.sleep(0.01)

        bt = tk.Button(root, width=27, pady=7, text='Connect', bg='#7b7b7b', fg='white', border=0,
                       font=('Calibri Bold', 14), command=connect_and_start)
        bt.pack()
        root.mainloop()

    def disconnect(self):
        self.build_and_send_message(chatlib.PROTOCOL_CLIENT['disconnect_msg'], '')
        self.__socket.close()
        exit()

    def request_game_obj(self) -> None or int:
        try:
            self.build_and_send_message(chatlib.PROTOCOL_CLIENT['game_status_request'], '')
        except socket.error:
            return None
        cmd, data = self.recv_message_and_parse()
        if cmd != chatlib.PROTOCOL_SERVER['game_status_response']:
            if cmd == chatlib.PROTOCOL_SERVER['winner_msg']:
                if self.id == int(data):
                    messagebox.showinfo('Game Ended!', 'Congratulations! You Won!!!')
                else:
                    messagebox.showinfo('Game Ended!', 'You Lost!!!')
                self.disconnect()
            return None
        try:
            game_data = json.loads(data)
            self.game.score_0 = game_data['score_0']
            self.game.score_1 = game_data['score_1']
            for i in range(len(self.game.planes)):
                self.game.planes[i].data_from_dict(game_data['planes'][i])
            return 1
        except:
            return None

    def request_initial_data(self) -> dict or None:
        try:
            self.build_and_send_message(chatlib.PROTOCOL_CLIENT['initial_details'], '')
        except socket.error:
            return None
        cmd, data = self.recv_message_and_parse()
        if cmd != chatlib.PROTOCOL_SERVER['initial_data_response']:
            return None
        try:
            data = json.loads(data)
            return data
        except:
            return None

    def handle_key_press(self, key: int):
        if self.id == 1:
            if key == pygame.K_RIGHT:
                key = pygame.K_d
            elif key == pygame.K_LEFT:
                key = pygame.K_a
        if (self.id == 0 and key in WHITE_CONTROLS) or (self.id == 1 and key in BLACK_CONTROLS) \
                or key == pygame.K_SPACE:
            self.build_and_send_message(chatlib.PROTOCOL_CLIENT['key_down_msg'], str(key))

    def handle_key_release(self, key: int):
        if self.id == 1:
            if key == pygame.K_RIGHT:
                key = pygame.K_d
            elif key == pygame.K_LEFT:
                key = pygame.K_a
        if (self.id == 0 and key in WHITE_CONTROLS) or (self.id == 1 and key in BLACK_CONTROLS):
            self.build_and_send_message(chatlib.PROTOCOL_CLIENT['key_up_msg'], str(key))

    def start(self):
        self.startup_screen()
        init_data = self.request_initial_data()
        if not init_data:
            messagebox.showerror('Data error', 'Could\'nt get game data')
            exit()
        screen_width = init_data['width']
        screen_height = init_data['height']
        plane_pos = init_data['planes_pos']
        self.game = game.Game(screen_width, screen_height, plane_pos)
        self.game.initialise_window()
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    self.handle_key_press(key)
                elif event.type == pygame.KEYUP:
                    key = event.key
                    self.handle_key_release(key)
            self.request_game_obj()
            self.game.draw()
        self.disconnect()


if __name__ == '__main__':
    client = Client()
    client.start()
