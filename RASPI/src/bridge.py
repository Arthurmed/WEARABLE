import rospy
from wearable.msg import signals, mode, freq
from threading import Thread
import time
import socket
import sys



#VARIABLES SERVER
HOST = '192.168.1.16'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setblocking(False)
s.settimeout(None)

#binding socket to localhost
try:
    s.bind((HOST, PORT))
    s.listen(10)
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
print 'Socket bind complete'


#ACEPTING INCOMING CONNEXIONS

servers = []
def checking_connections():
    global servers
    while not rospy.is_shutdown():
        print("escuchando")
        sc, addr = s.accept()
        sc.settimeout(None)
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        servers.append(sc)


t1 = Thread(target=checking_connections)
t1.setDaemon(True)
t1.start()


def callback_signals(data):

    for server in servers:
        server.send(str(data.EDA))


def callback_shutdown():

    print'adios'
    for server in servers:
        server.close()
    s.close()

def main():


    #INICIO ROS NODES PUBLISHER Y SUBSCRIBERS
    rospy.init_node("listener")
    pub_mode = rospy.Publisher('mode', mode, queue_size=20)
    pub_freq = rospy.Publisher('frequency', freq, queue_size=20)
    rospy.Subscriber("signals", signals, callback_signals)
    rospy.on_shutdown(callback_shutdown)  # when shuttingdown the node


    while not rospy.is_shutdown():


        if servers:
            for server in servers:
                try:
                    recibido = server.recv(1024).split(',')  # TODO: hacerla non-blocking

                    if recibido[0] == 'RUN':
                        pub_mode.publish(1)  # start measurings

                    elif recibido[0] == 'STOP':
                        pub_mode.publish(0)  # stop measuring

                    elif recibido[0] == 'RESET':
                        pub_mode.publish(2)

                    elif recibido[0] == 'FREQ':
                        pub_freq.publish(int(recibido[1]))

                    print recibido
                except socket.error, e:
                    print(e)
                    server.close()  # el peer ha cerrado al conexion
                    servers.remove(server)
                    print('se ha desconectado')
        else:

            time.sleep(0.1)






if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        for server in servers:
            server.close()
        s.close()


