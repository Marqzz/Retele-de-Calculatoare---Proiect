import socket
import sys
import select
import threading
from time import sleep

global rec_data
rec_data = []


def break_message():
    global received_file, contor, r, rec_data, is_recieving

    for x in rec_data:
        aux = x.split("||")
        date = ""
        for x in aux:
            if x.startswith("ACK--"):
                temp, ack = x.split("--")
            elif x.startswith("SRC--"):
                temp, src = x.split("--")
            else:
                date = x

        received_file = received_file + date

    rec_data.clear()
    print("S-au receptionat ", str(contor), " packete")
    contor = 0
    if ack == "f":
        s.sendto(bytes("T||" + str(contor), encoding="ascii"), ("127.0.0.1", int(src)))
    if ack == "t":
        s.sendto(bytes("F", encoding="ascii"), ("127.0.0.1", int(src)))
        print("mesaj final receptionat: ", received_file)
        is_recieving = False



def receive_fct():
    global running, contor, r, rec_data, is_recieving
    is_recieving = True
    contor = 0
    while running:
        # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
        # Stabilim un timeout de 1 secunda
        r, _, _ = select.select([s], [], [], 1)
        if not r and is_recieving:
            break_message()
        else:
            # sleep(1)

            data, address = s.recvfrom(1024)
            temp = data.decode("ascii")
            rec_data.append(temp)
            contor = contor + 1


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
