import RPi.GPIO as GPIO

class GPO():

    #these numbers are the order that outputs will be assigned from GPIO header
    gpio_gen = (17, 18, 27, 22, 23, 24, 25)
    
    def __init__(self, num=0):
        self.pin = self.gpio_gen[num]
        self.state = False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=self.state)

    def get_state(self):
        #return the current status of the gpo
        return self.state
        
    def toggle(self):
        #toggle state of gpo
        self.state = not self.state
        GPIO.output(self.pin, self.state)

    def cleanup(self):
        GPIO.cleanup()

    
        

    
