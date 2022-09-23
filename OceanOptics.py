#ADC1000USB and USB4000 Ocean Optics USB driver
#Copyright (C) 2015  Emanuele Centurioni
#E-mail: centurioni@bo.imm.cnr.it

import time
import usb.core
from threading import Thread
from numpy import *

class ADC1000USB:
    def __init__(self,int_time=3,avg=25,boxcar=2,run=False,lock=False):
        self.usb = usb.core.find(idVendor=0x2457, idProduct=0x1004)
        self.usb.write(0x02,chr(0x01))#Initialize Spectrometer and acquire a spectrum
        self.int_time=int_time#milliseconds
        self.last_int_time=0
        self.avg=avg#number of averages
        self.boxcar=boxcar
        self.run=run
        self.lock=lock
        self.counts=[]#resolution reduced spectra (using boxcar)
        self.master=channel(self,wave_cal=[],reg=[2,3,4,5],ch=0,low_cut=200)
        self.master.readspectra()#after initialization a spectra must be read
        self.slave=channel(self,wave_cal=[],reg=[6,7,8,9],ch=1,high_cut=1100)
        self.int_time_min=3#ms
        self.int_time_max=65535#ms
        self.transition_cut=680# wavelenght cut between master and slave (nm)
        self.maxcount=4096
    def set_int_time(self):#int time is in milliseconds on ADC1000USB
        MSB,LSB=HiLow(self.int_time)
        self.usb.write(0x02,chr(0x02)+chr(LSB)+chr(MSB))
    def getspectra(self):
        if self.last_int_time <> self.int_time:
            self.set_int_time()
            self.last_int_time = self.int_time
        self.master.getspectra()
        self.slave.getspectra()
        self.lock=True
        del self.counts[:]
        for c in self.master.counts:
            if c[0] <= self.transition_cut:self.counts.append(c)
        for c in self.slave.counts:
            if c[0] > self.transition_cut:self.counts.append(c)
        self.lock=False
    def QueryInformation(self):
        for i in range(10):
            self.usb.write(0x02,chr(0x05)+chr(i))
            ret = self.usb.read(0x87,64)
            string=""
            for r in ret[2:]:
                string=string+chr(r)
            print i,string

class channel():
    def __init__(self,parent,wave_cal=[],reg=[],ch=0,low_cut=0,high_cut=2000):
        self.parent=parent
        self.data=[]#buffer used for averaging spectra
        self.spectra=[]#averaged spectra
        self.counts=[]#resolution reduced spectra (boxcar)
        self.wave_cal=wave_cal#wave calibration data
        self.ch=ch
        self.reg=reg#registers with calibration data
        self.low_cut=low_cut
        self.high_cut=high_cut
        self.ReadCalibration()
    def ReadCalibration(self):
        del self.wave_cal[:]
        for i in self.reg:
            self.parent.usb.write(0x02,chr(0x05)+chr(i))
            ret = self.parent.usb.read(0x87,64)
            string=""
            for r in ret[2:]:
                if r <> 0: string=string+chr(r)
            self.wave_cal.append(float(string))
    def requestspectra(self):
        self.parent.usb.write(0x02,chr(0x0B)+chr(self.ch)+chr(0))#select channel
        try:
            self.parent.usb.write(0x02,chr(0x09))#+chr(1))#+chr(i)
        except:
            print "request except"
            self.readspectra()
            self.parent.usb.write(0x02,chr(0x09))
    def readspectra(self):
        s=[]
        for j in range(0,64,2):
            LSB=self.parent.usb.read(0x82,64)
            MSB=self.parent.usb.read(0x82,64)
            for i in range(64):
                s.append(MSB[i]*256+LSB[i])
        a=self.parent.usb.read(0x82,64)
        return s
    def getspectra(self):
        self.requestspectra()
        try:
            time.sleep(self.parent.int_time/1000.0)#per tempi di integrazione lunghi non risponde subito
            s=self.readspectra()
            self.data.append(array(s))
            self.data=self.data[-self.parent.avg:]
        except:
            print "not ready"
            print self.ch
        del self.spectra[:]
        a=self.data[0]+0
        for d in self.data[1:]:
            a=a+d
        a=1.0*a/len(self.data)
        edark=0.0
        for c in a[:23]:
            edark=edark+c
        edark=edark/23.0
        a=a-edark#subctract electrical dark
        for i in range(len(a)):
            w=self.wave_cal[0]+self.wave_cal[1]*(i)+self.wave_cal[2]*(i)**2+self.wave_cal[3]*(i)**3
            if self.low_cut <= w <= self.high_cut:self.spectra.append([w,a[i]])
        self.red_res()
    def red_res_and_cut(self):#reduce resolution and number of points using boxcar
        del self.counts[:]
        k=len(self.spectra)/(self.parent.boxcar*2+1)
        #T=T[:k*(r*2+1)]
        for i in range(self.parent.boxcar,len(self.spectra[:k*(self.parent.boxcar*2+1)]),self.parent.boxcar*2+1):
            s=0.0
            for j in range(i-self.parent.boxcar,i+self.parent.boxcar+1):
                s=s+self.spectra[j][1]
            self.counts.append([self.spectra[i][0],s/(self.parent.boxcar*2+1)])
    def red_res(self):#reduce resolution keeping all the points using boxcar
        del self.counts[:]
        for i in range(len(self.spectra)):
            s=0.0
            for j in range(i-self.parent.boxcar,i+self.parent.boxcar+1):
                try:s=s+self.spectra[j][1]
                except:pass
            self.counts.append([self.spectra[i][0],s/(self.parent.boxcar*2+1)])

