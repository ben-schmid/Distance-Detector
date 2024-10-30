import RPi.GPIO as GPIO
import time
import datetime
import threading
from gpiozero import RGBLED
from colorzero import Color


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIGGER_PIN = 18
ECHO_PIN = 17
FREQ = 60
HIGH_TIME=0.1
LOW_TIME=1-HIGH_TIME
SPEED_OF_SOUND=330/float(1000000)

GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

led = RGBLED(26, 19, 13) #initalize RGB LED, numbers are GPIO pins where the LED is connected to



#helper function for get_measurement
def getDistance(td):
	distance=SPEED_OF_SOUND*td/float(2)
	return distance


#function to return the measured distance to activate the motor
def measure_distance():
    while True:
        GPIO.output(TRIGGER_PIN,GPIO.HIGH)
    #	print 'Trigger HIGH'
        time.sleep(HIGH_TIME)
        GPIO.output(TRIGGER_PIN,GPIO.LOW)
    #	print 'Trigger LOW'



        while GPIO.input(ECHO_PIN)==False:
    # pulse is LOW
            pass


        starttime = datetime.datetime.now().microsecond
        while GPIO.input(ECHO_PIN)==True:
    # pulse is HIGH
            pass

    # pulse is LOW
        endtime = datetime.datetime.now().microsecond
        travel_time=endtime - starttime
        time.sleep(LOW_TIME)
        
        if (getDistance(travel_time)) >= 0.02 and (getDistance(travel_time)) <= 4.0: 
            #dont return if range is wrong
            return (getDistance(travel_time))

#initialize global variabel run to true
run = True

# Main driver thread
def main_thread():
    print("Please move to the sweet spot")
    print()
    print()
    print("Green means move forward")
    print("Yellow means slow down")
    print("Red means stop! You are in the sweet spot")
    print("Blinking blue means reverse!")
    print("Type 'stop' to stop the program")
    while (run):
        distance = measure_distance()
        print(distance)
        if distance > .2 and distance < .3:
            #approaching sweet spot, slow down, change color yellow
            led.color = Color("yellow")
        elif distance >= .3:
            # move forward to approach sweet spot, LED color green
            led.color = Color("green")
        elif distance < 0.15:
            #too far foward, move back
            # Call blink function to have LED blink blue when too far forward
            led.blink(
                on_time=0.2, off_time=0.2, 
                fade_in_time=0, fade_out_time=0, 
                on_color=Color("blue"), off_color=(0,0,0), 
                n=2, background=True)
        else:
            #STOP, user in the sweet spot, change LED to red
            led.color = Color("red")

#Exit thread to catch the stop command
def exit_thread():
    global run
    while (run):
        stop_command = input("")
        if stop_command.upper() == 'STOP':
            run = False #stops the main while loop in the main thread


program_thread = threading.Thread(target=main_thread)
input_thread = threading.Thread(target=exit_thread)

#try block to catch keyboard interrupt
try:
    program_thread.start()
    input_thread.start()

    # Wait for the input thread to finish
    input_thread.join()

    # After the input thread ends, wait for the program loop thread to finish
    program_thread.join()
except KeyboardInterrupt:
    run = False #stops the main while loop in the main thread
    program_thread.join()
    input_thread.join()
    print("Exiting program.")

print("Program Stopped")
led.close() #close LED, this function calls GPIO.cleanup on LED pins
GPIO.cleanup([TRIGGER_PIN, ECHO_PIN]) # clean ULTRASOUND pins

