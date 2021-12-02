import socket
import sys
import select
import threading

global running
contor = 0
data = input("client trimite: ")
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
UDPClientSocket.sendto(bytes(data, encoding="ascii"), ("127.0.0.1", int(20001)))
while 1:
    # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
    # Stabilim un timeout de 1 secunda
    data, address = UDPClientSocket.recvfrom(1024)
    print("S-a receptionat ", str(data), " de la ", address)
    print("Contor= ", contor)
