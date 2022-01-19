from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QLabel, QApplication
from PyQt5.QtWidgets import QMainWindow
import socket
import sys
import select
import threading
import package
import random


class App(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Transfer files with congestion control - CLIENT SIDE'
        self.left = 150
        self.top = 150
        self.width = 500
        self.height = 375

        # Parametrii pt conexiune
        self.ip_address_sender = "127.0.0.1"
        self.ip_address_receiver = "127.0.0.1"
        self.sender_port = "20001"
        self.receiver_port = "20001"
        self.probability = 0.9
        self.run = False


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

    def set_probability(self):
        self.probability = self.textbox_probability.text()
        print(self.probability)

    def break_message(self):
        global received_file, contor, r, rec_data, is_recieving, ack, src, s,running
        max = 1
        aux_ack = ""
        cnt = 0
        # luam fiecare pachet din lista (rec_data) si il prelucram;
        # adaugand continutul la mesajul final
        for x in rec_data:
            p = random.random()
            aux = x.split("||")
            date = ""
            for x in aux:
                if x.startswith("ACK--"):
                    temp, ack = x.split("--")
                elif x.startswith("SRC--"):
                    temp, src = x.split("--")
                elif x.startswith("SECV--"):
                    temp, secv_numb = x.split("--")
                else:
                    date = x

            #received_file = received_file + date

            # verificam daca pachetul receptionat este ultimul (if ack == "t") si afisam fisierul primit
            if ack == "f":
                if p < float(self.probability):
                    s.sendto(bytes("T||" + str(secv_numb) + "||-1", encoding="ascii"), (self.ip_address_sender, int(src)))
                    received_file[int(secv_numb)] = date
                    max = int(secv_numb)
                    cnt = cnt + 1
                    # incercam retrimitere pachetul pierdut
                    print("s-a primit pachetul " + str(secv_numb))
                else:
                    s.sendto(bytes("F||" + str(secv_numb) + "||-1", encoding="ascii"), (self.ip_address_sender, int(src)))
                    print("Eroare la pachetul " + str(secv_numb))
            if ack == "t":
                aux_ack = ack
                print("S-au receptionat cu succes", str(cnt), " pachete din " + str(len(rec_data)))
                final = ""
                s.sendto(bytes("F||" + str(secv_numb) + "||-1", encoding="ascii"), (self.ip_address_sender, int(src)))
                for i in range(1, contor + 1):
                    final = final + received_file[i]
                print(received_file)
                print("mesaj final receptionat: ", final)
                is_recieving = False
                running = False
        if aux_ack != "t":
            s.sendto(bytes("N||" + str(-2) + "||" + str(cnt), encoding="ascii"), (self.ip_address_sender, int(self.sender_port)))
            # resetam contorul responsabil de a arata nr de pachete primite
        # golim lista pentru a o repopula cu noile pachete primite
        print("S-au receptionat cu succes", str(cnt), " pachete din " + str(len(rec_data)))
        print()

        rec_data.clear()

        contor = contor + cnt

    def receive_fct(self):
        global running, contor, r, rec_data, is_recieving
        is_recieving = True
        while running:
            # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
            # Stabilim un timeout de 1 secunda
            # o s aprelucram pachetele primite
            r, _, _ = select.select([s], [], [], 1)
            if not r and is_recieving:
                self.break_message()
            else:
                # sleep(1)

                data, address = s.recvfrom(1024)
                temp = data.decode("ascii")
                # adaugam in lista pachetele
                rec_data.append(temp)

    def set_run(self):
        self.run = True
        print(self.run)

        global running, rec_data, received_file, s,contor
        rec_data = []
        # Creare socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        received_file = {}
        running = True
        contor = 0
        try:
            receive_thread = threading.Thread(target=self.receive_fct)
            receive_thread.start()
        except:
            print("Eroare la pornirea thread‐ului")
            sys.exit()

        #s.sendto(bytes("Hello server", encoding="ascii"), (self.ip_address_sender, int(self.sender_port)))
        s.sendto(bytes("Hello server||-2||-3", encoding="ascii"), (self.ip_address_sender, int(self.sender_port)))

        while running:
            try:
                x = 1
            except KeyboardInterrupt:
                running = False
                print("Waiting for the thread to close...")
                #s.sendto(bytes("client closing", encoding="ascii"), (self.ip_address_sender, int(self.sender_port)))
                s.sendto(bytes("client closing", encoding="ascii"), (self.ip_address_sender, int(self.sender_port)))

                receive_thread.join()
                break

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

        self.textbox_probability = QLineEdit(self)
        self.textbox_probability.move(10, 235)
        self.textbox_probability.resize(75, 30)
        self.textbox_probability.setText("0.9")

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

        button_probability = QPushButton('Confirm', self)
        button_probability.setToolTip('RECEIVER PORT BUTTON')
        button_probability.move(90, 235)
        button_probability.clicked.connect(self.set_probability)

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
