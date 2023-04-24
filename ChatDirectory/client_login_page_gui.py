from tkinter import *
from ChatDirectory.client_chat import *
#import client_chat
#from client_gui import *
#from client_create_account_gui import *
#from client_select_room_gui import *

# from chat import get_response, bot_name
#from ChatDirectory.candidate_select_room import chat_application_select_room_page
import select_room_gui
from ChatDirectory import client_chat

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class chat_application_login_page:

    def __init__(self, ):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("We Hire - login page")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        user_name = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                          text='Enter your user name and password:', font="Helvetica 20", )
        user_name.place(x=10, y=50)
        line1 = Label(self.window, bg=BG_GRAY)
        line1.place(x=15, y=85, width=435, height=4)

        user_name = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                          text='User name:', font="Helvetica 15")
        user_name.place(x=10, y=130)
        self.e_user_name = Entry(self.window, width=40)
        self.e_user_name.place(x=150, y=136)

        password = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='Password:', font="Helvetica 15")
        password.place(x=10, y=200)
        self.e_password = Entry(self.window, width=40, show='*')
        self.e_password.place(x=150, y=206)

        login_b = Button(self.window, text='Submit', font="Helvetica 35 bold", command=lambda: self.login())
        login_b.place(x=150, y=300, width=200, height=70)

    def login(self):
        success = client_chat.login_func(self.e_user_name.get(), self.e_password.get())
        if success:
            self.close()
            app_choose_room = select_room_gui.chat_application_select_room_page()
            app_choose_room.run()
        else:
            self.e_user_name.delete(0, END)
            self.e_password.delete(0, END)



if __name__ == "__main__":
    app = chat_application_login_page()
    app.run()
