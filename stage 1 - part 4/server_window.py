from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QLabel, QApplication
from PyQt5.QtWidgets import QMainWindow
import socket
import sys
import select
import threading
import package

global confirmed, first_conn, connected, connected_client, k, running, s, to_send


def confirm_receive(date):
    global confirmed, first_conn, vol
    aux = date.decode("ascii")

    ack = aux.split("||")
    if ack[0] == "F":
        confirmed = False
        print("final transmisie fisier!")
        first_conn = True
        vol = 1
    if ack[0] == "T":
        confirmed = True







class App(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Transfer files with congestion control - SERVER SIDE'
        self.left = 150
        self.top = 150
        self.width = 500
        self.height = 375

        # Parametrii pt conexiune
        self.file_path = ""
        self.ip_address_sender = ""
        self.ip_address_receiver = ""
        self.sender_port = ""
        self.receiver_port = ""
        self.number_of_packets = ""
        self.run = False
        self._mutex = QMutex()
        self._mutex2 = QMutex()
        # Pentru algoritm
        self.threshold = 0

        self.initUI()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.file_path = fileName
        print(self.file_path)

    def set_sender_address(self):
        self.ip_address_sender = self.textbox_addr_sender.text()
        print(self.ip_address_sender)

    def set_receiver_address(self):
        self.ip_address_receiver = self.textbox_addr_receiver.text()
        print(self.ip_address_receiver)

    def set_sender_port(self):
        self.sender_port = self.textbox_sender_port.text()
        print(self.sender_port)

    def set_receiver_port(self):
        self.receiver_port = self.textbox_receiver_port.text()
        print(self.receiver_port)

    def set_number_of_packets(self):
        self.number_of_packets = self.textbox_packets.text()
        print(self.number_of_packets)

    def set_threshold(self):
        self.threshold = self.textbox_threshold.text()
        print(self.threshold)

        # self._mutex.unlock()

    # slow start
    def send_package(self):
        global k, confirmed, vol, old_k, connected_client, to_send
        old_k = k  # in caz de eroare (timeout), se va retine ultimul set de pachete care trebuia trimis.
        thresh = 16
        #self._mutex2.lock()
        for i in range(0, vol):
            if (k < len(to_send)):
                data = package.Package.binaryToString(to_send[k])
                s.sendto(bytes(data, encoding="ascii"), connected_client[1])
                #self._mutex2.lock()
                k = k + 1
                #self._mutex2.unlock()
        if vol < thresh:
            vol = vol * 2
        else:
            vol = vol + 1
        confirmed = False
        #self._mutex2.unlock()

    def first_connection(self):

        global connected, confirmed, connected_client, k
        #self._mutex.lock()
        k = 0
        connected_client = s.recvfrom(1024)
        connected = True
        confirmed = True
        #self._mutex.unlock()

    def receive_fct(self):
        global running, connected_client, connected, first_conn
        contor = 0
        #self._mutex.lock()
        while running:
            # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            r, _, _ = select.select([s], [], [], 1)
            if not r:
                contor = contor + 1
            else:
                if first_conn:
                    self.first_connection()
                    first_conn = False
                else:
                    connected_client = s.recvfrom(1024)
                    confirm_receive(connected_client[0])
                    if confirmed:
                        print("Mesajul catre clientul cu adresa: ", connected_client[0], " a fost transmis cu succes!")
                    else:
                        print("Eroare la transmiterea mesajuli catre clientul cu adresa: ", connected_client[1])
                    print("Contor= ", contor, "s")
        #self._mutex.unlock()

    def set_run(self):
        #self._mutex.lock()
        self.run = True
        print(self.run)
        global s, to_send, running, first_conn, connected, confirmed,vol
        # Creare socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        s.bind((self.ip_address_receiver, int(self.receiver_port)))


        to_send = package.pack("fisier.txt", "f", self.receiver_port)#20001
        #to_send = package.pack(self.file_path, "f", self.receiver_port)

        running = True
        connected = False
        confirmed = True
        first_conn = True

        try:
            receive_thread = threading.Thread(target=self.receive_fct)
            receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()

        print("se asteapta conectarea clientului")

        vol = 1
        k = 0

        print(len(to_send))
        while True:
            while connected:
                try:
                    while k < len(to_send) and confirmed:
                        self.send_package()

                except KeyboardInterrupt:
                    running = False
                    print("Waiting for the thread to close...")
                    receive_thread.join()
                    #self._mutex.unlock()
                    sys.exit()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        # Textboxs

        self.textbox_packets = QLineEdit(self)
        self.textbox_packets.move(10, 35)
        self.textbox_packets.resize(75, 30)
        self.textbox_packets.setText("1")

        self.textbox_addr_sender = QLineEdit(self)
        self.textbox_addr_sender.move(10, 75)
        self.textbox_addr_sender.resize(75, 30)
        self.textbox_addr_sender.setText("Sender IP")

        self.textbox_addr_receiver = QLineEdit(self)
        self.textbox_addr_receiver.move(10, 115)
        self.textbox_addr_receiver.resize(75, 30)
        self.textbox_addr_receiver.setText("Receiver IP")

        self.textbox_sender_port = QLineEdit(self)
        self.textbox_sender_port.move(10, 155)
        self.textbox_sender_port.resize(75, 30)
        self.textbox_sender_port.setText("Sender port")

        self.textbox_receiver_port = QLineEdit(self)
        self.textbox_receiver_port.move(10, 195)
        self.textbox_receiver_port.resize(75, 30)
        self.textbox_receiver_port.setText("Receiver port")

        self.textbox_threshold = QLineEdit(self)
        self.textbox_threshold.move(10, 235)
        self.textbox_threshold.resize(75, 30)
        self.textbox_threshold.setText("0")

        # Buttons
        button_packets = QPushButton('Num of Packets', self)
        button_packets.setToolTip('NUM OF PACKS BUTTON')
        button_packets.move(90, 35)
        button_packets.clicked.connect(self.set_number_of_packets)

        button_address_sender = QPushButton('Confirm', self)
        button_address_sender.setToolTip('IP SENDER BUTTON')
        button_address_sender.move(90, 75)
        button_address_sender.clicked.connect(self.set_sender_address)

        button_address_receiver = QPushButton('Confirm', self)
        button_address_receiver.setToolTip('IP RECEIVER BUTTON')
        button_address_receiver.move(90, 115)
        button_address_receiver.clicked.connect(self.set_receiver_address)

        button_sender_port = QPushButton('Confirm', self)
        button_sender_port.setToolTip('SENDER PORT BUTTON')
        button_sender_port.move(90, 155)
        button_sender_port.clicked.connect(self.set_sender_port)

        button_sender_port = QPushButton('Confirm', self)
        button_sender_port.setToolTip('RECEIVER PORT BUTTON')
        button_sender_port.move(90, 195)
        button_sender_port.clicked.connect(self.set_receiver_port)

        button_threshold = QPushButton('Confirm', self)
        button_threshold.setToolTip('THRESHOLD BUTTON')
        button_threshold.move(90, 235)
        button_threshold.clicked.connect(self.set_threshold)

        button_choose_file = QPushButton('Choose File', self)
        button_choose_file.setToolTip('CHOOSE FILE BUTTON')
        button_choose_file.move(45, 275)
        button_choose_file.clicked.connect(self.openFileNameDialog)

        button_run = QPushButton('Run', self)
        button_run.setToolTip('RUN BUTTON')
        button_run.move(45, 315)
        button_run.clicked.connect(self.set_run)

        # adaugarea logo AC
        # am luat toata poza ca un label , si am manevrat o dupa nevoi
        label = QLabel(self)
        pixmap = QPixmap('logo_ac_iasi.jpg')
        label.setPixmap(pixmap)
        label.resize(300, 300)
        label.move(200, 25)

        self.show()


if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
