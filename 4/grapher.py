import matplotlib.pyplot as plt
import numpy as np
import math

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

def mean(values):
    mean = 0
    for v in values: mean += v
    mean /= len(values)
    return mean

def standard_deviation(values):
    m = mean(values)

    dev = 0
    for v in values: dev += (v - m) ** 2
    dev /= len(values) - 1
    return math.sqrt(dev)
    

availableColors = ["grey", "orange", "green", "magenta", "black", "blue"]
class Trial:
    def __init__(self, filename = None, labelName = None):
        self.m = []
        self.V = []
        self.errors = []
        self.color = availableColors[0]
        availableColors.pop(0)
        self.labelLine = True
        self.name = labelName

        if filename == None:
            return

        self.labelLine = False
        
        file = open(filename + ".csv", "r")
        raw = file.read().split("\n")
        file.close()

        if len(filename) == 1:
            filename = "Loading Trial " + filename
        
        
        if labelName == None:
            self.name = filename.title()

        file = open("output.txt", "a")
        file.write("\n\n" + self.name + "\n\nMass\tRaw V\tAdjusted\n")

        line = raw[1].split("\t")
        offset = float(line[1])
        for line in raw[1:]:
            if line == "": continue
            line = line.split("\t")
            self.m.append(float(line[0]) / 1000)
            self.V.append(float(line[1]) - offset)
            file.write("{}\t{}\t{:.4g}\n".format(line[0], line[1], float(line[1]) - offset))

        file.close()

    def V_from_m(self, m):
        V = []
        for i in range(0, len(self.m)):
            if self.m[i] == m:
                V.append(self.V[i])
        return V

    def plot(self):
        plt.scatter(self.m, self.V, marker = ".", label = self.name, color = self.color, s=10)

    def gradient(self):
        return np.polyfit(np.array(self.m), np.array(self.V), 1)[0]
    def fit_values(self):
        gradient = self.gradient()
        val = []
        for mass in self.m:
            val.append(mass * gradient)
        return val

    def plot_fit(self):
        if self.labelLine:
            plt.plot(self.m, self.fit_values(), linestyle = "--", color = self.color, linewidth = 1, label = self.name)
        else:
            plt.plot(self.m, self.fit_values(), linestyle = "--", color = self.color, linewidth = 1)

    def plot_error_bars(self):
        plt.errorbar(self.m, self.V, yerr=[self.errors, self.errors], capsize=2, fmt=".", label = self.name)

    def eq_text(self):
        return "V = {:#0.4g} m\nr^2 = {:#0.5g}".format(self.gradient(), r_squared(self.V, self.fit_values()))



file = open("output.txt", "w") # clear previous contents
file.close()

loading = [Trial("1"), Trial("2"), Trial("3")]
unloading = Trial("unloading")
combined = Trial(labelName = "Loading Best Fit")
averaged = Trial(labelName = "Loading")
averaged.labelLine = False

for trial in loading:
    combined.m.extend(trial.m)
    combined.V.extend(trial.V)


file = open("output.txt", "a")
file.write("\n\nCombined Loading Data\n\nMass\tMean V\tStandard Dev\n")

for m in combined.m:
    if m not in averaged.m:
        averaged.m.append(m)
        vals = combined.V_from_m(m)
        V = mean(vals)
        error = standard_deviation(vals)
        averaged.V.append(V)
        averaged.errors.append(error)
        file.write("{}\t{:#0.4g}\t{:#0.4g}\n".format(m, V, error))

file.close()

combined.m.sort()
combined.V.sort()

averaged.plot_fit()
#combined.plot_fit()
unloading.plot_fit()

plt.text(1.250, 1.6, unloading.eq_text(), horizontalalignment="right", color = unloading.color)
plt.text(1.300, 1.3, combined.eq_text(), color = combined.color)

unloading.plot()
averaged.plot_error_bars()
#for trial in loading:
#    trial.plot()

plt.xlabel("Mass (kg)")
plt.ylabel("Voltage (mV)")
plt.legend()
plt.show()
