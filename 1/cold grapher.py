import numpy as np
import matplotlib.pyplot as plt
import math
import copy

plt.rcParams["font.family"] = "Times New Roman"

file = open("cold.csv", "r")
data = file.read().split("\n")[1:]
file.close()

time = []
voltage = []
temp = []
log_volt = []

equil = 0.0143770
timeshift = 3.1


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



file = open("raw output cold.csv", "w")
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
b_time = np.array(time[50:150])
b_log_volt = np.array(log_volt[50:150])
sb_time = np.array(time[500:1700])
sb_log_volt = np.array(log_volt[500:1700])
time = np.array(time)
log_volt = np.array(log_volt)
m, c = np.polyfit(b_time, b_log_volt, 1)
m2, c2 = np.polyfit(sb_time, sb_log_volt, 1)
plt.scatter(time, log_volt, marker=".")
plt.plot(time[:1250], m * time[:1250] + c, linestyle="--", color="orange")
plt.plot(time, m2 * time + c2, linestyle="--", color="red")
if c >= 0: plt.text(0, -12, "ln(| %0.4g" % equil + " - V |) = %0.4g " % m + " t + %0.4g" % c)
else: plt.text(0, -12, "ln(| %0.4g" % equil + " - V |) = %0.4g " % m + " t - %0.4g" % -c)
plt.text(0, -13, "r^2 = %0.4g*" % r_squared(b_log_volt, m*b_time+c))
plt.text(0, -14, "*calculated over 5 - 15 s. range")

plt.text(80, -1, "ln(| %0.4g" % equil + " - V |) = %0.4g " % m2 + " t + %0.4g" % c2)
plt.text(80, -2, "r^2 = %0.4g*" % r_squared(sb_log_volt, m2*sb_time+c2))
plt.text(80, -3, "*calculated over 50 - 170 s. range")

plt.xlabel("Time (s)")
plt.ylabel("Linearized Voltage     ln(| " + str(equil) + " - V |)")

plt.figure(2)
plt.scatter(time[:300], log_volt[:300], marker=".")
plt.plot(time[:300], m * time[:300] + c, linestyle="--", color="orange")
if c >= 0: plt.text(0, -2.8, "ln(| %0.4g" % equil + " - V |) = %0.4g " % m + " t + %0.4g" % c)
else: plt.text(0, -2.8, "ln(| %0.4g" % equil + " - V |) = %0.4g " % m + " t - %0.4g" % -c)
plt.text(0, -3.1, "r^2 = %0.4g*" % r_squared(b_log_volt, m*b_time+c))
plt.text(0, -3.4, "*calculated over 5 - 15 s. range")
plt.xlabel("Time (s)")
plt.ylabel("Linearized Voltage     ln(| " + str(equil) + " - V |)")



plt.figure(3)
plt.scatter(time, voltage, marker=".")
plt.plot(time, equil + math.e ** c * math.e ** (m*time), linestyle="--", color="orange")
plt.text(25, 0.4, "V = %0.4g" % equil + " + %0.4g" % (math.e**c) + " e ^ (%0.4g t)" % m)
plt.text(25, 0.35, "r^2 = %0.4g*" % r_squared(voltage[31:], equil + math.e ** c * math.e ** (m*time[31:])))
plt.text(25, 0.3, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Measured Potential Difference (V)")


plt.figure(4)
plt.scatter(time, temp, marker = ".")
plt.plot(time, 71 * equil -10.2 + 71 * math.e ** c * math.e ** (m*time), linestyle="--", color="orange")
plt.text(25, 10, "T = %0.4g" % (71*equil-10.2) + " + %0.4g" % (71*math.e**c) + " e ^ (%0.4g t)" % m)
plt.text(25, 7, "r^2 = %0.4g*" % r_squared(temp[31:], 71 * equil -10.2 + 71 * math.e ** c * math.e ** (m*time[31:])))
plt.text(25, 4, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")

plt.figure(5)
voltage = np.array(voltage)
plt.scatter(time, 100 * abs(equil - voltage) / math.e**c, marker=".")
plt.plot(time, 100 * math.e**(m*time), linestyle="--", color="orange")
plt.text(10, 70, "E = 100 e^(%0.4g t)" % m)
plt.text(10, 62, "r^2 = %0.4g*" % r_squared(100 * abs(equil - voltage[31:]) / math.e**c, 100 * math.e**(m*time)))
plt.text(10, 54, "*only calculated starting after input start")
plt.xlabel("Time (s)")
plt.ylabel("Dynamic Error (% of input step size)")

plt.figure(6)
plt.scatter(-m*time, (voltage - equil) / math.e**c - 1, marker=".")
plt.plot(-m*time, math.e**(m*(time)) - 1, linestyle="--", color="orange")
plt.text(2, -0.6, "V = e^(- n_τ) - 1" % m)
plt.text(2, -0.7, "r^2 = %0.4g" % r_squared((voltage - equil) / math.e**c - 1, math.e**(m*(time)) - 1))
plt.text(2, -0.8, "*only calculated starting after input start")
plt.xlabel("Number of Time Constants (n_τ)")
plt.ylabel("Output Voltage")


plt.show()
