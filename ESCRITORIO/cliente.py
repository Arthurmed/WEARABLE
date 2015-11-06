__author__ = 'USUARIO'

import socket
from threading import Thread

s = socket.socket()
s.connect(("192.168.1.30", 8888))


def read_data():

    while True:

        mensaje = s.recv(1024)
        if mensaje != '':
            print mensaje

        if mensaje == "quit":
            break


t1 = Thread(target=read_data)
t1.daemon = True
t1.start()

while True:

    mensaje = raw_input("> ")
    s.send(mensaje)
    if mensaje == "quit":
        break

print "adios"

s.close()