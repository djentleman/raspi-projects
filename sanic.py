import time
## rpi drivers for sonic the hedgehog - sega megadrive
## using the dgen emulator

## uinput used for simulated key presses

import os
import RPi.GPIO as GPIO
import uinput
import math

device = uinput.Device([uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_SPACE])
 
GPIO.setmode(GPIO.BCM)
DEBUG = 1
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
 
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18 # clock pin
SPIMISO = 23 # digital in
SPIMOSI = 24 # digital out
SPICS = 25 # control?
ABUTTON = 4 # GND
BBUTTON = 17 # 3V3
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(ABUTTON, GPIO.IN)
GPIO.setup(BBUTTON, GPIO.IN)
 
# 10k trim pot connected to adc #0
potentiometer_adc = 0; 
 
last_read = 0       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'
leftLim = 0
rightLim = 0 

currentCycle = 0

while True:
	currentCycle += 1
        # we'll assume that the pot didn't move
        trim_pot_changed = False
 
        # read the analog pin
        horz = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)
        vert = readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS)
	button = readadc(2, SPICLK, SPIMOSI, SPIMISO, SPICS)
	"""
	print vert
	print horz
	print button
	time.sleep(0.2)
	continue
	"""
	# how much has it changed since the last read?
        pot_adjust = abs(horz - last_read)
 
        if 0:
                print "horz:",bin(horz)
              #  print "pot_adjust:", pot_adjust
              #  print "last_read", last_read
 
        if ( pot_adjust > tolerance ):
               trim_pot_changed = True
 
        if 0:
                print "trim_pot_changed", trim_pot_changed

	last_read = horz
	
	if (GPIO.input(BBUTTON)):
		device.emit_click(uinput.KEY_SPACE)
	
		
	
	horzVal = horz + 1
	
	if abs(512 - horz) < 50:
		x = "xxx nigga tripple x rated"
	
	elif horz >= 512:
		# turn right
		rightVal = abs(horzVal - 1025)
		rightLim = math.log(rightVal, 2) + 1
		if (currentCycle % int((rightLim / 2) + 1)) == 0:
			device.emit_click(uinput.KEY_RIGHT)

	else:
		# turn left
		leftLim = math.log(horzVal, 2) + 1
		if (currentCycle % int((leftLim / 2) + 1)) == 0:
			device.emit_click(uinput.KEY_LEFT)

		
	time.sleep(0.03) # 30ms between cycles	
