#!/usr/bin/env python

import serial,time

class PowerLab_Single_Serial:
    def __init__( self, serial_port_filename ):
        self.filename = serial_port_filename
        self.open()

    def send_string_and_get_CRC(self, some_string):
        result = self.send_string_and_get_bytes(some_string,2)
        return (result[0]<<8)+result[1]

    def send_string_and_get_bytes(self, some_string, number_bytes):
        try:
            self.ser.flushInput()
            self.ser.write(some_string)
            self.ser.flush()
            s_ret = self.ser.read(number_bytes+len(some_string))
            # s_ret = ''
            # while( len(s_ret) < number_bytes ):
            #     s_ret = s_ret + self.ser.read(number_bytes)
        except OSError, e:
            print "Serial port disappeared!"
            self.ser.close()
            self.open()
            return self.send_string_and_get_bytes(some_string, number_bytes)
        ret_list = [ord(x) for x in s_ret]
        for i in range(0, len(some_string)):
            del ret_list[0]
        return ret_list
        

    def open(self):
        while(1):
            try:
                self.ser = serial.Serial(self.filename, 19200, timeout=.2)
                break
            except serial.serialutil.SerialException, e:
                print "Open serial error is " + str(e)
                time.sleep(1)

    def close(self):
        self.ser.close()
