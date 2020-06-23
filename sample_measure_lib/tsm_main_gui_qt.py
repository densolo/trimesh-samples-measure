
import os
import sys
import time
import threading
import traceback

# import tkinter as tk
# import tkinter.ttk as ttk
# from tkinter import filedialog, Menu, Text, END
# from tkinter import Tk, Text, TOP, BOTH, X, N, LEFT, RIGHT
# from tkinter import Frame, Label, Entry
# import pygubu

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QFileDialog
from PyQt5.QtCore import QSize, pyqtSignal, QObject
from PyQt5.QtWidgets import QPushButton, QAction
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QFile, QUrl
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
# from PySide2.QtUiTools import QUiLoader


from PyQt5 import QtCore, QtGui, QtWidgets, QtWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings


DEBUG_PORT = '5577'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
IS_DEBUG = '-debug' in sys.argv


class IORedirector(QObject):

    stdout_queue = pyqtSignal(str)

    def __init__(self, text_area):
        super(IORedirector, self).__init__()
        self.text_area = text_area
        self.stdout_queue.connect(self.handle_queue)

    def handle_queue(self, txt):
        pass


class QtStdoutRedirector(IORedirector):
    
    def write(self, txt):
        self.stdout_queue.emit(txt)
        #self.text_area.insertPlainText(txt)

    def handle_queue(self, txt):
         self.text_area.insertPlainText(txt)

    def flush(self):
        pass


# class StdoutRedirector(IORedirector):
    
#     def write(self,str):
#         self.text_area.insert(END, str)
#
#     def flush(self):
#         pass


# def configure_menu(root):
#     menubar = Menu(root)

#     filemenu = Menu(menubar, tearoff=0)
#     filemenu.add_command(label='Open 3MF ...', command=lambda: handle_open(root))
#     filemenu.add_command(label='Exit', command=root.quit)

#     menubar.add_cascade(label="File", menu=filemenu)

#     root.config(menu=menubar) 


# def configure_textarea(root):
#     S = tk.Scrollbar(root)
#     T = tk.Text(root, height=40, width=120)
#     S.pack(side=tk.RIGHT, fill=tk.Y)
#     T.pack(side=tk.LEFT, fill=tk.Y)
#     S.config(command=T.yview)
#     T.config(yscrollcommand=S.set)
#     return T


# def redirector(root, text, inputStr=""):
#     import sys
#     sys.stdout = StdoutRedirector(text)
#     sys.stderr = StdoutRedirector(text)
#     text.insert(END, inputStr)


# def handle_open(root):
#     from sample_measure_lib.tsm_main import measure_file_with_images
#     from sample_measure_lib.draws_io import ImageHandler

#     root.filename =  filedialog.askopenfilename(
#         initialdir = "/",
#         title = "Select 3mf file", 
#         filetypes = (("3mf files","*.3mf"), ("all files","*.*")))

#     measure_file_with_images(root.filename)


def qt_handle_open(window):
    from sample_measure_lib.tsm_main import measure_file_with_images

    home = os.path.expanduser("~/")
    filename = QFileDialog.getOpenFileName(window, 'Open file', home, "3mf files (*.3mf)")[0]
    if filename:
        print("Opening file %s" % (filename,))
        enable_handler = WidgetEnableHandler(window.findChild(QAction, "actionOpen_File"))
        enable_handler.setEnabled(False)
        t = threading.Thread(target=handle_open_file, args=[enable_handler, filename])
        t.start()


def handle_open_file(enable_handler, filename):
    try:
        from sample_measure_lib.tsm_main import measure_file_with_images
        # b = window.findChild(QPushButton, "buttonOpenFile")
        # enable_handler.setEnabled(False)
        try:
            measure_file_with_images(filename)        
        finally:
            enable_handler.setEnabled(True)
    except Exception:
        print(traceback.format_exc())


