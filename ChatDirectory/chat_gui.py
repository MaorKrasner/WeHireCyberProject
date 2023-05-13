from tkinter import *
from tkinter import filedialog

import ChatDirectory.client_chat
from ChatDirectory import chat_info_gui
from ChatDirectory.client_chat import *

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"


class ChatApplication:

    def __init__(self, user):
        self.window = Tk()
        self.user = user
        self._setup_main_window()
        self.start_receive_thread()


    def run(self):
        self.window.mainloop()


    def close(self):
        self.window.destroy()

    def start_receive_thread(self):
        ChatDirectory.client_chat.start_receive(self.text_widget)


    def _setup_main_window(self):
        self.window.title("We Hire - Chat")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=720, height=550, bg=BG_COLOR)

        # head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text=f'Welcome {self.user}', font=FONT_BOLD, pady=10)

        head_label.place(width=465, height=50)

        # tiny divider
        line1 = Label(self.window, width=450, bg=BG_GRAY)
        line1.place(relwidth=1, rely=0.07, relheight=0.012)
        line2 = Label(self.window, width=450, bg=BG_GRAY)
        line2.place(relwidth=4, rely=0.139, relheight=0.012)

        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.68, relwidth=1, rely=0.15)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, 'send !INFO to see info, send !SIGN to create and sign a diploma')
        self.text_widget.insert(END, '\n')
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)

        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self.on_enter_pressed)

        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self.on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.04, relwidth=0.22)

        # files button
        button_explore = Button(bottom_label, width=20, bg=BG_GRAY,
                                text="Browse Files",
                                command=self.browseFiles)
        button_explore.place(relx=0.77, rely=0.047, relheight=0.025, relwidth=0.22)

    def on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self.msg_entry.delete(0, END)
        self.insert_message(msg)

    def insert_message(self, msg):
        if not msg or [x for x in msg] == [' ' for x in range(len(msg))]:
            return
        else:
            if msg != 'FILE' and msg != 'HACK':
                if msg != '!INFO':
                    self.text_widget.configure(state=NORMAL)
                    self.text_widget.insert(END, msg)
                    self.text_widget.insert(END, '\n')
                    self.text_widget.configure(state=DISABLED)
                    self.text_widget.see(END)
                else:
                    app = chat_info_gui.chat_application_info_page()
                    app.run()
            res = ChatDirectory.client_chat.session_func(msg, self.text_widget)
            if res == 'exit':
                self.close()
                exit()
            elif res == 'File not accessible':
                self.text_widget.configure(state=NORMAL)
                self.text_widget.insert(END, res)
                self.text_widget.insert(END, '\n')
                self.text_widget.configure(state=DISABLED)
                self.text_widget.see(END)
            elif res == 'sent':
                self.text_widget.configure(state=NORMAL)
                self.text_widget.insert(END, res)
                self.text_widget.insert(END, '\n')
                self.text_widget.configure(state=DISABLED)
                self.text_widget.see(END)
            else:
                return


    def browseFiles(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                          "*.txt*"),
                                                         ("all files",
                                                          "*.*")))
        self.insert_message('FILE')
        self.insert_message(filename)

if __name__ == "__main__":
    app = ChatApplication('maorkr')
    app.run()