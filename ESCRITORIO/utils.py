import serial
import struct


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

    def check_paring(self):

        """
        :param self:
        :return: string with OK if AT mode
        """
        self._SER.flush()
        self._SER.write(self.cmd('AT'))
        try:
            a = self._SER.readline()
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



class Parser():

    SOF = b'\xFD'
    ESC = b'\xFC'
    EOF = b'\xFF'


    tipoMensaje = { 'MESSAGE_TYPE_EDA': 1,
                'MESSAGE_TYPE_EMG': 2,
                'MESSAGE_TYPE_HRV': 3,
                'MESSAGE_TYPE_CTR': 10,
                }

    def __init__(self, serial_port):

        self.tipoProcesado = {'MESSAGE_TYPE_EDA': self.process_MESSAGE_TYPE_EDA,
                'MESSAGE_TYPE_EMG': self.process_MESSAGE_TYPE_EMG,
                'MESSAGE_TYPE_HRV': self.process_MESSAGE_TYPE_HRV,
                'MESSAGE_TYPE_CTR': self.process_MESSAGE_TYPE_CTR}

        self.ser = serial_port



    def verify_CS(self, raw):
        """
        Comprueba que el checksum es correcto
        @param chksum: valor que viene de la red WSN
        @return: Booleano indicando si es correcto
        """
        total = 0
        for b in raw[0:-1]:
            total += b

        return total == raw[-1]


    def twos_comp(self, val, bits=8):
        """compute the 2's compliment of int value val"""
        if (val & (1 << (bits - 1))) != 0:
            val -= (1 << bits)
        return val

    def process_MESSAGE_TYPE_EDA(self, raw):
        """
        Process the messages of class MODE
        :param raw:
        :return: dictionary with type and mode
        """
        eda = raw[2:6]
        return struct.unpack('>f', eda)


    def process_MESSAGE_TYPE_EMG(self, raw):
        """
        Process the messages of class MANUAL
        :param raw:
        :return:
        """

        pass

    def process_MESSAGE_TYPE_HRV(self):
        #TODO : implementar
        pass

    def process_MESSAGE_TYPE_CTR(self, data):
        #TODO : implementar
        pass

    def get_Trame(self):

        """
        esta funcion es una maquina de estados que me devuelve un dicionario con el tipo
        de trama y sus valores. El formato de la trama es el siguiente:

        START LL TT DATOS CS END
        - 2 bytes de comienzo
        - 1 byte de longitud
        - 1 byte de tipo de trama
        - n bytes con los datos
        - 1 byte con el Check Sum
        - 2 bytes de final de trama

        MAQUINA DE ESTADOS:
        0-> buscando comienzo de trama
        1-> leyendo trama y parseando

        :return: dictionay with data
        """

        STATUS = 0
        while True:

            if STATUS == 0:  # buscando comienzo de trama
                byte = self.ser.read(1)  # leo byte a byte
                if byte == Parser.ESC:
                    byte = self.ser.read(1)
                    if byte == Parser.SOF:
                        STATUS = 1

            if STATUS == 1: # leemos contenido de la trama
                raw = self.ser.read(1)
                LL = ord(raw)  #
                raw += self.ser.read(LL-1)  # leemos la totalidad del mensaje (menos acceso a puerto)
                STATUS = 0

                #if self.verify_CS(raw):  # TODO: comprobamos que no hay errores en el checksum
                if True:
                    TT = ord(raw[1])  # extraemos el tipo de mensaje para procesar
                    for t, value in Parser.tipoMensaje.items():
                        if value == TT:  # vemos que tipo de trama es
                            result = self.tipoProcesado[t](raw)  # la mandamos a procesar
                            return result

                #else:  # la trama esta corrupta, leo otra
                #    STATUS = 0


#P = Parser()

#while True:
#    print(P.get_Trame())
