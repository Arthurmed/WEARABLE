

import serial
import time


class BLE(object):

    def __init__(self, PORT, BAUDRATE):

        self._BAUD = BAUDRATE
        self._PORT = PORT
        self._TIMEOUT = 0.5  # 1 seg por defecto
        self._SER = serial.Serial(self._PORT, self._BAUD, timeout=self._TIMEOUT)
        #TODO: Testear si esta conectado
        self._CONNECTED = False

    def cmd(self, data):
        return data + '\r\n'

    def get_test(self):

        """
        :param self:
        :return: string with OK if AT mode
        """
        if not self._CONNECTED:
            self._SER.write(self.cmd('AT'))
            return self._SER.read(4)
        else:
            return 'DEVICE IS CONNECTED'

    def get_devices(self):

        """
        :return:
        dictionary with the found devices and their respective MAC address
        """
        devices = dict()

        #TODO: modify for taking into consideration if _CONNECTED
        self._SER.write(self.cmd('AT+INQ'))
        #time.sleep(0.5)  # time to reply
        ack = '+INQE'
        answer = ''
        while ack not in answer:  # ack not in answer
            answer += self._SER.read(50)
            print answer
            #TODO: modify for detecting severals BLE
            if '+INQ:' in answer:  # device found in answer
                num = answer[answer.find(':') + 1]
                mac = answer[answer.find(' ') + 1:answer.find(' ') + 15]
                devices[num] = mac
        return devices

    def connect_device(self, device):
        """

        :param device: dictionary with number and MAC of device to connect
        :return: string containing CONNECTED + MAC device
        """
        if not self._CONNECTED:
            for ble_id in device.keys():
                self._SER.write(self.cmd('AT+CONN' + ble_id))
                ack = '+CONNECTED>>' + device[ble_id]
                answer = ''
                while ack not in answer:
                    answer += self._SER.read(50)
                self._CONNECTED = True
                return 'CONNECTED>>' + device[ble_id]

    def read_data(self):
        """

        :return: a line of data
        """
        return self._SER.readline()


    def write_data(self, data):
        """

        :param data:
        :return: none
        """
        self._SER.write(data)

    def disconnect(self):
        self._SER.close()
        #self._CONNECTED = False

    def get_state(self):
        return self._CONNECTED