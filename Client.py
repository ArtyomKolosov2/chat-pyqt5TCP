import socket
from PyQt5.QtWidgets import (QApplication, QWidget, QPlainTextEdit,
                             QPushButton, QHBoxLayout, QVBoxLayout,
                             QLabel, QLineEdit, QMainWindow)
from PyQt5.QtCore import (QThread, pyqtSlot, pyqtSignal, QTime, QSize, Qt)
from PyQt5.QtGui import (QIcon, QFont, QPixmap)
import os


class UserInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.__is_connected = False
        self.initialize_component()
        self.MyServer = MyServer(self.add_message,
                                 self.change_connect_status)
        self.MyServer.signal_connected.connect(self.change_connect_status)
        self.MyServer.signal_you.connect(self.add_message)

        self.change_connect_status(self.__is_connected)

    def add_message(self, msg):
        time = QTime.currentTime()
        print(msg, " !!!")
        self.plaintText.insertPlainText(r"<b>[{0}]</b> {1} {2}".format(time.toString("hh:mm:ss"), msg, "\n"))

    def initialize_component(self):
        self.button_send = QPushButton("Send")
        self.button_send.setShortcut("return")
        self.button_send.setMinimumSize(QSize(50, 20))
        self.button_send.clicked.connect(self.send_message)

        # self.button_file = QPushButton("FileSend")
        # self.button_file.clicked.connect(self.send_file)

        self.lineEd_message = QLineEdit()
        self.lineEd_nick = QLineEdit()

        self.msg_lab = QLabel("Сообщения:")
        self.connection_lab = QLabel("Connection:")
        self.lab_con = QLabel()
        self.lab_nick = QLabel("Ваш никнейм:")

        self.plaintText = QPlainTextEdit()
        self.plaintText.setReadOnly(True)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.lab_nick)
        hbox4.addWidget(self.lineEd_nick)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.connection_lab)
        hbox3.addWidget(self.lab_con)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.msg_lab)
        hbox2.addSpacing(50)
        hbox2.addLayout(hbox3)

        hbox1 = QHBoxLayout()
        # hbox1.addWidget(self.button_file)
        hbox1.addWidget(self.lineEd_message)
        hbox1.addWidget(self.button_send)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.plaintText)
        vbox.addLayout(hbox1)

        self.setLayout(vbox)

    @pyqtSlot()
    def send_message(self):
        if self.__is_connected:
            text = "{0}: {1}".format(self.lineEd_nick.text(), self.lineEd_message.text())
            self.lineEd_message.clear()
            self.MyServer.send_message(text)

    # def send_file(self):
    #     self.MyServer.send_file()

    def change_connect_status(self, status):
        self.__is_connected = status
        self.connection_lab.setText("Connection:")
        if not self.__is_connected:
            self.lab_con.setPixmap(QPixmap("disconnected.png").scaled(QSize(32, 32), Qt.KeepAspectRatio))
            self.MyServer.Read.terminate()
            self.MyServer.start()
        else:
            self.lab_con.setPixmap(QPixmap("connected.png").scaled(QSize(32, 32), Qt.KeepAspectRatio))


class ReadMessage(QThread):
    signal = pyqtSignal(str)
    signal_connected = pyqtSignal(bool)

    def __init__(self, server):
        if not isinstance(server, socket.socket):
            raise TypeError
        self.server = server
        super().__init__()

    def run(self):
        while True:
            try:
                data = self.server.recv(1024).decode("utf-8")
                print(data, "???")
                self.signal.emit(data)
            except ConnectionResetError:
                self.signal_connected.emit(False)
                break


class MyServer(QThread):
    signal_you = pyqtSignal(str)
    signal_connected = pyqtSignal(bool)

    def __init__(self, func1, func2):
        super().__init__()
        self.functions = (func1, func2)
        self.initialize_server()

    def initialize_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__read = ReadMessage(self.server)
        host = socket.gethostname()
        print(host)
        port = 1234
        self.server_addres = host, port
        self.server.bind((host, 0))
        self.__read.signal.connect(self.functions[0])
        self.__read.signal_connected.connect(self.functions[1])

    def run(self):
        is_connected = False

        print(1)
        while not is_connected:
            try:
                print(2)
                self.server.connect(self.server_addres)
                print(3)
                self.server.send("CONNECTION_SUCCEED".encode("1251"))
                if self.server.recv(1024).decode("1251") == "True":
                    print("Connected! Server is now online...")
                    is_connected = True
                    self.signal_connected.emit(is_connected)
                    self.__read.start()
                    break
            except ConnectionResetError:
                print("Server is offline...Repeat")
            except OSError as msg:
                if msg.errno == 10056:
                    self.server.close()
                    self.initialize_server()

                print(msg)
            self.sleep(5)

    def send_message(self, message):
        self.server.sendto(message.encode("utf-8"), self.server_addres)
        self.signal_you.emit("(You){0}".format(message))

    # def send_file(self):
    #     path = "back.jpg"
    #     file = open(path, "rb")
    #     info = os.stat(path)[6]
    #     parts = info // 1024
    #     left = info % 1024
    #     string = "{0} {1} {2}".format(path, parts, left)
    #     self.server.send("1".encode("1251"))
    #     self.server.send(string.encode("1251"))
    #     for i in range(parts):
    #         self.server.send(file.read(1024))
    #     self.server.send(file.read(left))
    #     file.close()

    def get_read(self):
        return self.__read

    Read = property(get_read)


class MainWindow(QMainWindow):
    def __init__(self, version="0.0.0"):
        super().__init__()
        self.UI = UserInterface()
        self.setCentralWidget(self.UI)
        self.setFont(QFont("Arial", 11))
        self.setWindowIcon(QIcon("letter.ico"))
        self.setWindowTitle("ChatPy {0} TCP".format(version))
        self.setMaximumSize(QSize(360, 800))
        self.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow("0.6.7")
    file = open("stile.txt", "r")
    stile = file.read()
    file.close()
    app.setStyleSheet(stile)
    sys.exit(app.exec_())
