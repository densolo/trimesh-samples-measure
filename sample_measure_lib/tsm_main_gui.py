
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


class TaskQueue():

    def __init__(self, root, textWidget):
        self.root = root
        self.queue = queue.Queue()
        self.textWidget = textWidget ##root.nametowidget('frame-output.text-output')
        self.root.after(500, self.process_queue)

    def insert(self, pos, txt):
        self.queue.put(('output', txt))

    def emit_done(self):
        self.queue.put(('done', None))

    def process_queue(self):
        try:
            for _ in range(100):
                event, msg = self.queue.get(0)
                
                if event == 'output':
                    self.textWidget.insert(END, msg)

                elif event == 'done':
                    enable_buttons(self.root, True)

        except queue.Empty:
            pass
        
        self.root.after(500, self.process_queue)


class MainWindow():

    def __init__(self, root):
        self.root = root
        self.filename = ''
        self.start_id = ''
        self.thread = None

        self.configure()

        self.taskQueue = TaskQueue(root, get_output_widget(root))

    def configure(self):

        Label(text="File").grid(row=0, column=0, pady=10, padx=10, sticky=E)
        Button(text="Open 3mf File", name='button-open', command=self.handle_open).grid(row=0, column=1, pady=10, padx=10, sticky=W)

        Label(text="", name='label-filename').grid(row=1, column=1, columnspan=4, pady=10, padx=10, sticky=W)

        Label(text="ID").grid(row=2, column=0, pady=10, padx=10, sticky=E)

        idFrame = Frame(self.root, name='frame-id')
        idFrame.grid(row=2, column=1, columnspan=4, pady=10, padx=10, sticky=W)
        Entry(idFrame, width=5, name='entry-id').pack(side=LEFT)
        
        for _id in ('A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'):
            self.__add_id_button(idFrame, _id)
            
        Button(text="Run Measures", name='button-run', command=self.handle_run).grid(row=3, column=1, pady=10, padx=10, sticky=W)

        Label(text="Output").grid(row=4, column=0, pady=10, padx=10, sticky=NE)
        textFrame = Frame(self.root, name='frame-output')
        textFrame.grid(row=4, column=1, columnspan=4, pady=10, padx=10)
        self.configure_textarea(textFrame)

        self.update_states()

    def __add_id_button(self,idFrame, _id):
        Button(idFrame, text=_id, command=lambda: self.handle_id_button(_id)).pack(side=LEFT)

    def handle_id_button(self, _id):
        idEntry = self.root.nametowidget('frame-id.entry-id')
        idEntry.delete(0, END)
        idEntry.insert(0, _id)

    def configure_textarea(self, root):
        S = tk.Scrollbar(root)
        T = tk.Text(root, name='text-output', height=20, width=120)
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
        
        self.update_states()
        self.handle_id_button('')
        get_output_widget(self.root).delete(1.0, END)
        #print("Press 'Run Measures'" % (self.filename))

    def handle_run(self):        
        if not self.filename:
            return

        self.start_id = self.root.nametowidget('frame-id.entry-id').get().strip()
        enable_buttons(self.root, False)

        self.thread = threading.Thread(target=self.run_worker)
        self.thread.start()

    def run_worker(self):
        from sample_measure_lib.tsm_main_v3 import measure_file_with_images
        try:
            measure_file_with_images(self.filename, start_id=self.start_id)
        finally:
            self.taskQueue.emit_done()

    def update_states(self):
        labelFile = self.root.nametowidget('label-filename')
        buttonRun = self.root.nametowidget('button-run')
        if self.filename:
            labelFile.configure(text=self.filename)
            buttonRun.configure(state=NORMAL)
        else:
            labelFile.configure(text="<no file opened>")
            buttonRun.configure(state=DISABLED)


def enable_buttons(root, enabled):
    state = NORMAL if enabled else DISABLED
    root.nametowidget('button-open').configure(state=state)
    root.nametowidget('button-run').configure(state=state)


def get_output_widget(root):
    return root.nametowidget('frame-output.text-output')


def main():
    root = tk.Tk()
    root.title("3MF Samples Measure")

    win = MainWindow(root)
    r = redirector(win.taskQueue)

    root.mainloop()