class WidgetEnableHandler(QObject):

    enable = pyqtSignal(bool)

    def __init__(self, widget):
        super(WidgetEnableHandler, self).__init__()
        self.widget = widget
        self.enable.connect(self.handle_enable)

    def setEnabled(self, enable):
        self.enable.emit(enable)

    def handle_enable(self, enable):
        self.widget.setEnabled(enable)



class AppForm(QMainWindow):
    def __init__(self):
        super(AppForm, self).__init__()
        self.load_ui()

    def load_ui(self):
        # loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "resources", "qt-form", "form.ui")
        #ui_file = QFile(path)
        #ui_file.open(QFile.ReadOnly)
        uic.loadUi(path, self)
        #ui_file.close()

        textArea = self.findChild(QPlainTextEdit, "textArea")
        assert textArea
        sys.stdout = QtStdoutRedirector(textArea)
        sys.stderr = QtStdoutRedirector(textArea)

        actionOpen_File = self.findChild(QAction, "actionOpen_File")
        actionOpen_File.triggered.connect(lambda:qt_handle_open(self))


class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        self.view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        self.view.loadFinished.connect(self.handleLoaded)

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "ui", "index.html").replace("\\", "/")
        self.view.load(QUrl.fromLocalFile(path))

        self.channel = QWebChannel()
        self.channel.registerObject('backend', self)
        self.view.page().setWebChannel(self.channel)

        self.inspector = QWebEngineView()
        self.inspector.setWindowTitle('Web Inspector')
        self.inspector.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.inspector.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

    def handleLoaded(self, ok):
        if ok and IS_DEBUG:
            self.inspector.load(QtCore.QUrl(DEBUG_URL))
            self.inspector.show()

    @QtCore.pyqtSlot(str, result=str)
    def backendEvent(self, jsonData):
        print("backendEvent: %s" % (jsonData,))
        self.view.page().runJavaScript("console.log('hi');")
        return "return"


def main():
    if IS_DEBUG:
        os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT
    
    app = QtWidgets.QApplication(sys.argv)
    win = AppWindow()
    win.resize(800, 600)
    win.show()
    app.exec_()


def main2():
    app = QApplication([])
    #widget = AppForm()
    #widget.show()

    browser = QWebEngineView()

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "ui", "index.html").replace("\\", "/")
    print("path: %s" % path)

    browser.load(QUrl.fromLocalFile(path))
    browser.show()
    #browser.load(QUrl(url))

    sys.exit(app.exec_())


def main3():

    wx = 800
    wy = 600

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setMinimumSize(QSize(wx, wy))    


    b2 = QPushButton("Open File", window, objectName='buttonOpenFile')
    b2.clicked.connect(lambda:qt_handle_open(window))

    textArea = QPlainTextEdit(window)
    
    textArea.setReadOnly(True)
    textArea.setFont(QFont('Courier'))
    textArea.move(10,30)
    textArea.resize(wx-2*10, wy-2*10 - 30)

    sys.stdout = QtStdoutRedirector(textArea)
    sys.stderr = QtStdoutRedirector(textArea)

    window.show()

    app.exec_()


# def main2():

#     ui_spec = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'form.ui')
#     assert os.path.exists(ui_spec), ui_spec
#     builder = builder = pygubu.Builder()
#     builder.add_from_file(ui_spec)


#     mainwindow = builder.get_object('frame_1')
#     mainwindow.mainloop()
    

# def main2():
#     root = tk.Tk()
#     root.title("3MF Samples Measure")
#     root.geometry("300x300+300+300")

#     configure_menu(root)

#     app = MainForm(root)

#     # sidebar = tk.Frame(root, width=200, height=500)
#     # sidebar.pack(expand=False, fill=BOTH, side=LEFT, anchor='nw')

#     # mainarea = tk.Frame(root, bg='#CCC', width=500, height=500)
#     # mainarea.pack(expand=True, fill=BOTH, side=RIGHT)

#     T = configure_textarea(mainarea)
#     redirector(root, T)

#     print("Started")

#     root.mainloop()


if __name__ == '__main__':
    main()

