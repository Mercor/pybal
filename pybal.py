#!/usr/bin/python3

import quick2wire.i2c as i2c
import time

address = 0x6b
iodir_register=0x00
gpio_register=0x09

L3G_WHO_AM_I      = 0x0F

L3G_CTRL_REG1     = 0x20
L3G_CTRL_REG2     = 0x21
L3G_CTRL_REG3     = 0x22
L3G_CTRL_REG4     = 0x23
L3G_CTRL_REG5     = 0x24
L3G_REFERENCE     = 0x25
L3G_OUT_TEMP      = 0x26
L3G_STATUS_REG    = 0x27

L3G_OUT_X_L       = 0x28
L3G_OUT_X_H       = 0x29
L3G_OUT_Y_L       = 0x2A
L3G_OUT_Y_H       = 0x2B
L3G_OUT_Z_L       = 0x2C
L3G_OUT_Z_H       = 0x2D

L3G_FIFO_CTRL_REG = 0x2E
L3G_FIFO_SRC_REG  = 0x2F

L3G_INT1_CFG      = 0x30
L3G_INT1_SRC      = 0x31
L3G_INT1_THS_XH   = 0x32
L3G_INT1_THS_XL   = 0x33
L3G_INT1_THS_YH   = 0x34
L3G_INT1_THS_YL   = 0x35
L3G_INT1_THS_ZH   = 0x36
L3G_INT1_THS_ZL   = 0x37
L3G_INT1_DURATION = 0x38


def write_register(bus, reg, b):
    bus.transaction(
        i2c.writing_bytes(address, reg, b))
    
def read_register(bus, reg):
    return bus.transaction(
        i2c.writing_bytes(address, reg),
        i2c.reading(address, 1))[0][0]

def twos_comp(val, bits):
    # compute the 2's compliment of int value val
    if( (val&(1<<(bits-1))) != 0 ):
        val = val - (1<<bits)
    return val
    
with i2c.I2CMaster() as bus:
    print("initializing gyro")
    write_register(bus,  L3G_CTRL_REG1, 0x0F)
    
    who_am_i = read_register(bus, L3G_WHO_AM_I)
    print("%02x" % who_am_i)
    
    print("getting coords...")
	
    while 1 : 
        xlow, xhigh, ylow, yhigh, zlow, zhigh = bus.transaction(
        i2c.writing_bytes(address, L3G_OUT_X_L | (1 << 7)),
        i2c.reading(address, 6))[0]
        
        x = twos_comp((xhigh << 8 | xlow), 16)
        y = twos_comp((yhigh << 8 | ylow), 16)
        z = twos_comp((zhigh << 8 | zlow), 16)
        
        xsum += x
        ysum += y
        zsum += z
        
#        print("XL:%02x XH:%02x YL:%02x YH:%02x ZL:%02x ZH:%02x x %5i y %5i z %5i " % ( xlow, yhigh, ylow,yhigh, zlow, zhigh, x, y, z))
        print("x %5i y %5i z %5i xsum %4i ysum %4i zsum %4i" % ( x, y, z, xsum, ysum, zsum))
        
        # print("XH:", bin(xhigh)[2:])
        # print("YL:", bin(ylow)[2:])
        # print("yH:", bin(yhigh)[2:])
        # print("zL:", bin(zlow)[2:])
        # print("zH:", bin(zhigh)[2:])
        
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
    # while True:
        # results = bus.transaction(
            # i2c.write_bytes(address, gpio_register),
            # i2c.read(address, 1))

        # gpio_state = results[0][0]

        # print(gpio_state)

        # time.sleep(1)



