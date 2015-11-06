

import serial

class BLE(serial.Serial):

    def __init__(self, parent=None):
        super(BLE, self).__init__(parent)
        #check si decive is connected:
        self._CONNECTED = False
        self._timeout = 1

    def cmd(self, data):
        return data + '\r\n'

    def check_paring(self):

        """
        :param self:
        :return: string with OK if AT mode
        """
        self.flush()
        self.write(self.cmd('AT'))
        try:
            a = self.readline()
            return False

        except:
            return True


    def get_devices(self):

        """
        :return:
        dictionary with the found devices and their respective MAC address
        """
        devices = dict()

        #TODO: modify for taking into consideration if _CONNECTED
        self.write(self.cmd('AT+INQ'))
        #time.sleep(0.5)  # time to reply
        ack = '+INQE'
        answer = ''
        while ack not in answer:  # ack not in answer
            answer += self.read(50)
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
                self.write(self.cmd('AT+CONN' + ble_id))
                ack = '+CONNECTED>>' + device[ble_id]
                answer = ''
                while ack not in answer:
                    answer += self.read(50)
                self._CONNECTED = True
                return 'CONNECTED>>' + device[ble_id]

    def read_data(self):
        """

        :return: a line of data
        """
        return self.readline()


    def write_data(self, data):
        """

        :param data:
        :return: none
        """
        self.write(data)

    def disconnect(self):
        self.close()

    def get_state(self):
        return self._CONNECTED
