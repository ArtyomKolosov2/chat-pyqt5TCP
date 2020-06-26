import socket
from PyQt5.QtCore import QThread

connections = []


class GetConnections(QThread):
    def __init__(self, server, num_of_clients=20):
        super().__init__()
        if not (isinstance(server, socket.socket) and isinstance(num_of_clients, int)):
            raise TypeError
        self.server = server
        self.num_of_clients = num_of_clients
        self.start()

    def run(self):
        self.server.listen(5)
        while True:
            sock, addr = self.server.accept()
            print('Connected to :', addr[0], ':', addr[1])
            if sock.recv(1024).decode("1251") == "CONNECTION_SUCCEED":
                sock.send("True".encode("1251"))
                connections.append(Connection(sock, addr))


class Connection(QThread):
    def __init__(self, sock, addr):
        super().__init__()
        if not isinstance(sock, socket.socket):
            raise TypeError("Not A Server")
        self.sock = sock
        self.addr = addr
        # self.wait = WaitMessage(sock)
        # self.wait.start()
        self.start()

    def __str__(self):
        return "{0}".format(self.sock)

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
            except ConnectionResetError:
                print("Connection {0} was closed".format(self.addr))
                connections.remove(self)
                break
            else:
                # if data.decode("1251") == "1":
                #     main_info = self.sock.recv(1024).decode("1251")
                #     main_info = main_info.split()
                #     for i in range(len(main_info)):
                #         if main_info[i].isdigit():
                #             main_info[i] = int(main_info[i])
                #     download = DownloadFile(
                #         self.sock,
                #         main_info[0],
                #         main_info[1],
                #         main_info[2]
                #     )
                # else:
                    print(self.addr, data.decode("utf-8"))
                    for connection in connections:
                        if not connection == self:
                            connection.sock.send(data)


class DownloadFile(QThread):
    def __init__(self, server, path, amount_of_segmnets, last_part):
        super().__init__()
        self.server = server
        self.segments = amount_of_segmnets
        self.path = path
        self.last_part = last_part
        self.start()

    def run(self):
        path = "files\\{0}".format(str(self.path))
        print(path)
        file = open(str(path), "wb")
        self.sleep(1)
        for i in range(self.segments):
            file.write(self.server.recv(1024))
        file.write(self.server.recv(self.last_part))
        file.close()
        print("over")



def main():

    host = socket.gethostname()
    port = 1234
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))

    except OSError:
        print("Error: Server is already running!")
        exit(1)
    connect = GetConnections(server)
    while True:
        com = input("Command: ")
        if com == "1":
            for connection in connections:
                print(connection)


if __name__ == "__main__":
    main()
