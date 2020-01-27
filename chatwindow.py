import os
import sys
# import server
import client
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from functools import partial


# ----------------- AUTO SCROLL WHEN NEW MESSAGE ----------------- #
class ScrollLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols = 1, size_hint_y=None)
        self.add_widget(self.layout)

        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history(self, message):

        self.chat_history.text += '\n' + message

        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

        self.scroll_to(self.scroll_to_point)


# ----------------- SIGN IN PAGE ----------------- #
class ConnectPage(GridLayout):
    def __init__(self, **kwargs):
        super(ConnectPage, self).__init__(**kwargs)
        self.cols = 2

        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]

        else:
            prev_ip = ""
            prev_port = ""
            prev_username = ""

        self.add_widget(Label(text="IP: "))
        self.ip = TextInput(text=prev_ip, multiline=False)
        self.add_widget(self.ip)

        self.add_widget(Label(text="PORT: "))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text="Username: "))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)

        self.join = Button(text="Join")
        self.add_widget(Label())
        self.join.bind(on_press=self.join_button)
        self.add_widget(self.join)

    def join_button(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")

        info = f"Attemping to join {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)

        # ------------ CHANGE PAGE ------------ #
        chat_app.screen_manager.current = "Info"
        Clock.schedule_once(self.connect, 1)

    def connect(self, _):
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text

        chat_app.my_client = client.Client(ip, port, username, show_error)

        # print(chat_app.my_client.client_socket)
        if not chat_app.my_client.client_socket:
            return

        # since chat page listen to connection
        # so we have to create chatpage after connection
        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"


# ----------------- INFO PAGE ----------------- #
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super(InfoPage, self).__init__(**kwargs)
        self.cols = 1
        self.message = Label(halign="center", valign="middle", font_size=30)
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


# ----------------- CHAT PAGE ----------------- #
class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super(ChatPage, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        # -------------- FIRST ROW -------------- #

        # Window.size[0] is x, Window.size[1] is y
        self.history = ScrollLabel(height=Window.size[1] * 0.8, size_hint_y=None)
        self.add_widget(self.history)

        # -------------- SECOND ROW -------------- #
        self.new_message = TextInput(width=Window.size[0] * 0.8, size_hint_x=None, multiline=False)
        self.send = Button(text = "Send")
        self.send.bind(on_press=self.send_message)

        lower_page = GridLayout(cols = 2)
        lower_page.add_widget(self.new_message)
        lower_page.add_widget(self.send)
        self.add_widget(lower_page)

        # bind enter with send
        Window.bind(on_key_down = self.on_key_down)

        # check input per 1 sec
        Clock.schedule_once(self.focus_text_input, 1)
        Clock.schedule_interval(self.receive_message, 1)
        #chat_app.my_client.client_listening(self.incoming_message, show_error)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # Enter key = 40
        if keyboard == 40:
            self.send_message(None)

    def receive_message(self, _):
        chat_app.my_client.client_listening(self.incoming_message, show_error)

    def send_message(self, _):

        # get the input message
        message = self.new_message.text
        chat_app.my_client.client_listening(self.incoming_message, show_error)

        # clean the input box
        self.new_message.text = ""

        if message:
            self.history.update_chat_history(f'[color=fcc3c3]{chat_app.connect_page.username.text}[/color] > {message}')
            chat_app.my_client.client_send(message)

        Clock.schedule_once(self.focus_text_input, 0.1)

    def focus_text_input(self,_):
        self.new_message.focus = True


    def incoming_message(self, username, message):
        self.history.update_chat_history(f"[color=bee3f5]{username}[/color] > {message}")



class ChatWindow(App):
    def build(self):
        # -------------- ALL SCREEN -------------- #
        self.screen_manager = ScreenManager()

        # -------------- CONNECT PAGE -------------- #
        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        # -------------- IFNO PAGE -------------- #
        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        self.my_client = None

        return self.screen_manager

    def create_chat_page(self):
        # -------------- CHAT PAGE -------------- #
        self.chat_page = ChatPage()
        screen = Screen(name="Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)


def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = ChatWindow()
    chat_app.run()

# Ignore a value when unpacking
# x, _, y = (1, 2, 3)  # x = 1, y = 3
#  Ignore the multiple values. It is called "Extended Unpacking" which is available in only Python 3.x
# x, *_, y = (1, 2, 3, 4, 5)  # x = 1, y = 5  # Ignore the index
