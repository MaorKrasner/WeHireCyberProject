from tkinter import *
#from client_chat import *
from ChatDirectory.client_chat import *
from ChatDirectory.employer_create_account_page_gui import chat_application_create_account_employer_page
from client_login_page_gui import *
from candidate_create_account_page_gui import *
from chat_gui import *

from ChatDirectory import client_login_page_gui

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class chat_application_start_page:

    def __init__(self, ):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("We Hire - start page")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=720, height=550, bg=BG_COLOR) # 470 550

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text='Welcome!', font="Helvetica 30 bold", pady=10)

        head_label.place(x=275, y=50)

        login_b = Button(self.window, text='Login', font=FONT_BOLD, command=lambda: self.login_b())
        login_b.place(x=580 / 2 - 140 / 2, y=180, width=300, height=70) # 140, 720
        create_account_b_candidate = Button(self.window, text='Create account for candidate', font=FONT_BOLD, command=lambda: self.create_candidate_b())
        create_account_b_candidate.place(x=580 / 2 - 140 / 2, y=300, width=300, height=70)  # 720 / 2 - 140 / 2, 140 70
        create_account_b_employer = Button(self.window, text='Create account for employer', font=FONT_BOLD, command=lambda: self.create_employer_b())
        create_account_b_employer.place(x=580 / 2 - 140 / 2, y=420, width=300, height=70)  # 720 / 2 - 140 / 2, 140 70

    def login_b(self):
        pass
        start_func('1')
        self.close()
        app_login = client_login_page_gui.chat_application_login_page()
        app_login.run()

    def create_candidate_b(self):
        pass
        start_func('2')
        self.close()
        app_create_account = chat_application_create_account_candidate_page()
        app_create_account.run()

    def create_employer_b(self):
        pass
        start_func('2')
        self.close()
        app_create_account = chat_application_create_account_employer_page()
        app_create_account.run()


if __name__ == "__main__":
    app = chat_application_start_page()
    app.run()