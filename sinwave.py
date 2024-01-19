#Began work on January 16, 2024
import numpy as np
import matplotlib.pyplot as plt

# #Set the frequency and amplitude of the sine wave
# frequency = 5
# amplitude = 1

# #Set the sampling rate and duration of the waveform 
# samping_rate = 100
# duration = 1

# #Generate the time_array
# t = np.arange(0, duration, 1/samping_rate)

# #Generate the sine wave
# sine_wave = amplitude * np.sin(2*np.pi*frequency*t)

# #Plot the sine wave
# plt.plot(t, sine_wave)

x = np.linspace(0, 2 *np.pi, 100)
y = np.sin(x)

plt.plot(x, y, linewidth = 3)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show

#Need to generate an array consisting of a sinwave
#Do I need a test file of data points??

