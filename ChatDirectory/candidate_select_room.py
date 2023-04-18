from tkinter import *
import candidate_gui
#import client_chat


BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class chat_application_select_room_page:

    def __init__(self,):
        self.rooms_of_employes = [] # list that will contain tuples of the username of employer and the company name for every employer that is connected
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def close(self):
        self.window.destroy()

    def _setup_main_window(self):
        self.window.title("We Hire - Select room page for candidates")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text='select a room with the employer you want to be with:', font="Helvetica 30 bold", pady=10)

        head_label.place(x=110, y=50)

        #work_b = Button(self.window, text='work', font=FONT_BOLD, command=lambda: self.work_b())
        #work_b.place(x=470/2-140/2, y=150, width=140, height=70)
        #talking_b = Button(self.window, text='talking', font=FONT_BOLD, command=lambda: self.talking_b())
        #talking_b.place(x=470 / 2 - 140 / 2, y=270, width=140, height=70)
        #dating_b = Button(self.window, text='dating', font=FONT_BOLD, command=lambda: self.dating_b())
        #dating_b.place(x=470 / 2 - 140 / 2, y=390, width=140, height=70)

    def create_list(self):
        x_label = 170
        y_label = 200
        x_button = 300
        y_button = y_label
        for room in self.rooms_of_employes:
            current_room_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                                       text=str(room[0]) + " : " + str(room[1]), font="Helvetica 10 bold", pady=10)
            current_room_label.place(x=x_label, y=y_label)
            current_room_button = Button(self.window, text='join this room', font=FONT_BOLD,command=lambda: self.request_to_join_room(str(room[0])))
            current_room_button.place(x=x_button, y=y_button, width=140, height=70)
            y_label += 120
            y_button = y_label


    def request_to_join_room(self, username):
        pass

    def work_b(self):
        #username = client_chat.select_room_func('work')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'work')
        app_login.run()


    def talking_b(self):
        #username = client_chat.select_room_func('talking')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'talking')
        app_login.run()


    def dating_b(self):
        #username = client_chat.select_room_func('dating')
        username = "krasner"
        self.close()
        app_login = client_gui.ChatApplication(username, 'dating')
        app_login.run()



if __name__ == "__main__":
    app = chat_application_select_room_page()
    app.run()
