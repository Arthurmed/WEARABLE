import socket


class MONITOR(object):

    def __init__(self):
        """
        Communication with Matlab monitor in order to plot information
        through UDP socket

        """

        #TODO: Run matlab process to automatize
        self._S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ADD = ('192.168.1.30', 9999)
        self._SERVER = ('192.168.1.30', 10000)
        self._S.bind(self._ADD)  # bind server
        self._S.connect(self._SERVER)  # connect to matlab server

    def send_data(self, data):

        self._S.send(data)

class DISPLAY(object):

    def __init__(self):
        """
        Communication with Matlab monitor in order to plot information
        through UDP socket

        """

        #TODO: Run matlab process to automatize
        self._S = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ADD = ('192.168.1.30', 9999)
        self._SERVER = ('192.168.1.30', 10001)  # ip from display
        self._S.bind(self._ADD)  # bind server
        self._S.connect(self._SERVER)  # connect to matlab server

    def send_data(self, data):
        self._S.send(data)

    def receive_data(self):
        self._S.recv(50)