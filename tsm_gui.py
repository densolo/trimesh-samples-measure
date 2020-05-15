
import tkinter as tk
from tkinter import filedialog, Menu, Text, END
import sys


class IORedirector(object):
    def __init__(self,text_area):
        self.text_area = text_area


class StdoutRedirector(IORedirector):
    
    def write(self,str):
        self.text_area.insert(END, str)

    def flush(self):
        pass


def configure_menu(root):
    menubar = Menu(root)

    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label='Open 3MF ...', command=handle_open)
    filemenu.add_command(label='Exit', command=root.quit)

    menubar.add_cascade(label="File", menu=filemenu)

    root.config(menu=menubar) 


def configure_textarea(root):
    S = tk.Scrollbar(root)
    T = tk.Text(root, height=40, width=120)
    S.pack(side=tk.RIGHT, fill=tk.Y)
    T.pack(side=tk.LEFT, fill=tk.Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)
    return T


def redirector(root, text, inputStr=""):
    import sys
    sys.stdout = StdoutRedirector(T)
    sys.stderr = StdoutRedirector(T)
    text.insert(END, inputStr)


def handle_open():
    from tsm import measure_file_with_images

    root.filename =  filedialog.askopenfilename(
        initialdir = "/",
        title = "Select 3mf file", 
        filetypes = (("3mf files","*.3mf"), ("all files","*.*")))

    measure_file_with_images(root.filename)


root = tk.Tk()
root.title("3MF Samples Measure")

configure_menu(root)
T = configure_textarea(root)
r = redirector(root, T)

root.mainloop()
