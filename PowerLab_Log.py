#!/usr/bin/env python

import time

class PowerLab_Log:
    def __init__(self, log_filename, log_type="simple"):
        self.file = open(log_filename,'w')
        self.log_type = log_type
        if( log_type == "simple" ):
            self.headers = ["time","machine ID","Cell1V","Cell2V","Cell3V","Cell4V","Cell5V","Cell6V","Cell7V","Cell8V","supply_volts","mAHr_into_battery","mAHr_out_battery","status_flags","mode","BatteryV","fast_amps","power_limit","error_code"]
            self.file.write(",".join(self.headers) + '\n')

    def log(self,machine_name,status):
        if( self.log_type == "simple" ):
            write = [time.time(),machine_name]
            for each in status["cell_voltages"]:
                write.append("%.3f" % each)
            write.append("%.2f" % (status["supply_volts"]))
            for each in ["mahr_into_battery","mahr_out_of_battery"]:
                write.append(status[each])
            for each in ["status_flags","mode"]:
                write.append("0x%X"%(status[each]))
            write.append("%.3f" % (status["output_positive_reading"]))
            for each in ["fast_amps_reading","power_reduced_reason","error_code"]:
                write.append(status[each])
            self.file.write(",".join([str(x).replace(',','\\x2C') for x in write]).replace('\n','\\n') + '\n')
        elif( self.log_type == "raw" ):
            self.file.write(str(status).replace('\n','\\n')+"\n")
        self.file.flush()
        


if __name__ == "__main__":
    from PowerLab_Serial import PowerLab_Single_Serial
    from PowerLab import PowerLab
    communication = PowerLab_Single_Serial("/dev/ttyUSB0")
    powerlab = PowerLab(communication)
    log = PowerLab_Log( "test_log.csv" )

    while 1:
        time.sleep( 1 )
        try:
                log.log( "test", powerlab.get_status() )
        except Exception, e:
                print e


