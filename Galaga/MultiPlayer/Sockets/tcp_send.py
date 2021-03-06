import socket
from PyQt5.QtCore import QThread


class TcpSend:

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, address, port):
        super().__init__()
        TcpSend.socket.connect((address, port))

    def send_msg(self, msg):
        data = TcpSend.socket.send(msg.encode('utf8'))
        return data