class USB4000:
    def __init__(self,int_time=20,avg=4,boxcar=5,run=False,lock=False,wave_cal=[]):
        self.usb = usb.core.find(idVendor=0x2457, idProduct=0x1022)
        self.usb.write(0x01,chr(0x01))#Initialize Spectrometer
        self.int_time=int_time#milliseconds
        self.last_int_time=0
        self.avg=avg#number of averages
        self.boxcar=boxcar
        self.data=[]#buffer used for averaging spectra
        self.run=run
        self.lock=lock
        self.spectra=[]#averaged spectra
        self.counts=[]#resolution reduced spectra (boxcar)
        self.wave_cal=wave_cal#wave calibration data
        self.int_time_min=1#ms
        self.int_time_max=65535#ms
        self.low_cut=200
        self.high_cut=1000
        self.maxcount=32768
        self.ReadCalibration()#read wave calibration data from spectrometer's EEPROM
    def set_int_time(self):#int time is in microseconds on USB4000
        MSW=self.int_time*1000/65536
        LSW=self.int_time*1000-65536*MSW
        LSW_MSB,LSW_LSB=HiLow(LSW)
        MSW_MSB,MSW_LSB=HiLow(MSW)
        self.usb.write(0x01,chr(0x02)+chr(LSW_LSB)+chr(LSW_MSB)+chr(MSW_LSB)+chr(MSW_MSB))
    def getspectra(self):
        if self.last_int_time <> self.int_time:
            self.set_int_time()
            self.last_int_time = self.int_time
        self.requestspectra()
        try:
            s=self.readspectra()
            self.data.append(array(s))
            self.data=self.data[-self.avg:]
        except:
            print "not ready"
        self.lock=True
        del self.spectra[:]
        a=self.data[0]+0
        for d in self.data[1:]:
            a=a+d
        a=1.0*a/len(self.data)
        edark=0.0
        for c in a[5:18]:
            edark=edark+c
        edark=edark/13.0
        #a=a[21:3668]-edark#active pixels
        a=a[:3668]-edark
        for i in range(len(a)):
            w=self.wave_cal[0]+self.wave_cal[1]*(i)+self.wave_cal[2]*(i)**2+self.wave_cal[3]*(i)**3
            if self.low_cut <= w <= self.high_cut:self.spectra.append([w,a[i]])
        self.red_res()        
        self.lock=False
    def requestspectra(self):
        try:
            self.usb.write(0x01,chr(0x09))
        except:
            print "request except"
            self.readspectra()
            self.usb.write(0x01,chr(0x09))
    def readspectra(self):
        s=[]
        for i in range(4):
            ret = self.usb.read(0x86,512)
            for j in range(0,512,2):
                s.append(ret[j]+ret[j+1]*256)
        for i in range(11):
            ret = self.usb.read(0x82,512)
            for j in range(0,512,2):
                s.append(ret[j]+ret[j+1]*256)
        ret = self.usb.read(0x82,512)
        return(s)
    def red_res(self):
        del self.counts[:]
        k=len(self.spectra)/(self.boxcar*2+1)
        for i in range(self.boxcar,len(self.spectra[:k*(self.boxcar*2+1)]),self.boxcar*2+1):
            s=0.0
            for j in range(i-self.boxcar,i+self.boxcar+1):
                s=s+self.spectra[j][1]
            self.counts.append([self.spectra[i][0],s/(self.boxcar*2+1)])
    def ReadCalibration(self):
        del self.wave_cal[:]
        for i in [1,2,3,4]:
            self.usb.write(0x01,chr(0x05)+chr(i))
            ret = self.usb.read(0x81,64)
            string=""
            for r in ret[2:]:
                if r <> 0: string=string+chr(r)
            self.wave_cal.append(float(string))
    def querystatus(self):
        self.usb.write(0x01,chr(0xFE))
        ret = self.usb.read(0x81,64)
        print "Number of pixel = "+str(ret[0]+ret[1]*256)
        LSW = ret[2]+ret[3]*256
        MSW = ret[4]+ret[5]*256
        print "Integration time = "+str(LSW+MSW*256)+" us"
        print "Lamp enable = "+str(ret[6])
        print "Trigger mode = "+str(ret[7])
        print "Spectral acquisition status = "+str(ret[8])
        print "Packets in spectra = "+str(ret[9])
        print "Power down = "+str(ret[10])
        print "Packets count = "+str(ret[11])
        print "USB communication speed = "+str(ret[14])
    def QueryInformation(self):
        for i in range(19):
            self.usb.write(0x01,chr(0x05)+chr(i))
            ret = self.usb.read(0x81,64)
            string=""
            for r in ret[2:]:
                string=string+chr(r)
            print i,string

