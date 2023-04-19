from tkinter import *
import candidate_gui
# import client_chat
from chat_database_management import *

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class chat_application_select_room_page:

    def __init__(self, ):
        self.rooms_of_employes = []  # list that will contain tuples of the username of employer and the company name for every employer that is connected
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("We Hire - Select room page for candidates")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=1000, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text='select a room to join:', font="Helvetica 30 bold", pady=10)

        head_label.place(x=300, y=20)

        self.show_all_employers()

        '''
        work_b = Button(self.window, text='work', font=FONT_BOLD, command=lambda: self.work_b())
        work_b.place(x=470/2-140/2, y=150, width=140, height=70)
        talking_b = Button(self.window, text='talking', font=FONT_BOLD, command=lambda: self.talking_b())
        talking_b.place(x=470 / 2 - 140 / 2, y=270, width=140, height=70)
        dating_b = Button(self.window, text='dating', font=FONT_BOLD, command=lambda: self.dating_b())
        dating_b.place(x=470 / 2 - 140 / 2, y=390, width=140, height=70)
        '''

    def show_all_employers(self):
        x_label = 170
        y_label = 100
        x_button = 700
        y_button = y_label
        employers_list = show_only_employers_from_client_user()
        for employer in employers_list:
            employer_user_name = str(employer[0])
            employer_full_name = ''.join(employer[1] + " " + employer[2])
            company_that_employer_works_in = str(employer[3])
            current_room_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                                       text=employer_user_name + " : " + employer_full_name + ", works in : " + company_that_employer_works_in, font="Helvetica 20 bold", pady=10)
            current_room_label.place(x=x_label, y=y_label)
            current_room_button = Button(self.window, text='request to join', font=FONT_BOLD)
                                         #,command=lambda: self.request_to_join_room(str(room[0])))
            current_room_button.place(x=x_button, y=y_button, width=110, height=40)
            y_label += 80
            y_button = y_label

    def request_to_join_room(self, username):
        pass

    '''
    def work_b(self):
        # username = client_chat.select_room_func('work')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'work')
        app_login.run()

    def talking_b(self):
        # username = client_chat.select_room_func('talking')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'talking')
        app_login.run()

    def dating_b(self):
        # username = client_chat.select_room_func('dating')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'dating')
        app_login.run()
    '''

if __name__ == "__main__":
    app = chat_application_select_room_page()
    app.run()
