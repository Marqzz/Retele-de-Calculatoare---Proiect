def pack(path, ack, src_port):
    file = open(path)
    text = file.read()

    file.close()
    pachet = Package("", ack, src_port)
    rez = []

    size = 16
    print(len(text))
    for i in range(0, len(text), size):
        if i + size >= len(text):
            rez.append(
                pachet.formHeader(pachet) + Package.stringToBinary("||") + pachet.stringToBinary(text[i:len(text)]))
            i = i + 1
        else:
            rez.append(
                pachet.formHeader(pachet) + Package.stringToBinary("||") + pachet.stringToBinary(text[i:(i + size)]))

    rez.append(pachet.formHeader(Package("", "t", src_port)))
    for j in rez:
        print(Package.binaryToString(j))

    return rez


class Package:
    dest_port = ""
    src_port = ""
    ack = ""
    size = 0

    def __init__(self, data, ack, src_port):
        self.data = data

        self.ack = ack
        self.src_port = src_port

    @staticmethod
    def stringToBinary(s):
        return [bin(ord(x))[2:].zfill(2) for x in s]

    @staticmethod
    def binaryToString(b):
        return ''.join([chr(int(x, 2)) for x in b])

    @staticmethod
    def formHeader(pack):
        return pack.stringToBinary("ACK--" + pack.ack + "||SRC--" + pack.src_port)
