import socket
import sys
import time

import select
import threading

import package
from package import *


def confirm_receive(date):
    global confirmed, first_conn, vol, connected, k, retransmitere_pachete, err_transmitere, cnt, cwnd
    # verificam confirmarea primirii pachetului.
    aux = date.decode("ascii")
    ack = aux.split("||")
    # print("pachet primit")
    # print(ack)

    if int(ack[1]) == -1:
        print("final transmisie fisier!")
        print(retransmitere_pachete)
        first_conn = True
        vol = 1
        cwnd = 64
    # "T" = confirmare primire de la client
    elif ack[0] == "F":
        print("eroare la trimiterea pachetului cu numarul de secventa: " + str(ack[1]))
        retransmitere_pachete.append(int(ack[1]))
        err_transmitere = True
        if vol / 2 >= 16:
            cwnd = vol / 2
        elif cwnd / 2 >= 16:
            cwnd = cwnd / 2
        vol = 1
    elif ack[0] == "T":
        cnt = cnt + 1
    if int(ack[2]) == cnt:
        confirmed = True
    if confirmed and not err_transmitere:
        if vol < cwnd:
            vol = vol * 2
        else:
            vol = vol + 1


def first_connection():
    global connected, confirmed, connected_client, k, vol
    k = 0
    vol = 1
    connected_client = s.recvfrom(1024)
    connected = True
    confirmed = True


def receive_fct():
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
                first_connection()
                first_conn = False
            # receptionam mesajul de la client, prelucram confirmarea
            # si informam utilizatorul daca mesajul a fost sau nu transmis cu succes
            else:
                connected_client = s.recvfrom(1024)
                confirm_receive(connected_client[0])
                # if confirmed:
                # print("Mesajul catre clientul cu adresa: ", connected_client[1], " a fost transmis cu succes!")

                # print("Contor= ", contor, "s")


# Creare socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

s.bind(('127.0.0.1', int(20001)))

to_send = package.pack("fisier.txt", "f", "20001", 64)
running = True
connected = False
confirmed = True
first_conn = True
retransmitere_pachete = []
cwnd = 64
x = threading.main_thread()
# thread responsabil de receptia mesajelor
try:
    receive_thread = threading.Thread(target=receive_fct)
    receive_thread.start()
except:
    print("Eroare la pornirea thread‐ului")
    sys.exit()

print("se asteapta conectarea clientului")

vol = 1
k = 0
err_transmitere = False
cnt = 0


# slow start si AIMD
def send_package():
    global k, confirmed, vol, retransmitere_pachete, err_transmitere, connected
    # trimitem pachetele in functie de fereastra alocata si asteptam confirmarea
    err_transmitere = True
    for i in range(0, vol):
        if len(retransmitere_pachete) == 0 and confirmed:
            err_transmitere = False

        if k == len(to_send) - 1 and not err_transmitere and confirmed:
            data = Package.binaryToString(to_send[k])
            s.sendto(bytes(data, encoding="ascii"), connected_client[1])
            k = k + 1
            confirmed = False
            connected = False

        if k < len(to_send) - 1 and len(retransmitere_pachete) == 0:
            data = Package.binaryToString(to_send[k])
            s.sendto(bytes(data, encoding="ascii"), connected_client[1])
            print("k="+str(k))
            k = k + 1
            confirmed = False
            err_transmitere = False
        if len(retransmitere_pachete) > 0:
            data = Package.binaryToString(to_send[retransmitere_pachete.pop() - 1])
            s.sendto(bytes(data, encoding="ascii"), connected_client[1])
            confirmed = False
            err_transmitere = False


    #print(vol)


print(len(to_send))
while True:
    while connected:
        try:
            # asteptam confirmarea pentru trimiterea urmatoarelor pachete
            while k < len(to_send) and confirmed:
                send_package()

        except KeyboardInterrupt:
            running = False
            print("Waiting for the thread to close...")
            receive_thread.join()
            sys.exit()
