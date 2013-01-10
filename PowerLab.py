#!/usr/bin/env python

import time

class PowerLab:
    def __init__(self, communication_object,charger_number=0):
        self.communication_object = communication_object
        self.charger_number = charger_number

    def SelP(self, preset_num):
        to_send_string = "SelP" + chr(preset_num)
        crc = self.communication_object.send_string_and_get_CRC(to_send_string)
        #TODO: calculate CRC
        return True

    def Sel(self, command_letter):
        command_letters = ['C','c','D','d','M','m','Y','y','E']
        if( command_letter in command_letters ):
            to_send_string = "Sel" + command_letter
            crc = self.communication_object.send_string_and_get_CRC(to_send_string)
            return(crc == 0x05DC)
        else:
            raise Exception("Invalid Command Letter %s" % command_letter)

    def start_something(self,uppercase_letter,with_bananas):
        status = self.get_status()
        if( status["mode"] == 0 ):
            if( self.Sel( uppercase_letter if with_bananas else uppercase_letter.lower() ) ):
                time.sleep(3.5)
                status = self.get_status()
                if( status["mode"] == 10 ):
                    return self.Sel('E')
                else:
                    return True
        return False

    def start_charge(self, with_bananas=False):
        return self.start_something('C',with_bananas)
        
    def start_discharge(self, with_bananas=False):
        return self.start_something('D',with_bananas)

    def start_monitor(self, with_bananas=False):
        return self.start_something('M',with_bananas)

    def start_cycling(self, with_bananas=False):
        return self.start_something('Y',with_bananas)
        
    def choose_preset( self, number ):
        if( type(number) == type(0) and number >= 0 and number <= 24 ):
            return self.SelP( number )
        else:
            raise Exception( "Invalid preset %d" % number )

    def stop(self):
        status = self.get_status()
        if( status["mode"] in [6,7,8,9,11] ):
            if( self.Sel('E') ):
                time.sleep(1)
                status = self.get_status()
                if( status["mode"] == 0 ):
                    return True
        return False

    def clear_error(self):
        status = self.get_status()
        if( status["mode"] == 99 ):
            if( self.Sel('E') ):
                time.sleep(1)
                status = self.get_status()
                if( status["mode"] == 0 ):
                    return True
        return False

    def get_status(self):
        ret = {}
        raw_byte_array = self.communication_object.send_string_and_get_bytes( "Ram"+chr(self.charger_number), 149 )

        def word( first_index ):
            return (raw_byte_array[first_index]<<8)+raw_byte_array[first_index+1]
        def dword( first_index ):
            return (word(first_index)<<16)+word(first_index+2)

        def sword( first_index ):
            ret = word(first_index)
            if( ret >= 32768 ):
                ret = ret - 65536
            return ret

        #TODO: calculate CRC

        ret["version"] = word(0)/100.0
        ret["cell_voltages"] = [ x * 5.12 / 65536 for x in [word(i*2+2) for i in range(0,8)] ]
        ret["pwm_drive"] = word(18)
        ret["charge_current_set_point"] = word(20)/1666.0
        ret["supply_volts_with_current"] = word(22)*46.96/4095/16
        ret["supply_volts"] = word(24)*46.96/4095
        ret["cpu_temperature"] = (word(26)*2.5/4095 - 0.986)/0.00355
        ret["dis_charge_seconds"] = word(28)
        ret["fast_amps_reading"] = sword(30)/600.0
        ret["output_positive_reading"] = word(32)*46.96/4095
        ret["mahr_into_battery"] = dword(34)/2160
        ret["average_cell_fuel"] = word(38)/10
        ret["start_fuel"] = word(40)/10
        ret["average_amps_reading"] = word(42)/600.0
        ret["status_flags"] = word(44) #TODO: more processing
        ret["RXstatus_flags"] = word(46)
        ret["status2_flags"] = word(48)
        ret["VRAmps"] = word(68)/600.0
        ret["maxcell_volts"] = word(74)/12797.0
        ret["status6_flags"] = word(76)
        ret["dis_charge_minutes"] = word(78)
        ret["supply_amps"] = word(80)/150.0
        ret["battery_positive_volts"] = word(82)/12797.0
        ret["mahr_out_of_battery"] = dword(84)/2160
        ret["regen_volt_set_point"] = word(90)*46.96/4095
        ret["discharge_set_amps"] = word(92)/600.0
        ret["internal_discharge_pwm"] = word(94)
        ret["negative_node_volt_drop"] = word(96)*46.96/4095
        ret["positive_node_volt_drop"] = word(98)*46.96/4095
        ret["battery_negative_volts"] = word(100)*46.96/4095
        ret["starting_supply_volts"] = word(104)*46.96/4095
        ret["VROffset"] = word(114)/6.3984
        ret["slow_average_amps"] = sword(116)/600.0
        ret["preset_set_charge_amps"] = word(118)/600.0
        ret["slaves_found"] = word(120)
        ret["balancer_pwms"] = [raw_byte_array[i] for i in range(124,131+1)]
        ret["detected_cell_count"] = raw_byte_array[132]
        ret["mode"] = raw_byte_array[133]
        ret["error_code"] = raw_byte_array[134]
        ret["chemistry"] = raw_byte_array[135]
        ret["loaded_preset"] = raw_byte_array[137]
        ret["screen_number"] = raw_byte_array[139]
        ret["cycle_number"] = raw_byte_array[142]
        ret["power_reduced_reason"] = raw_byte_array[143]
        
        ret["nicd_fallback_volts"] = word(70)/12797.0  - ret["maxcell_volts"]
        ret["cell_ir"] = [ ((x / 6.3984 - ret["VROffset"])/ret["VRAmps"]) if ret["VRAmps"] > 0 else 0 for x in [word(i*2+52) for i in range(0,8)] ]

        self.last_status = ret
        return ret

if __name__ == "__main__":
    global powerlab
    from PowerLab_Serial import PowerLab_Single_Serial
    communication = PowerLab_Single_Serial("/dev/ttyUSB0")
    powerlab = PowerLab(communication)

    gs = powerlab.get_status()
    print(gs)

    print("output_positive_reading is %.3f, sum of cell voltages is %.3f" % (gs["output_positive_reading"],sum(gs["cell_voltages"])))
    




