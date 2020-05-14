
import tkinter as tk
from tkinter import filedialog, Menu, Text, END
import sys

class IORedirector(object):
    '''A general class for redirecting I/O to this Text widget.'''
    def __init__(self,text_area):
        self.text_area = text_area

class StdoutRedirector(IORedirector):
    '''A class for redirecting stdout to this Text widget.'''
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
    # root = Toplevel()
    #T = Text(root)
    sys.stdout = StdoutRedirector(T)
    sys.stderr = StdoutRedirector(T)
    #T.pack()
    text.insert(END, inputStr)

# quote = """HAMLET: To be, or not to be--that is the question:
# Whether 'tis nobler in the mind to suffer
# The slings and arrows of outrageous fortune
# Or to take arms against a sea of troubles
# And by opposing end them. To die, to sleep--
# No more--and by a sleep to say we end
# The heartache, and the thousand natural shocks
# That flesh is heir to. 'Tis a consummation
# Devoutly to be wished."""
# T.insert(tk.END, quote)


def handle_open():
    from tsm import measure_file_with_images

    root.filename =  filedialog.askopenfilename(
        initialdir = "/",
        title = "Select 3mf file", 
        filetypes = (("3mf files","*.3mf"), ("all files","*.*")))

    measure_file_with_images(root.filename)

    #labelDone = tk.Label(root, text= 'Completed')
    #appCanvas.create_window(150, 200, window=labelDone)


root = tk.Tk()
root.title("3MF Sampls Measure")

configure_menu(root)
T = configure_textarea(root)

r = redirector(root, T)

print("Python Location: {}".format(sys.executable))
print("Python Version: {}".format(sys.version))
root.mainloop()
