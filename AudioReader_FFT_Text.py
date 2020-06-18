# Import that necessary programs
from pyqtgraph.Qt import QtGui, QtCore                                         # Has to be installed from http://www.pyqtgraph.org/ 
import numpy as np                                                             
import pyqtgraph as pg                                                         # Found in same package as pyqtgraph.Qt
import sys
import pyaudio                                                                 # Needed for the live audio management (use pipwin install in command code)
import scipy.fftpack as fft                                                    # For the Fast Fourier Transform
import struct                                                                  # Unpacking the audio data

# Make a class to run the data in to

class Plot2D():
    def __init__(self):                                                        # This is the initiation of the window to plot into
        self.traces = dict()                                                   # By setting up the GUI of the window
        self.phase = 0                                                         #
        self.t = np.arange(0, 3.0, 0.01)                                       #
        pg.setConfigOptions(antialias=True)                                    #
        self.app = QtGui.QApplication([])                                      #
        self.win = pg.GraphicsWindow(title="Audio and Fourier Transform of it")#
        self.win.resize(1000,600)                                              # 
        self.win.setWindowTitle('Audio Spectrum Analysier')                    # Name that window of the page

# Make the axis variable names, ticks and size
                                                                
        wf_xlabels = [(0, 'Start'), (4096, 'End')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])
        
        wf_ylabels = [(0, '0'), (30,'30'), (60,'60'),(90,'90'), (120,'120'), 
                      (150,'150'), (180,'180'),(210,'210'), (240, '240')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])
        
        sp_xlabels = [(np.log10(28),'A0'), (np.log10(55),'A1'), 
                      (np.log10(110),'A2'), (np.log10(220),'A3'),
                      (np.log10(440),'A4'), (np.log10(880),'A5'), 
                      (np.log10(1760),'A6'), (np.log10(3520),'A7'),
                      (np.log10(7040),'A8'),(np.log10(22050),'22050')]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])
        
# Build the plots for the wave and fourier
        
        self.waveform = self.win.addPlot(title="WAVEFORM", row=1, col=1, 
                                         axisItems={'bottom':wf_xaxis,
                                                    'left': wf_yaxis})
        self.spectrum = self.win.addPlot(title="SPECTRUM", row=2, col=1, 
                                         axisItems={'bottom':sp_xaxis})

# Variables list 
        
        self.CHUNK = 1024 * 2                                                  # CHUNK = amount of data gathered
        self.FORMAT = pyaudio.paInt16                                          # Set data to 16 Bit format
        self.CHANNELS = 1                                                      # Imput channel of mic
        self.RATE = 44100                                                      # Hurtz of mic
   
# Gathering the audio data
     
        self.p = pyaudio.PyAudio()                                             # set p to be the audio data
        self.stream = self.p.open(                                             # P collects the data through the, 
            format=self.FORMAT,                                                # Correct format and,
            channels=self.CHANNELS,                                            # Correct channel and,
            rate=self.RATE,                                                    # at the correct rate             
            input=True,                                                        
            output=True,                                                       
            frames_per_buffer=self.CHUNK                                       # set the buffer rate
            )
        
        self.x = np.arange(0, 2* self.CHUNK, 2)                                # set the x axis values for the Waveform                           
        self.f = np.linspace(0, self.RATE / 2, self.CHUNK / 2)                 # set the x axis for the fourier transform

    def start(self):                                                           # start the plot to open the graph
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):#
            QtGui.QApplication.instance().exec_()                              #

    def set_plotdata(self,name,data_x,data_y):                                 # build the plots with what the data will be entered into
        if name in self.traces:                                                # if statement places the data into the correct lines
            self.traces[name].setData(data_x,data_y)                           #  
        else:
            if name == 'waveform':                                             # the data for waveform goes in here  
                self.traces[name] = self.waveform.plot(pen='c',width=4)        # set the width and colour of the plot line
                self.waveform.setYRange(0, 255, padding=0)                     # set the range of the y values
                self.waveform.setXRange(0, 2* self.CHUNK, padding=0.005)       # set the range of the x values
            if name == 'spectrum':                                             # the data for spectrum goes here
                self.traces[name] = self.spectrum.plot(pen='m',width=3)        # set the width and colour of the plot line
                self.spectrum.setLogMode(x=True, y=False)                      # set the axis to be in a log base 10 for the x axis
                self.spectrum.setYRange(0,1, padding=0)                        # set the range for y axis 
                self.spectrum.setXRange(np.log10(20), np.log10(self.RATE / 2), # set the range for the x axis
                                        padding=0.005)                         #
                
# The function for updating the graph

    def update(self):                                                          
        wf_data = self.stream.read(self.CHUNK)                                 # Gather the mic input data and call it something
        wf_data = struct.unpack(str(2 * self.CHUNK)+ 'B',wf_data)              # Unpack the decoded mic data
        wf_data = np.array(wf_data,dtype='b')[::2] + 128                       # half the data and wrap the data around to by setting it to have mod 128
        self.set_plotdata(name='waveform',data_x=self.x,data_y=wf_data)        # Input the new data into the tracer that will plot it
        
        sp_data = fft.fft(np.array(wf_data,dtype='int8')-128)                  # Get the Fast Fourier of the decoded mic data
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)])                       # Take the absolute value of half the data
        sp_data = sp_data* 2 / (128 * self.CHUNK)                              # Rescale the data to plot correctly
        FFT_Data = sp_data
        self.set_plotdata(name='spectrum',data_x=self.f,data_y=sp_data)        # Place the data into the tracer for the spectrum
        
# This is the note return section of the code        
        
        if FFT_Data[20]>0.5:                                                   # The if statement states that if a point on the spectrum,
            print('The note A4 was heard')                                     # goes over the threashold which is currently set to 0.5,
        if sp_data[22]>0.5:                                                    # it prints that the note that corrosponds to that array value,
            print('The note A#4 was heard')                                    # was heard to the screen.
        if sp_data[23]>0.5:
            print('The note B4 was heard')
        
        if sp_data[24]>0.5:
            print('The note C5 was heard')
        if sp_data[26]>0.5:
            print('The note C#5 was heard')
        if sp_data[27]>0.5:
            print('The note D5 was heard')
        if sp_data[29]>0.5:
            print('The note D#5 was heard')
        if sp_data[31]>0.5:
            print('The note E5 was heard')
        if sp_data[32]>0.5:
            print('The note F5 was heard')
        if sp_data[34]>0.5:
            print('The note F#5 was heard')
        if sp_data[36]>0.5:
            print('The note G5 was heard')
        if sp_data[39]>0.5:
            print('The note G#5 was heard')
        if sp_data[41]>0.5:
            print('The note A5 was heard')
        else:
            print('No note detected')                                                         # Else it prints nothing
            #print(np.where(sp_data>0.7))
        
        
        
        
    def animation(self):                                                       # The animation is build to cause the graph to refresh
        timer = QtCore.QTimer()                                                #
        timer.timeout.connect(self.update)                                     # 
        timer.start(20)                                                        # Refresh rate
        self.start()                                                           # Start code


if __name__ == '__main__':                                                     # These three lines start the classes
    p = Plot2D()                                                               # So are like a starter motor in a car
    p.animation()                                                              #

############################# End of Code #####################################
