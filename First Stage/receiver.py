import socket
import sys
import select
import threading


class Package:
    def __init__(self, data, seq, checksum, ack, src_port, dest_port, src_addr, dest_addr):
        self.data = data
        self.seq = seq
        self.checksum = checksum
        self.ack = ack
        self.src_port = src_port
        self.dest_port = dest_port
        self.src_addr = src_addr
        self.dest_addr = dest_addr


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
            data, address = s.recvfrom(1024)
            print("S-a receptionat ", str(data), " de la ", address)
            print("Contor= ", contor)


# Citire nr port din linia de comanda


# Creare socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

s.bind(('127.0.0.1', int(20001)))

running = True

# try:
#     receive_thread = threading.Thread(target=receive_fct)
#     receive_thread.start()
# except:
#     print("Eroare la pornirea thread‐ului")
#     sys.exit()
bytesAddressPair = s.recvfrom(1024)
message = bytesAddressPair[0]
address = bytesAddressPair[1]
clientMsg = "Message from Client:{}".format(message)
clientIP = "Client IP Address:{}".format(address)
print(clientMsg)
print(clientIP)
while True:
    try:
        data = input("Trimite: ")
        s.sendto(bytes(data, encoding="ascii"), address)
    except KeyboardInterrupt:
        running = False
        print("Waiting for the thread to close...")
        # receive_thread.join()
        break
