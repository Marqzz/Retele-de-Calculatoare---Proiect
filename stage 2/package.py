def pack(path, ack, src_port, size):
    file = open(path)
    text = file.read()

    file.close()
    pachet = Package("", ack, src_port, size)
    rez = []


    k = 1
    print(len(text))
    # parcurgem continutul fisierului si adaugam in lista "rez" pachetele formatate.
    # verificam sa nu depasim dimeniunea fisierului
    for i in range(0, len(text), pachet.size):

        if i + pachet.size >= len(text):
            rez.append(
                pachet.formHeader(pachet, k) + Package.stringToBinary("||") + pachet.stringToBinary(text[i:len(text)]))
        else:
            rez.append(
                pachet.formHeader(pachet, k) + Package.stringToBinary("||") + pachet.stringToBinary(text[i:(i + pachet.size)]))
        k = k + 1

# adaugam la final pachetul de confirmare a finalizarii trimiterii
    rez.append(pachet.formHeader(Package("", "t", src_port, pachet.size), "-1"))
    for j in rez:
        print(Package.binaryToString(j))

    return rez


class Package:
    dest_port = ""
    src_port = ""
    ack = ""
    size = 0

    def __init__(self, data, ack, src_port, size):
        self.data = data
        self.ack = ack
        self.src_port = src_port
        self.size = size

    @staticmethod
    def stringToBinary(s):
        return [bin(ord(x))[2:].zfill(2) for x in s]

    @staticmethod
    def binaryToString(b):
        return ''.join([chr(int(x, 2)) for x in b])

    @staticmethod
    def formHeader(pack, i):
        return pack.stringToBinary("ACK--" + pack.ack + "||SRC--" + pack.src_port + "||SECV--" + str(i))
