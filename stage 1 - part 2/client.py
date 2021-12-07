import socket
import sys
import select
import threading
from time import sleep


def break_message(data):
    global received_file

    temp = data.decode("ascii")
    aux = temp.split("||")
    date = ""
    for x in aux:
        if x.startswith("ACK--"):
            temp, ack = x.split("--")
        elif x.startswith("SRC--"):
            temp, src = x.split("--")
        else:
            date = x

    received_file = received_file + date
    if ack == "f":
        s.sendto(bytes("T", encoding="ascii"), ("127.0.0.1", int(src)))
    if ack == "t":
        s.sendto(bytes("F", encoding="ascii"), ("127.0.0.1", int(src)))
        print("mesaj final receptionat: ", received_file)


def receive_fct():
    global running
    contor = 0

    while running:
        # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
        # Stabilim un timeout de 1 secunda
        r, _, _ = select.select([s], [], [], 1)
        if not r:
            contor = contor + 1
        else:
            sleep(1)
            contor = contor + 1
            data, address = s.recvfrom(1024)
            print("S-a receptionat un packet")
            print("Contor= ", contor)
            break_message(data)


# Creare socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
received_file = ""
running = True
try:
    receive_thread = threading.Thread(target=receive_fct)
    receive_thread.start()
except:
    print("Eroare la pornirea thread‐ului")
    sys.exit()

s.sendto(bytes("Hello server", encoding="ascii"), ("127.0.0.1", int(20001)))

while True:
    try:
        x = 1
    except KeyboardInterrupt:
        running = False
        print("Waiting for the thread to close...")
        s.sendto(bytes("client closing", encoding="ascii"), ("127.0.0.1", int(20001)))
        receive_thread.join()
        break
