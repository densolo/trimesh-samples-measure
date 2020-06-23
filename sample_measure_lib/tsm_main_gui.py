
import tkinter as tk
from tkinter import filedialog, Menu, Text, Frame, Button, Label, Entry
from tkinter import END, DISABLED, NORMAL, E, W, NE, LEFT
import sys
import queue
import threading


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area


class StdoutRedirector(IORedirector):
    
    def write(self, str):
        self.text_area.insert(END, str)

    def flush(self):
        pass


def redirector(text, inputStr=""):
    sys.stdout = StdoutRedirector(text)
    sys.stderr = StdoutRedirector(text)
    text.insert(END, inputStr)


class TextQueue():

    def __init__(self, root, textWidget):
        self.root = root
        self.queue = queue.Queue()
        self.textWidget = textWidget ##root.nametowidget('frame-output.text-output')
        self.root.after(500, self.process_queue)

    def insert(self, pos, txt):
        self.queue.put(txt)

    def process_queue(self):
        try:
            for _ in range(100):
                msg = self.queue.get(0)
                self.textWidget.insert(END, msg)
        except queue.Empty:
            pass
        
        self.root.after(500, self.process_queue)


class MainWindow():

    def __init__(self, root):
        self.root = root
        self.filename = ''
        self.configure()
        self.thread = None

    def configure(self):

        Button(text="Open 3mf File", command=self.handle_open).grid(row=0, column=1, pady=10, padx=10, sticky=W)

        Label(text="File").grid(row=1, column=0, pady=10, padx=10, sticky=E)
        Label(text="", name='label-filename').grid(row=1, column=1, columnspan=4, pady=10, padx=10, sticky=W)

        Label(text="ID").grid(row=2, column=0, pady=10, padx=10, sticky=E)

        idFrame = Frame(self.root, name='frame-id')
        idFrame.grid(row=2, column=1, columnspan=4, pady=10, padx=10, sticky=W)
        Entry(idFrame, width=5, name='entry-id').pack(side=LEFT)
        
        for _id in ('A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'):
            self.__add_id_button(idFrame, _id)
            
        Button(text="Run Measures", command=self.handle_run).grid(row=3, column=1, pady=10, padx=10, sticky=W)

        Label(text="Output").grid(row=4, column=0, pady=10, padx=10, sticky=NE)
        textFrame = Frame(self.root, name='frame-output')
        textFrame.grid(row=4, column=1, columnspan=4, pady=10, padx=10)
        self.configure_textarea(textFrame)


    def __add_id_button(self,idFrame, _id):
        Button(idFrame, text=_id, command=lambda: self.handle_id_button(_id)).pack(side=LEFT)

    def handle_id_button(self, _id):
        idEntry = self.root.nametowidget('frame-id.entry-id')
        idEntry.delete(0, END)
        idEntry.insert(0, _id)

    def configure_textarea(self, root):
        S = tk.Scrollbar(root)
        T = tk.Text(root, name='text-output', height=40, width=120)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        T.pack(side=tk.LEFT, fill=tk.Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        T.bind("<Key>", lambda e: "break")
        return T
        
    def handle_open(self):
        self.filename = filedialog.askopenfilename(
            initialdir = "/",
            title = "Select 3mf file", 
            filetypes = (("3mf files","*.3mf"), ("all files","*.*")))
        
        labelFile = self.root.nametowidget('label-filename')
        labelFile.configure(text=self.filename)

        print("Opened file: %s" % (self.filename))

    def handle_run(self):
        from sample_measure_lib.tsm_main import measure_file_with_images

        if self.filename:
            self.thread = threading.Thread(target=measure_file_with_images, args=[self.filename])
            self.thread.start()


def main():
    root = tk.Tk()
    root.title("3MF Samples Measure")

    win = MainWindow(root)
    text = TextQueue(root, root.nametowidget('frame-output.text-output'))
    r = redirector(text)

    root.mainloop()
