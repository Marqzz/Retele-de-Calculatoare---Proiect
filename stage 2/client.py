import random
import socket
import sys
import select
import threading
from time import sleep

global rec_data
rec_data = []


def break_message():
    global received_file, contor, r, rec_data, is_recieving
    max = 1
    aux_ack = ""
    cnt = 0
    # luam fiecare pachet din lista (rec_data) si il prelucram, adaugand continutul la mesajul final
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
        # print(contor)

        # verificam daca pachetul receptionat este ultimul (if ack == "t") si afisam fisierul primit
        if ack == "f":
            if p < 0.9:
                s.sendto(bytes("T||" + str(secv_numb) + "||-1", encoding="ascii"), ("127.0.0.1", int(src)))
                received_file[int(secv_numb)] = date
                max = int(secv_numb)
                cnt = cnt + 1
                print("s-a primit pachetul " + str(secv_numb))
            else:
                s.sendto(bytes("F||" + str(secv_numb) + "||-1", encoding="ascii"), ("127.0.0.1", int(src)))
                print("Eroare la pachetul " + str(secv_numb))
        if ack == "t":
            aux_ack = ack
            print("S-au receptionat cu succes", str(cnt), " pachete din " + str(len(rec_data)))
            final = ""
            s.sendto(bytes("F||" + str(secv_numb) + "||-1", encoding="ascii"), ("127.0.0.1", int(src)))
            for i in range(1, contor + 1):
                final = final + received_file[i]
            print(received_file)
            print("mesaj final receptionat: ", final)
            is_recieving = False
    if aux_ack != "t":
        s.sendto(bytes("N||" + str(-2) + "||" + str(cnt), encoding="ascii"), ("127.0.0.1", int(20001)))
        # resetam contorul responsabil de a arata nr de pachete primite
    # golim lista pentru a o repopula cu noile pachete primite
    print("S-au receptionat cu succes", str(cnt), " pachete din " + str(len(rec_data)))
    print()

    rec_data.clear()



    contor = contor + cnt


def receive_fct():
    global running, contor, r, rec_data, is_recieving
    is_recieving = True
    while running:
        # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
        # Stabilim un timeout de 1 secunda daca nu se mai primesc pachete, inseamna ca serverul asteapta confirmarea,
        # deci vom prelucra pachetele primite.
        r, _, _ = select.select([s], [], [], 1)
        if not r and is_recieving:
            break_message()
        else:
            data, address = s.recvfrom(1024)
            temp = data.decode("ascii")
            # adaugam in lista pachetele
            rec_data.append(temp)


# Creare socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
received_file = {}
contor = 0
running = True
try:
    receive_thread = threading.Thread(target=receive_fct)
    receive_thread.start()
except:
    print("Eroare la pornirea thread‐ului")
    sys.exit()

# stabilim conexiunea cu serverul
s.sendto(bytes("Hello server||-2||-3", encoding="ascii"), ("127.0.0.1", int(20001)))

while True:
    try:
        x = 1
    except KeyboardInterrupt:
        running = False
        print("Waiting for the thread to close...")
        s.sendto(bytes("client closing", encoding="ascii"), ("127.0.0.1", int(20001)))
        receive_thread.join()
        break
