from tkinter import *

import ChatDirectory.client_chat
import candidate_gui
from ChatDirectory.client_chat import *


BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class chat_application_select_room_page:

    def __init__(self,):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("Secured Chat Authority (select room page)")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text='select room:', font="Helvetica 30 bold", pady=10)

        head_label.place(x=110, y=50)

        work_b = Button(self.window, text='work', font=FONT_BOLD, command=lambda: self.work_b())
        work_b.place(x=470/2-140/2, y=150, width=140, height=70)
        talking_b = Button(self.window, text='talking', font=FONT_BOLD, command=lambda: self.talking_b())
        talking_b.place(x=470 / 2 - 140 / 2, y=270, width=140, height=70)
        dating_b = Button(self.window, text='dating', font=FONT_BOLD, command=lambda: self.dating_b())
        dating_b.place(x=470 / 2 - 140 / 2, y=390, width=140, height=70)

    def work_b(self):
        username = ChatDirectory.client_chat.select_room_func("work")
        self.close()
        app_login = candidate_gui.ChatApplication(username, "work")
        app_login.run()


    def talking_b(self):
        username = ChatDirectory.client_chat.select_room_func("talking")
        self.close()
        app_login = candidate_gui.ChatApplication(username, "talking")
        app_login.run()


    def dating_b(self):
        username = ChatDirectory.client_chat.select_room_func("dating")
        self.close()
        app_login = candidate_gui.ChatApplication(username, "dating")
        app_login.run()



'''if __name__ == "__main__":
    app = chat_application_select_room_page()
    app.run()'''
