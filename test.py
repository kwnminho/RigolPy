import visa
import matplotlib.pyplot as plot
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
import time
import datetime
from scipy.optimize import leastsq

fname='output_20160121_RF Leakage.txt'

rm = visa.ResourceManager()
rm.list_resources()
# Identifying the device
scope = rm.open_resource('USB0::0x1AB1::0x0960::DSA8A154902989::INSTR',read_termination='\n')
print(scope.query('*IDN?'))
# Set Center frequency
#scope.write(":FREQuency:CENTer 15000000")
scope.write(":CALCulate:MARKer1:CPEak ON")
#scope.write(":SENSe:DETector:RMS")
scope.write(":TRACE:MATH:PEAK:TABLE:STATE OFF")
scope.write(":BANDwidth:RESolution 300KHZ") # Sets resolution. Will slow sweeptime
scope.write(":FREQuency:START 1MHZ")
scope.write(":FREQuency:STOP 500MHZ")
# Get the X-axis scale
startfreq=int(scope.query(':FREQuency:START?'))
stopfreq=int(scope.query(':FREQuency:STOP?'))
datasize=601 # Number of measurement points in a single inquiry
freqs=(np.arange(datasize)*(stopfreq-startfreq)/datasize+startfreq)*1e-6
x=np.linspace(startfreq*1e-6,stopfreq*1e-6,num=datasize)
# Data Acquisition
timesize=700 # Number of time bins
step=1 # in seconds. How often should measurements occur?
updatetime=1 # in seconds. Spectogram refresh interval.
specdata=-90*np.ones((timesize,datasize)) # Initialize the spectogram array to -90 dB
plot.show()

# File I.O
plot.rcParams.update({'font.size': 35})
def do_filewrite(filename,data):
    ROW_SIZE=1
    NUM_COLMUNS=len(data)
    f=tables.open_file(filename,mode='w')
    atom=tables.Float64Atom()
    array_c = f.create_earray(f.root, 'data', atom, (0, NUM_COLMUNS))
    array_c.append(data)
    f.close()

def do_plot():
    plot.cla()
    plot.imshow(specdata,aspect='auto',extent=(startfreq*1e-6,stopfreq*1e-6,timesize*step,0))
    plot.title('Spectogram',fontsize=30)
    plot.xlabel("Frequency (MHz)",fontsize=30)
    plot.ylabel("Time(s)",fontsize=30)
    plot.show(False)
    plot.pause(0.001)

def do_plot1d_peakutil():
    plot.cla()
    y=specdata[1]
    plot.plot(x,y)
    plot.xlim([startfreq*1e-6,stopfreq*1e-6])
    plot.title('Spectrum',fontsize=30)
    plot.ylabel("Amplitude(dB)",fontsize=30)
    plot.xlabel("Frequency(MHz)",fontsize=30)
    indexes=peakutils.indexes(y+80,thres=0.3,min_dist=100)
    pplot(x,y,indexes)
    plot.show(False)
    plot.pause(0.001)

initialtime=time.time()
starttime=time.time()
starttime2=time.time()


while(True):
    if time.time()>starttime+step:
        starttime=time.time()
        try:
            rawdata=scope.query(':TRACE? TRACE1')[12:] # Strip off 10 characters of header
            my_list=rawdata.split(",")
            specdata[0]=np.array(my_list)
            ts=time.time() # Measurement time
            timestamp=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] # Formatted conversion
            #print(peakutils.peak.centroid(x,specdata[0]+min(specdata[0])),2)
            #indexes=peakutils.indexes(specdata[0]+100,thres=0.3,min_dist=50)
            #peak_x=peakutils.peak.interpolate(x,specdata[0]+100,width=10,ind=indexes)
            #print(peak_x)
            #centroid=peakutils.peak.centroid(x,specdata[0]+min(specdata[0]))
            #centroid_data=np.array([ts-initialtime,peak_x])
            #print(centroid_data)
            #f=open(fname,'ab')
            #np.savetxt(f,centroid_data[None],delimiter=',',fmt='%.4f',newline='\n')
            #f.close()
            specdata=np.roll(specdata,1,axis=0)

        except:
            ts=time.time()
            timestamp=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            specdata[0]=-100*np.ones((1,datasize))
            specdata=np.roll(specdata,1,axis=0)

        print(timestamp)

        if time.time()>starttime2+updatetime:
            starttime2=time.time()
            plot.subplot(211)
            do_plot1d_peakutil()
            plot.subplot(212)
            do_plot()



