from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QLabel, QApplication
from PyQt5.QtWidgets import QMainWindow
import socket
import sys
import select
import threading
import package
from package import *
import time

global confirmed, first_conn, connected, connected_client, k, running, s, to_send, cnt_not_acks, freq , show_final


def confirm_receive(date):
    global confirmed, first_conn, vol, connected, k, retransmitere_pachete, err_transmitere, cnt, cwnd, running, cnt_not_acks, vect_confirmari,show_final
    # verificam confirmarea primirii pachetului.

    aux = date.decode("ascii")
    ack = aux.split("||")
    if int(ack[1]) == -1:  # finalul , ultimul pachet trimis care indica finalul transmiterii
        print("Final transfer fisier!")
        print(retransmitere_pachete)
        show_final = True
        first_conn = True
        running = False
        vol = 1
        cwnd = 64

    # "F" = eroare de la client
    elif ack[0] == "F":
        cnt_not_acks = cnt_not_acks + 1

        if cnt_not_acks == 3:
            initial = int(ack[1])
            final = int(ack[1]) + vol - cnt

            for i in range(final, initial - 1, -1):
                if i < len(to_send) and not retransmitere_pachete.__contains__(i) and not vect_confirmari.__contains__(
                        i) and i < k + 1:
                    retransmitere_pachete.append(i)
                    print("am bagat pachetul " + str(i))

            err_transmitere = True
            if vol / 2 >= 16:
                cwnd = vol / 2

            elif cwnd / 2 >= 16:
                cwnd = cwnd / 2

            vol = 1

    elif ack[0] == "T":
        cnt_not_acks = 0
        cnt = cnt + 1
        vect_confirmari.append(int(ack[1]))
        err_transmitere = False

    if int(ack[2]) == cnt:
        confirmed = True

    if confirmed and not err_transmitere:
        if vol < cwnd:
            vol = vol * 2
        else:
            vol = vol + 1


class App(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Transmitator'
        self.left = 150
        self.top = 150
        self.width = 500
        self.height = 375

        # Parametrii pt conexiune
        self.file_path = "fisier.txt"
        self.ip_address_sender = "127.0.0.1"
        self.ip_address_receiver = "127.0.0.1"
        self.sender_port = "20001"
        self.receiver_port = "20001"
        self.number_of_packets = ""
        self.run = False

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

    # slow start si AIMD
    def send_package(self):
        global k, confirmed, vol, retransmitere_pachete, err_transmitere, connected, cnt_not_acks
        # trimitem pachetele in functie de fereastra alocata si asteptam confirmarea
        err_transmitere = True
        cnt_not_acks = 0
        print("-----------intrare trimitere------------")
        for i in range(0, vol):
            if len(retransmitere_pachete) == 0 and confirmed:
                err_transmitere = False

            if k == len(to_send) - 1 and not err_transmitere and confirmed:
                data = Package.binaryToString(to_send[k])
                s.sendto(bytes(data, encoding="ascii"), connected_client[1])
                k = k + 1

                confirmed = False
                connected = False
                self.label_text.setText("Final transfer fisier...")

            if k < len(to_send) - 1 and len(retransmitere_pachete) == 0:
                data = Package.binaryToString(to_send[k])
                s.sendto(bytes(data, encoding="ascii"), connected_client[1])
                print("k=" + str(k))
                k = k + 1
                confirmed = False
                self.label_text.setText("Se transfera fisierul...")

            if len(retransmitere_pachete) > 0:
                data = Package.binaryToString(to_send[retransmitere_pachete.pop() - 1])
                s.sendto(bytes(data, encoding="ascii"), connected_client[1])
                confirmed = False

    def first_connection(self):

        global connected, confirmed, connected_client, k, vol,vect_confirmari
        k = 0
        vol = 1
        connected_client = s.recvfrom(1024)
        connected = True
        confirmed = True
        vect_confirmari = []

    def receive_fct(self):
        global running, connected_client, first_conn, cnt
        contor = 0
        while running:
            # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            r, _, _ = select.select([s], [], [], 1)
            if not r:
                contor = contor + 1
                cnt = 0
            else:
                # verificam daca este prima conexiune
                if first_conn:
                    self.first_connection()
                    first_conn = False
                # receptionam mesajul de la client, prelucram confirmarea
                # si informam utilizatorul daca mesajul a fost sau nu transmis cu succes
                else:
                    connected_client = s.recvfrom(1024)
                    confirm_receive(connected_client[0])

    def set_run(self):

        self.run = True

        global s, to_send, running, first_conn, connected, confirmed, vol, retransmitere_pachete, cwnd, running, cnt_not_acks, freq,vect_confirmari,show_final
        cwnd = 64
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            s.bind((self.ip_address_receiver, int(self.receiver_port)))
        except:
            self.label_text.setText("Configuratii Gresite...")
        # Generam pachetele formate din textul nostru
        show_final = False
        vect_confirmari = []
        freq = []
        to_send = package.pack(self.file_path, "f", self.receiver_port, 64)
        cnt_not_acks = 0
        running = True
        connected = False
        confirmed = True
        first_conn = True
        retransmitere_pachete = []
        cwnd = 64
        cnt_not_acks = 0
        x = threading.main_thread()

        # thread responsabil de receptia mesajelor
        try:
            receive_thread = threading.Thread(target=self.receive_fct)
            receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()

        print("se asteapta conectarea clientului")

        vol = 1
        k = 0
        err_transmitere = False
        cnt = 0
        start_time = time.time()
        print(len(to_send))
        while running:
            actual_time = time.time()
            if actual_time - start_time > 30:
                self.label_text.setText("Timeout...")
                running = False
            while connected:
                try:
                    # asteptam confirmarea pentru trimiterea urmatoarelor pachete
                    while k < len(to_send) and confirmed:
                        self.send_package()

                except KeyboardInterrupt:
                    running = False
                    print("Waiting for the thread to close...")
                    receive_thread.join()

                    sys.exit()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.textbox_addr_sender = QLineEdit(self)
        self.textbox_addr_sender.move(10, 75)
        self.textbox_addr_sender.resize(75, 30)
        self.textbox_addr_sender.setText("127.0.0.1")

        self.textbox_addr_receiver = QLineEdit(self)
        self.textbox_addr_receiver.move(10, 115)
        self.textbox_addr_receiver.resize(75, 30)
        self.textbox_addr_receiver.setText("127.0.0.1")

        self.textbox_sender_port = QLineEdit(self)
        self.textbox_sender_port.move(10, 155)
        self.textbox_sender_port.resize(75, 30)
        self.textbox_sender_port.setText("20001")

        self.textbox_receiver_port = QLineEdit(self)
        self.textbox_receiver_port.move(10, 195)
        self.textbox_receiver_port.resize(75, 30)
        self.textbox_receiver_port.setText("20001")

        # Buttons

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

        self.label_text = QLabel(self)
        self.label_text.setText("Welcome :)")
        self.label_text.move(300,330)
        self.label_text.resize(250,30)
        #label_text.setAlignment(Qt_Alignment=AllignCenter)

        self.show()


if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
