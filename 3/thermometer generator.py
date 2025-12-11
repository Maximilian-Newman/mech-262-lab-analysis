# This program generates a csv file with the thermometer's theoretical frequency responses that can be used by the other program to generate a bode plot


import math

def amplitude(frequency):
    return math.sqrt(1 / (1 + 69.444 * frequency**2))

file = open("thermometer.csv", "w")
file.write("freq\tV_in\tV_out\n")
for i in range(-1000, 1000):
    i = 10**(i / 300)
    file.write(str(i) + "\t1\t" + str(amplitude(i)) + "\n")
file.close()
