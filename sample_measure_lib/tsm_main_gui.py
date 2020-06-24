
import tkinter as tk
from tkinter import filedialog, Menu, Text, Frame, Button, Label, Entry, ttk
from tkinter import END, DISABLED, NORMAL, E, W, NE, LEFT
from PIL import ImageTk, Image
import sys
import os
import queue
import threading
import multiprocessing
import traceback
from datetime import datetime

from sample_measure_lib.draws_io import ImageHandler, build_output_file
from sample_measure_lib.formats import validate_start_id

IMG_BASE_SIZE_X = 1024
IMG_BASE_SIZE_Y = 800


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area


class StdoutRedirector(IORedirector):
    
    def write(self, str):
        if str.strip():
            str = "{} {}".format(datetime.now().strftime("%H:%M:%S"), str)
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
        #self.queue = multiprocessing.Queue()

        self.textWidget = textWidget ##root.nametowidget('frame-output.text-output')
        self.root.after(500, self.process_queue)

    def insert(self, pos, txt):
        self.queue.put(('output', txt))

    def emit_done(self):
        self.queue.put(('done', None))

    def emit_image(self, base_path, name):
        self.queue.put(('image', (base_path, name)))

    def emit_csv(self, path):
        self.queue.put(('csv', path))

    def process_queue(self):
        try:
            for _ in range(100):
                event, msg = self.queue.get(0)
                
                if event == 'output':
                    self.action_print(msg)

                elif event == 'done':
                    enable_buttons(self.root, True)

                elif event == 'image':
                    self.action_image(*msg)

                elif event == 'csv':
                    self.action_csv(msg)

        except queue.Empty:
            pass

        except Exception:
            self.action_print(traceback.format_exc())
            raise
        
        self.root.after(500, self.process_queue)

    def action_print(self, msg):
        self.textWidget.insert(END, msg)

    def action_image(self, base_path, name):
        img_path = build_output_file(base_path, name, 'png')
        tabs = self.root.nametowidget('tabs')
        tabImage = Frame(tabs)

        pathLabel = Label(tabImage, text=img_path)
        pathLabel.pack()

        img = Image.open(img_path)

        if img.height > img.width*1.2:
            img = img.resize((int(IMG_BASE_SIZE_Y*img.width/img.height), IMG_BASE_SIZE_Y))
        else:
            img = img.resize((IMG_BASE_SIZE_X, int(IMG_BASE_SIZE_X*img.height/img.width)))
        ph = ImageTk.PhotoImage(img)
        imgLabel = Label(tabImage, image=ph)
        imgLabel.img = ph
        imgLabel.pack(side = "top", fill = "both", expand = "no")
        tabs.add(tabImage, text=name)

    def action_csv(self, csv_path):

        tabs = self.root.nametowidget('tabs')
        tabCsv = Frame(tabs)

        pathLabel = Label(tabCsv, text=csv_path)
        pathLabel.pack()

        csv_data = open(csv_path, 'r').read()
        csvText = tk.Text(tabCsv, height=20, width=120)
        csvText.insert(END, csv_data)
        csvText.pack()
        
        tabs.add(tabCsv, text='csv')


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
        Button(text="Open 3mf File", name='button-open', command=self.handle_open).grid(row=0, column=1, pady=(10, 2), padx=10, sticky=W)

        Label(text="", name='label-filename').grid(row=1, column=1, columnspan=4, pady=(2, 10), padx=10, sticky=W)

        Label(text="ID").grid(row=2, column=0, pady=10, padx=10, sticky=E)

        idFrame = Frame(self.root, name='frame-id')
        idFrame.grid(row=2, column=1, columnspan=4, pady=10, padx=10, sticky=W)
        Entry(idFrame, width=5, name='entry-id').pack(side=LEFT)
        
        for _id in ('A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'):
            self.__add_id_button(idFrame, _id)
            
        Button(text="Run Measures", name='button-run', command=self.handle_run).grid(row=3, column=1, pady=10, padx=10, sticky=W)


        tabs = ttk.Notebook(self.root, name='tabs')
        tabs.grid(row=4, column=0, columnspan=5)

        tab1 = Frame(tabs, name='tab-output')
        tabs.add(tab1, text='Output')
        
        #Label(text="Output").grid(row=4, column=0, pady=10, padx=10, sticky=NE)
        #textFrame = Frame(self.root, name='frame-output')
        #textFrame.grid(row=4, column=1, columnspan=4, pady=10, padx=10)
        self.configure_textarea(tab1)

        self.update_states()

    def __add_id_button(self,idFrame, _id):
        Button(idFrame, text=_id, command=lambda: self.handle_id_button(_id)).pack(side=LEFT, padx=2)

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
        #T.bind("<Key>", lambda e: "break")
        return T
        
    def handle_open(self):
        self.filename = filedialog.askopenfilename(
            initialdir = "/",
            title = "Select 3mf file", 
            filetypes = (("3mf files","*.3mf"), ("all files","*.*")))
        
        self.update_states()
        self.handle_id_button('')
        get_output_widget(self.root).delete(1.0, END)
        self.reset_tabs()
        #print("Press 'Run Measures'" % (self.filename))

    def handle_run(self):        
        if not self.filename:
            print("No file is opened")
            return

        self.start_id = self.root.nametowidget('frame-id.entry-id').get().strip()
        if not self.start_id:
            print("No ID is defined")
            return
   
        validate_start_id(self.start_id)

        enable_buttons(self.root, False)
        self.reset_tabs()

        # self.thread = multiprocessing.Process(None, MainWindow.run_worker, args=(self.taskQueue, self.filename, self.start_id))
        # self.thread.start()

        self.thread = threading.Thread(target=self.run_worker, args=(self.taskQueue, self.filename, self.start_id))
        self.thread.start()

    @staticmethod
    def run_worker(taskQueue, filename, start_id):
        from sample_measure_lib.tsm_main_v3 import measure_file_with_images
        import matplotlib
        import matplotlib.pyplot as plt

        try:
            measure_file_with_images(filename, img_handler=TabImageHandler(taskQueue, plt, filename), start_id=start_id)
        except Exception:
            print(traceback.format_exc())
            raise
        finally:
            taskQueue.emit_done()

    def update_states(self):
        labelFile = self.root.nametowidget('label-filename')
        buttonRun = self.root.nametowidget('button-run')
        if self.filename:
            labelFile.configure(text=self.filename)
            buttonRun.configure(state=NORMAL)
        else:
            labelFile.configure(text="<no file opened>")
            buttonRun.configure(state=DISABLED)

    def reset_tabs(self):
        tabs = self.root.nametowidget('tabs')

        for t in tabs.winfo_children():
            if not str(t).endswith("tab-output"):
                t.destroy()

def enable_buttons(root, enabled):
    state = NORMAL if enabled else DISABLED
    root.nametowidget('button-open').configure(state=state)
    root.nametowidget('button-run').configure(state=state)


def get_output_widget(root):
    return root.nametowidget('tabs.tab-output.text-output')


def main():
    root = tk.Tk()
    root.title("3MF Samples Measure")
    root.resizable(False, False)

    win = MainWindow(root)
    r = redirector(win.taskQueue)

    root.mainloop()


class TabImageHandler(ImageHandler):

    def __init__(self, taskQueue, plt, base_path):
        super(TabImageHandler, self).__init__(plt, base_path)
        self.taskQueue = taskQueue

    def save_image(self, name):
        super(TabImageHandler, self).save_image(name)
        self.taskQueue.emit_image(self.base_path, name)

    def show_csv(self, path):
        super(TabImageHandler, self).show_csv(path)
        self.taskQueue.emit_csv(path)
