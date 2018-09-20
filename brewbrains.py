"""
The brains of the controller. This handles all GPIO and redirects it as needed, as well as
logging and in hte future email reporting.
"""

import time
from datetime import datetime
import sensors
import gpo
import threading
import numpy
from queue import Queue
import csv
import smtplib



class BrewBrains(object):

    setpoints = []
    samples = 0
    logfile = ''
    log_period = 120     #logging interval in seconds (approx)
    temp_c = {}
    end_threads = False
    temp_thread = {}
    gpo = []
    tempq = {} # a dictionary of queues to communicate between temp reading and logging
    #gpoc = False
    sensorlist = []
    control_sensor = []
    email_toaddr = []
    ereporting_flag = False
    new_logfile = True

    def __init__(self, gpo_count=2):
        self.sensors = sensors.Sensors()
        self.sensorlist = self.sensors.get_ids() #after initialisation then sensor can't be added until restart
        self.set_threads()
        self.gpo_count = gpo_count       #max number of gpos is 7 atm

        #create separate instances of GPO. Not sure if this is the right thing to do....
        for gpo_num in range(self.gpo_count):
            self.gpo.append(gpo.GPO(gpo_num))
            self.control_sensor.append(None)
            self.setpoints.append({})
            self.setpoints[gpo_num]['temp_on'] = 15.0
            self.setpoints[gpo_num]['temp_off'] = 21.0
          
    def set_threads(self):
        for sensor in self.sensorlist:
            self.tempq[sensor] = Queue()
            self.temp_thread[sensor] = threading.Thread(target = self.read_temp,
                                                        name = sensor, args = (sensor,))
            self.temp_thread[sensor].start()
            
            self.temp_c[sensor] = None
        print(threading.enumerate())

    def get_sensors(self):
        return self.sensorlist

    def set_sensor(self, gpo, sensor):
        if sensor in self.sensorlist:
            self.control_sensor[gpo] = sensor
            print("Sensor " + sensor + " in control of gpo #%d now" %(gpo+1))
        else:
            self.control_sensor[gpo] = None
            print("Manual control only of gpo#%d now" %(gpo+1))
      
    def get_setpoints(self, gpo):
        return self.setpoints[gpo]['temp_off'], self.setpoints[gpo]['temp_on']
    
    def set_setpoints(self, temp_off, temp_on):
        self.change_setpoints(temp_off, temp_on)

    def set_logfile(self, filename, newlog=True):
        self.logfile = filename
        self.new_logfile = newlog

    def get_logfile(self):
        return self.logfile

    def config_email_reports(self, *emailadds):
        temp_addr= []
        for addr in emailadds:
            print(addr)
            if addr.find('@') and addr.find('.com') > 0:
                temp_addr.append(addr)
            else:
                print("Invalid email address entered")
                break
        else:
            self.email_toaddr = temp_addr[:]
            if not self.ereporting_flag:
                self.ereport_thread = threading.Timer(30.0, self.email_report)
                self.ereport_thread.start()
                self.ereporting_flag = True
                        
    def email_reports_config(self):
        return self.email_toaddr
            

    def get_samples(self):
        return self.samples

    def get_temp(self, sensor = None):
        #returns a list of all sensor temps if no ID specified
        if sensor == None:
            return list(self.temp_c.values())
        else:
            return self.temp_c[sensor]
        
    def get_log_period(self):
        return self.log_period

    def set_log_period(self, period):
        self.log_period = period
        

    def get_gpo_state(self, gpo_num = 0):
        return self.gpo[gpo_num].get_state()

    def get_gpo_count(self):
        return self.gpo_count

    def toggle_gpo(self, gpo_num):
        self.gpo[gpo_num].toggle()

    def email_report(self):
        #still need to do a lot of work here. need to figure out what i want.
        print("Yep done")
        self.ereport_thread = threading.Timer(30.0, self.email_report)
        self.ereport_thread.start()
        
    def read_temp(self, sensor):
        "This method is intended to be run by a separate thread for each sensor"
        #self.sensors = sensors.Sensors()
        while not self.end_threads:
            self.temp_c[sensor] = self.sensors.read_temp(sensor)
            self.tempq[sensor].put(self.temp_c[sensor])

            
            for gpo_num in range(self.gpo_count):
                if sensor == self.control_sensor[gpo_num]:
                    self.setpoint_toggle(gpo_num)

    def setpoint_toggle(self, gpo_num):
        """
        This method is for determining the need to toggle a GPO
        based on current state and temperature, then carries it out
        """
        if self.setpoints[gpo_num]['temp_on'] < self.setpoints[gpo_num]['temp_off']:
            #this condition for controlling heating situation
            if self.temp_c[self.control_sensor[gpo_num]] > self.setpoints[gpo_num]['temp_off'] and self.gpo[gpo_num].get_state():
                self.gpo[gpo_num].toggle()
            elif self.temp_c[self.control_sensor[gpo_num]] < self.setpoints[gpo_num]['temp_on'] and not self.gpo[gpo_num].get_state():
                self.gpo[gpo_num].toggle()

        elif self.setpoints[gpo_num]['temp_on'] > self.setpoints[gpo_num]['temp_off']:
            #this condition for controlling cooling situation
            if self.temp_c[self.control_sensor[gpo_num]] < self.setpoints[gpo_num]['temp_off'] and self.gpo[gpo_num].get_state():
                self.gpo[gpo_num].toggle()
            elif self.temp_c[self.control_sensor[gpo_num]] > self.setpoints[gpo_num]['temp_on'] and not self.gpo[gpo_num].get_state():
                self.gpo[gpo_num].toggle()
        
    def log_temp(self):
        "this method uses the temp queues for each sensor thread and outputs results to a file"
        
        if self.new_logfile:
            with open(self.logfile, 'w') as f:
                titlerow = ["Sensor ID", "DateTime", "Temp", "Avg", "Min", "Max"]
                for gpo_num in range(self.gpo_count):
                    titlerow.append("GPO#%d" %(gpo_num+1))
                csv_writer = csv.writer(f)
                csv_writer.writerow(titlerow)
                self.new_logfile = False
        
        while not self.end_threads:
            for i in range(self.log_period):
                if self.end_threads:
                    break
                time.sleep(1)
                
            with open(self.logfile, 'a') as f:
                #print f.tell()
                csv_writer = csv.writer(f)
                for sensor in self.sensorlist:
                    temp_list = []
                    while not self.tempq[sensor].empty():
                        temp_list.append(self.tempq[sensor].get())
                        self.tempq[sensor].task_done()

                    if temp_list:
                        row = [sensor, datetime.now(),temp_list[-1], "%.3f" %numpy.average(temp_list),
                               min(temp_list), max(temp_list)]
                        
                        for gpo_num in range(self.gpo_count):
                            row.append("ON" if self.gpo[gpo_num].get_state() else "OFF")
                        csv_writer.writerow(row)
            
            
    def toggle_logging(self):
        try:
            if self.log_thread.is_alive():
                self.log_thread.join()
            else:
                self.log_thread.start()
                
        except:            
            self.log_thread = threading.Thread(target = self.log_temp,
                                                       name = "log_thread")
            self.log_thread.start()

    def change_setpoints(self, gpo, temp_off, temp_on):
        self.setpoints[gpo]['temp_off'] = temp_off
        self.setpoints[gpo]['temp_on'] = temp_on

    def cleanup(self):
        "Join threads and queues and cleanup GPIO"
        print(threading.enumerate())
        self.end_threads = True

        try:
            self.log_thread.join()
        except:
            print("No log thread created")
            
        for sensor in self.sensorlist:
            while not self.tempq[sensor].empty():
                self.tempq[sensor].get()
                self.tempq[sensor].task_done()
            self.tempq[sensor].join()
            self.temp_thread[sensor].join()
        print(threading.enumerate())
        if self.ereporting_flag:
            self.ereport_thread.cancel()
        self.gpo[0].cleanup()       # will cleanup all GPIO no need to recall for each output (was getting a warning message)
