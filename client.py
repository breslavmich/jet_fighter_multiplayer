import socket
from constants import SERVER_IP, SERVER_PORT
import chatlib
import tkinter as tk
from tkinter import messagebox


class Client:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = 0
        self.game = None
        self.server_ip = SERVER_IP
        self.server_port = SERVER_PORT

    def build_and_send_message(self, command: str, data: str) -> None:
        message = chatlib.build_message(command, data)
        self.__socket.send(message.encode())
        print("[SERVER] -> [{}]:  {}".format(self.__socket.getpeername(), message))

    def recv_message_and_parse(self) -> tuple:
        try:
            full_msg = self.__socket.recv(2048).decode()
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
            else:
                raise Exception("Invalid connection message:", cmd, data)

        except Exception as e:
            return "Connection Error!!!" + str(e)

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
        bt = tk.Button(root, width=27, pady=7, text='Connect', bg='#7b7b7b', fg='white', border=0, font=('Calibri Bold', 14))
        bt.pack()

        root.mainloop()


client = Client()
client.startup_screen()
