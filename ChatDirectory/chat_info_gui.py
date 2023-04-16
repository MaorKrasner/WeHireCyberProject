from tkinter import *
#import client_chat
#import client_login_gui
#from client_gui import *

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class chat_application_info_page:

    def __init__(self, ):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("We Hire - INFO page")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        user_name = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                          text='INFO:', font="Helvetica 20 bold", ).place(x=185, y=10)
        line1 = Label(self.window, bg=BG_GRAY).place(x=184, y=45, width=80, height=4)

        online1 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                        text='!online:', font="Helvetica 15 bold").place(x=10,
                                                                         y=55)
        online2 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                        text='Displays all users connected to the system.', font="Helvetica 15").place(x=85,
                                                                                                       y=55)

        room_online1 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                             text='!room online:', font="Helvetica 15 bold").place(
            x=10, y=85)
        room_online2 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                             text='Displays all users connected to your', font="Helvetica 15").place(
            x=140, y=85)
        room_online3 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                             text='room.', font="Helvetica 15").place(
            x=140, y=115)

        profile1 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                        text='!profile:',
                        font="Helvetica 15 bold").place(x=10, y=145)
        profile2 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='And then to who(username), displays the',
                         font="Helvetica 15").place(x=90, y=145)
        profile3 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='data of this user.',
                         font="Helvetica 15").place(x=90, y=175)

        private1 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='!private:', font="Helvetica 15 bold").place(x=10, y=205)
        private2 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='And then to who(username), will start a', font="Helvetica 15").place(x=95, y=205)
        private3 = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                         text='private session with this user.',
                         font="Helvetica 15").place(x=95, y=235)

        login_b = Button(self.window, text='Close', font="Helvetica 35 bold", command=lambda: self.close())
        login_b.place(x=150, y=400, width=200, height=70)


if __name__ == "__main__":
    app = chat_application_info_page()
    app.run()
