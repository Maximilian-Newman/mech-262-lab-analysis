import numpy as np
import matplotlib.pyplot as plt
import math
import copy

plt.rcParams["font.family"] = "Times New Roman"

file = open("hot.csv", "r")
data = file.read().split("\n")[1:]
file.close()

time = []
voltage = []
temp = []
log_volt = []

equil = 1.51588
timeshift = 3.9



def r_squared(points, line):
    ssr = 0
    avLine = 0
    for i in range(0, len(points)):
        ssr += (points[i] - line[i]) ** 2
        avLine += line[i]
    
    avLine = avLine / len(points)
    sst = 0
    for i in range(0, len(points)):
        sst += (points[i] - avLine) ** 2

    return 1 - ssr / sst




file = open("raw output hot.csv", "w")
file.write("Time (s)\tP.D. (V)\tlinearized V\ttemp (°C)\n")
for point in data:
    if point == "": continue
    point = point.split("\t")
    time.append(float(point[0]) - timeshift)
    voltage.append(float(point[1]))
    temp.append(71 * float(point[1]) - 10.2)
    log_volt.append(math.log(abs(equil - float(point[1])), math.e))
    file.write(str(round(float(point[0]) - timeshift, 2)) + "\t")
    file.write(point[1] + "\t")
    file.write("%0.4g\t" % (math.log(abs(equil - float(point[1])), math.e)))
    file.write("%0.4g\n" % (71 * float(point[1]) - 10.2))

file.close()






plt.figure(1)
b_time = np.array(time[60:370])
b_log_volt = np.array(log_volt[60:370])
time = np.array(time)
log_volt = np.array(log_volt)
m, c = np.polyfit(b_time, b_log_volt, 1)
plt.scatter(time, log_volt, marker=".")
plt.plot(time, m * time + c, linestyle="--", color="orange")
if c >= 0: plt.text(0, -6, "ln(| " + str(equil) + " - V |) = %0.4g " % m + " t + %0.4g" % c)
else:      plt.text(0, -6, "ln(| " + str(equil) + " - V |) = %0.4g " % m + " t - %0.4g" % -c)
plt.text(0, -6.8, "r^2 = %0.4g*" % r_squared(b_log_volt, m*b_time+c))
plt.text(0, -7.6, "*calculated over 6 - 37 s. range")
plt.xlabel("Time (s)")
plt.ylabel("Linearized Voltage     ln(| " + str(equil) + " - V |)")


plt.figure(2)
plt.scatter(time, voltage, marker=".")
plt.plot(time, equil - math.e ** c * math.e ** (m*time), linestyle="--", color="orange")
plt.text(20, 1, "V = %0.4g" % equil + " - %0.4g" % (math.e**c) + " e ^ (%0.4g t)" % m)
plt.text(20, 0.9, "r^2 = %0.4g*" % r_squared(voltage[39:], equil - math.e ** c * math.e ** (m*time[39:])))
plt.text(20, 0.8, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Measured Potential Difference (V)")


plt.figure(3)
plt.scatter(time, temp, marker = ".")
plt.plot(time, 71 * equil - 10.2 - 71 * math.e ** c * math.e ** (m*time), linestyle="--", color="orange")
plt.text(15, 60, "T = %0.4g" % (71*equil-10.2) + " - %0.4g" % (71*math.e**c) + " e ^ (%0.4g t)" % m)
plt.text(15, 55, "r^2 = %0.4g*" % r_squared(temp[39:], 71 * equil - 10.2 - 71 * math.e ** c * math.e ** (m*time[39:])))
plt.text(15, 50, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")


plt.figure(4)
voltage = np.array(voltage)
plt.scatter(time, 100 * abs(equil - voltage) / math.e**c, marker=".")
plt.plot(time, 100 * math.e**(m*time), linestyle="--", color="orange")
plt.text(10, 70, "E = 100 e^(%0.4g t)" % m)
plt.text(10, 60, "r^2 = %0.4g*" % r_squared(100 * abs(equil - voltage[39:]) / math.e**c, 100 * math.e**(m*time[39:])))
plt.text(10, 50, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Dynamic Error (% of input step size)")

plt.figure(5)
plt.scatter(-m*time, 1 - (equil - voltage) / math.e**c, marker=".")
plt.plot(-m*time, 1 - math.e**(m*time), linestyle="--", color="orange")
plt.text(2.2, 0.8, "V = 1 - e^(- n_τ)" % m)
plt.text(2.2, 0.7, "r^2 = %0.4g*" % r_squared(1 - (equil - voltage[39:]) / math.e**c, 1 - math.e**(m*time[39:])))
plt.text(2.2, 0.6, "*only calculated starting after input start")
plt.xlabel("Number of Time Constants (n_τ)")
plt.ylabel("Output Voltage")

plt.show()
