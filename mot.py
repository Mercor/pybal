#!/usr/bin/python3
import sys
from time import sleep
from quick2wire.gpio import Pin
import quick2wire.i2c as i2c
import time
import math

class ji2c :

  def __init__(self, address, debug=False):
    self.bus = i2c.I2CMaster()
    self.address = address
    self.debug = debug
    if (self.debug):
      print("init ji2c")

  def write(self, reg, b):
      if (self.debug):
        print("ji2c write %x to reg %d" % (b, reg))
      self.bus.transaction(
          i2c.writing_bytes(self.address, reg, b))
    
  def read(self, reg):
      return self.bus.transaction(
          i2c.writing_bytes(self.address, reg),
          i2c.reading(self.address, 1))[0][0]
      

class PWM :
  bus = None

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = ji2c(address, False)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.bus.write(self.__MODE1, 0x00)
 


  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print( "Setting PWM frequency to %d Hz" % freq)
      print( "Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.bus.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10             # sleep
    self.bus.write(self.__MODE1, newmode)        # go to sleep
    self.bus.write(self.__PRESCALE, int(math.floor(prescale)))
    self.bus.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.bus.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.bus.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.bus.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.bus.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.bus.write(self.__LED0_OFF_H+4*channel, off >> 8)


# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 1600  # Max pulse length out of 4096

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print( "%d us per period" % pulseLength)
  pulseLength /= 4096                     # 12 bits of resolution
  print( "%d us per bit" % pulseLength)
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)








pin23= Pin(16, Pin.Out, pull=Pin.PullUp)
pin22= Pin(15, Pin.Out, pull=Pin.PullDown)

pin23.value=1
pin22.value=0

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
try:
  while (True):
    # Change speed of continuous servo on channel O
    pwm.setPWM(0, 0, servoMin)
   # pwm.setPWM(15, 0, servoMin)
    time.sleep(1)
    pwm.setPWM(0, 0, servoMax)
    #pwm.setPWM(15, 0, servoMax)
    time.sleep(1)
    pin23.value=1-pin23.value
    pin22.value=1-pin22.value
except KeyboardInterrupt:
    print("Stopping motor")
    pwm.setPWM(0, 0, 0)
    print("unexporting pins")
    pin23.unexport()
    pin22.unexport()


##pin = Pin(int(sys.argv[1]) if len(sys.argv) > 1 else 12, Pin.Out)
##
##
##try:
##    pin.value = 1
##    while True:
##        sleep(1)
##        pin.value = 1 - pin.value
##except KeyboardInterrupt:
##    pin.value = 0
##    pin.unexport()

