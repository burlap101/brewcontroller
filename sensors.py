import os, glob, time


class Sensors():

    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = {}
    sensorid = []

    def __init__(self):
        #os.system('modprobe w1-gpio')
        #os.system('modprobe w1-therm')
        for device_folder in glob.glob(self.base_dir + '28*'):
            self.sensorid.append(device_folder.split('/')[-1])
            self.device_file[self.sensorid[-1]] = device_folder + '/w1_slave'
        #print self.sensorid
        #print self.device_file
        

    def read_temp_raw(self, sensor):
        f = open(self.device_file[sensor], 'r')
        self.lines = f.readlines()
        f.close()
        

    def read_temp(self, sensor):
        self.read_temp_raw(sensor)
        while self.lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            self.read_temp_raw(sensor)
            print("Sensor CRC Fail")
        equals_pos = self.lines[1].find('t=')
        if equals_pos != -1:
            temp_string = self.lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            #temp_f = temp_c *9.0 / 5.0 + 32.0
            #return temp_c, temp_f
            return temp_c

    def get_ids(self):
        return self.sensorid

            
        
        
        
    
        
        

    