class FakeSpectrometer:
    def __init__(self,int_time=20,avg=4,boxcar=3,run=False,lock=False,wave_cal=[1.7859480E02,2.1551852e-01,-4.1099884e-06,-5.2138449e-10]):
        self.int_time=int_time#milliseconds
        self.last_int_time=0
        self.avg=avg#number of averages
        self.boxcar=boxcar
        self.data=[]#buffer used for averaging spectra
        self.run=run
        self.lock=lock
        self.spectra=[]#averaged spectra
        self.counts=[]
        self.wave_cal=wave_cal#wave calibration data
        self.int_time_min=1#ms
        self.int_time_max=10000#ms
        self.low_cut=200
        self.high_cut=1000
        self.maxcount=10000
        self.time0=time.time()
    def set_int_time(self):#int time is in microseconds on USB4000
        MSW=self.int_time*1000/65536
        LSW=self.int_time*1000-65536*MSW
        LSW_MSB,LSW_LSB=HiLow(LSW)
        MSW_MSB,MSW_LSB=HiLow(MSW)
    def getspectra(self):
        time.sleep(0.5)
        self.lock=True
        del self.spectra[:]
        a=range(3648)
        for i in range(len(a)):
            w=self.wave_cal[0]+self.wave_cal[1]*(i)+self.wave_cal[2]*(i)**2+self.wave_cal[3]*(i)**3
            if self.low_cut <= w <= self.high_cut:self.spectra.append([w,a[i]+time.time()-self.time0])
        self.red_res()        
        self.lock=False
    def red_res(self):
        del self.counts[:]
        k=len(self.spectra)/(self.boxcar*2+1)
        #T=T[:k*(r*2+1)]
        for i in range(self.boxcar,len(self.spectra[:k*(self.boxcar*2+1)]),self.boxcar*2+1):
            s=0.0
            for j in range(i-self.boxcar,i+self.boxcar+1):
                s=s+self.spectra[j][1]
            self.counts.append([self.spectra[i][0],s/(self.boxcar*2+1)])

def HiLow(x):
    Hi=x/256
    Low=x-256*Hi
    return Hi, Low

def ocean(spectrometer):
    while spectrometer.run:
        time.sleep(0.01)
        spectrometer.getspectra()
