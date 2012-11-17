#!/usr/bin/python3

import quick2wire.i2c as i2c
import time
import math

address = 0x6b



address_acc = 0x19



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


LSM303_CTRL_REG1_A       = 0x20
LSM303_CTRL_REG2_A       = 0x21
LSM303_CTRL_REG3_A       = 0x22
LSM303_CTRL_REG4_A       = 0x23
LSM303_CTRL_REG5_A       = 0x24
LSM303_CTRL_REG6_A       = 0x25 
LSM303_HP_FILTER_RESET_A = 0x25 
LSM303_REFERENCE_A       = 0x26
LSM303_STATUS_REG_A      = 0x27
                         
LSM303_OUT_X_L_A         = 0x28
LSM303_OUT_X_H_A         = 0x29
LSM303_OUT_Y_L_A         = 0x2A
LSM303_OUT_Y_H_A         = 0x2B
LSM303_OUT_Z_L_A         = 0x2C
LSM303_OUT_Z_H_A         = 0x2D

LSM303_FIFO_CTRL_REG_A   = 0x2E 
LSM303_FIFO_SRC_REG_A    = 0x2F 

LSM303_INT1_CFG_A        = 0x30
LSM303_INT1_SRC_A        = 0x31
LSM303_INT1_THS_A        = 0x32
LSM303_INT1_DURATION_A   = 0x33
LSM303_INT2_CFG_A        = 0x34
LSM303_INT2_SRC_A        = 0x35
LSM303_INT2_THS_A        = 0x36
LSM303_INT2_DURATION_A   = 0x37

LSM303_CLICK_CFG_A       = 0x38 
LSM303_CLICK_SRC_A       = 0x39 
LSM303_CLICK_THS_A       = 0x3A 
LSM303_TIME_LIMIT_A      = 0x3B 
LSM303_TIME_LATENCY_A    = 0x3C 
LSM303_TIME_WINDOW_A     = 0x3D 
                          
LSM303_CRA_REG_M         = 0x00
LSM303_CRB_REG_M         = 0x01
LSM303_MR_REG_M          = 0x02
 
LSM303_OUT_X_H_M         = 0x03
LSM303_OUT_X_L_M         = 0x04
LSM303_OUT_Y_H_M         = -1   
LSM303_OUT_Y_L_M         = -2   
LSM303_OUT_Z_H_M         = -3   
LSM303_OUT_Z_L_M         = -4   
                          
LSM303_SR_REG_M          = 0x09
LSM303_IRA_REG_M         = 0x0A
LSM303_IRB_REG_M         = 0x0B
LSM303_IRC_REG_M         = 0x0C
                          
LSM303_WHO_AM_I_M        = 0x0F 
                          
LSM303_TEMP_OUT_H_M      = 0x31 
LSM303_TEMP_OUT_L_M      = 0x32 
                          
LSM303DLH_OUT_Y_H_M      = 0x05
LSM303DLH_OUT_Y_L_M      = 0x06
LSM303DLH_OUT_Z_H_M      = 0x07
LSM303DLH_OUT_Z_L_M      = 0x08
                          
LSM303DLM_OUT_Z_H_M      = 0x05
LSM303DLM_OUT_Z_L_M      = 0x06
LSM303DLM_OUT_Y_H_M      = 0x07
LSM303DLM_OUT_Y_L_M      = 0x08
                          
LSM303DLHC_OUT_Z_H_M     = 0x05
LSM303DLHC_OUT_Z_L_M     = 0x06
LSM303DLHC_OUT_Y_H_M     = 0x07
LSM303DLHC_OUT_Y_L_M     = 0x08


def write_register(bus, address, reg, b):
    bus.transaction(
        i2c.writing_bytes(address, reg, b))
    
def read_register(bus, address, reg):
    return bus.transaction(
        i2c.writing_bytes(address, reg),
        i2c.reading(address, 1))[0][0]

def twos_comp(val, bits):
    # compute the 2's compliment of int value val
    if( (val&(1<<(bits-1))) != 0 ):
        val = val  - (1<<bits)
    return val
    
with i2c.I2CMaster() as bus:
    print("initializing gyro")
    write_register(bus, address, L3G_CTRL_REG1, 0x0F)
    
    who_am_i = read_register(bus, address, L3G_WHO_AM_I)
    print("%02x" % who_am_i)

    print("initializing acc")
    # Enable Accelerometer
    # 0x27 = 0b00100111
    # Normal power mode, all axes enabled, 10Hz
    write_register(bus, address_acc, LSM303_CTRL_REG1_A, 0x27)
    
    print("getting data...")

    xsum = 0
    ysum = 0
    zsum = 0	
    
    ignore = 400
    
    while 1 : 
        xlow, xhigh, ylow, yhigh, zlow, zhigh = bus.transaction(
        i2c.writing_bytes(address, L3G_OUT_X_L | (1 << 7)),
        i2c.reading(address, 6))[0]
        
        x = twos_comp((xhigh << 8 | xlow), 16)
        y = twos_comp((yhigh << 8 | ylow), 16)
        z = twos_comp((zhigh << 8 | zlow), 16)
        
        
        if(abs(x)>ignore) : xsum += x
        if(abs(y)>ignore) : ysum += y
        if(abs(z)>ignore) : zsum += z
        
        wx = (180 / 0x7fff) * x
        
        
        xalow, xahigh, yalow, yahigh, zalow, zahigh = bus.transaction(
        i2c.writing_bytes(address_acc, LSM303_OUT_X_L_A | (1 << 7)),
        i2c.reading(address_acc, 6))[0]
        
        xa = float(twos_comp((xahigh << 8 | xalow) , 16))
        ya = float(twos_comp((yahigh << 8 | yalow) , 16))
        za = float(twos_comp((zahigh << 8 | zalow) , 16))
        
        xa2 = xa * xa
        ya2 = ya * ya
        za2 = za * za
        
        #X Axis
        result=math.sqrt(ya2+za2);
        result=xa/result*10;
#        print("result %f" % (result))
        accel_angle_x = math.atan(result);

        #Y Axis
        result=math.sqrt(xa2+za2);
        result=ya/result;
        accel_angle_y = math.atan(result);
        
        winkel_x = xa/0x7fff*180.0 #*za/abs(za)
        
        togo = math.sin(math.radians(winkel_x)) * 10
        
#        print("XL:%02x XH:%02x YL:%02x YH:%02x ZL:%02x ZH:%02x x %5i y %5i z %5i " % ( xlow, yhigh, ylow,yhigh, zlow, zhigh, x, y, z))
#        print("x %5i y %5i z %5i xsum %4i ysum %4i zsum %4i wx %3.2i xa %5i ya %5i za %5i Winkel X %3i" % ( x, y, z, xsum, ysum, zsum, wx, xa, ya, za, accel_angle_x))
        print("xa %5i ya %5i za %5i Winkel X %f togo %f" % ( xa, ya, za, winkel_x, togo  ))
        
        # print("XH:", bin(xhigh)[2:])
        # print("YL:", bin(ylow)[2:])
        # print("yH:", bin(yhigh)[2:])
        # print("zL:", bin(zlow)[2:])
        # print("zH:", bin(zhigh)[2:])
        


        # time.sleep(1)



