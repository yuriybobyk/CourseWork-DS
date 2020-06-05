import os
import socket
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox
import numpy as np
import threading


class Client:
    client_socket = None
    last_received_message = None

    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.echo_text_widget = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.initialize_socket()
        self.filename_widget = None
        self.initialize_gui()
        self.on_generate_button = None
        self.echo_button = None
        self.ping_button = None
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = 'localhost'
        remote_port = 10319
        self.client_socket.connect((remote_ip, remote_port))

    def initialize_gui(self):
        self.root.title("Socket GUI")
        self.root.resizable(0, 0)
        self.display_filename_section()
        self.display_echo_text_section()
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()
        self.display_ping_section()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has now joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            elif "echo" in message:
                echo_command = message.split(":")[1]
                message = echo_command + "is echo command"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join chat", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='GUI chat box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Your message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')

    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def display_echo_text_section(self):
        frame = Frame()
        Label(Label(frame, text='Enter an echo text:', font=('Helvetica', 12)).pack(side='left', padx=10))
        self.echo_text_widget = Entry(frame, width=50, borderwidth=2)
        self.echo_text_widget.pack(side='left', anchor='sw')
        self.echo_button = Button(frame, text='Echo', width=10, command=self.on_echo).pack(side='left')
        frame.pack(side='bottom', anchor='e')

    def on_echo(self):
        if len(self.echo_text_widget.get()) == 0:
            messagebox.showerror("Enter a text to send an echo command.")
            return
        else:
            self.echo_text_widget.config(state='disabled')
            self.client_socket.send(("echo:" + self.echo_text_widget.get()).encode('utf-8'))

    def display_filename_section(self):
        frame = Frame()
        Label(frame, text='Enter your filename:', font=('Helvetica', 12)).pack(side='left', padx=10)
        self.filename_widget = Entry(frame, width=50, borderwidth=2)
        self.filename_widget.pack(side='left', anchor='sw')
        self.on_generate_button = Button(frame, text='Generate', width=10, command=self.on_generate_button).pack(side=
                                                                                                                 'left')
        frame.pack(side='bottom', anchor='e')

    def generate_file(self, file_name):
        numbers = [np.random.randint(0, 1000000000) for _ in range(1000002)]
        new_file = open(file_name, 'a')
        new_file.write(str(numbers).replace(", ", " "))

    def send_file(self, file_name):
        self.client_socket.send(("file_name:" + file_name).encode('utf-8'))

    def on_generate_button(self):
        file_name = self.filename_widget.get()
        if len(file_name) == 0:
            messagebox.showerror(
                "Enter your filename to generate a file")
            return
        else:
            self.filename_widget.config(state='disabled')
            self.generate_file(file_name)
            self.send_file(file_name)

    def display_ping_section(self):
        frame = Frame()
        self.ping_button = Button(frame, text="Try Ping", width=10, command=self.on_ping).pack(side='bottom')
        frame.pack(side='bottom', anchor='s')

    def on_ping(self):
        hostname = "localhost"
        response = os.system("ping -c 1 " + hostname)
        # check the response...
        if response == 0:
            pingstatus = "Ping Active"
        else:
            pingstatus = "Ping Error"

        return self.chat_transcript_area.insert('end', pingstatus + '\n')

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to finish sesion?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = Client(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
root.mainloop()