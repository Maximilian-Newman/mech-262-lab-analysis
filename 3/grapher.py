import matplotlib.pyplot as plt
import math
import numpy as np

# expected csv format:
#
# first row headers - will be ignored
# freq \t v_in \t v_out \n




def to_db(amplitude):
    return 20 * math.log(amplitude, 10)

figNum = 1
def new_graph():
    global figNum
    plt.figure(figNum)
    figNum += 1

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



# assumes exactly 2 points are in 2nd attenuation band for second order
def graph(filename, expectedCutoff=None, expectedAttenuation=None, secondOrder=False):
    new_graph()

    file = open(filename, "r")
    data = file.read().split("\n")[1:]
    file.close()

    decade = []
    gain = []

    for line in data:
        if line == "": continue
        line = line.split("\t")
        decade.append(math.log(float(line[0]), 10))
        gain.append(to_db(float(line[2]) / float(line[1])))

    threshGain = max(gain) - 3

    i = 0
    while gain[i] > threshGain: i += 1

    #linear interpolation
    threshDecade = decade[i-1] + (decade[i] - decade[i-1]) * (gain[i-1] - threshGain) / (gain[i-1] - gain[i])

    if secondOrder:
        stopBandDecade = np.array(decade[i:-2])
        stopBandGain = np.array(gain[i:-2])
        stopBandDecade2 = np.array(decade[-2:])
        stopBandGain2 = np.array(gain[-2:])
    else:
        stopBandDecade = np.array(decade[i:])
        stopBandGain = np.array(gain[i:])
    attenuation, yIntercept = np.polyfit(stopBandDecade, stopBandGain, 1)
    attenuation *= -1

    r = r_squared(stopBandGain, yIntercept - attenuation * stopBandDecade)

    eqDecade = (max(gain) - yIntercept) / -attenuation
    #threshDecade = (threshGain - yIntercept) / -attenuation ################################################
    threshFreq = 10 ** threshDecade

    if secondOrder:
        m2, c2 = np.polyfit(stopBandDecade2, stopBandGain2, 1)
        eqDecade2 = (c2 - yIntercept) / (-attenuation - m2)
        m2 = -m2
    else:
        eqDecade2 = max(decade)

    plt.plot([min(decade), eqDecade], [max(gain), max(gain)], linestyle="--", color="orange")
    plt.plot([threshDecade, threshDecade], [min(gain), max(gain)], linestyle="-.", linewidth=1, color="orange")
    plt.plot([eqDecade, eqDecade2], [yIntercept - attenuation * eqDecade, yIntercept - attenuation * eqDecade2], linestyle="--", color="orange")
    if secondOrder:
        plt.plot([eqDecade2, max(decade)], [c2 - m2 * eqDecade2, c2 - m2 * max(decade)], linestyle="--", color="orange")

    if expectedCutoff != None:
        plt.plot([math.log(expectedCutoff, 10), math.log(expectedCutoff, 10)], [min(gain), max(gain)], linestyle="-.", linewidth=1, color="green")
        plt.text(math.log(expectedCutoff, 10), min(gain), "  {:.4g} Hz\n".format(expectedCutoff), horizontalalignment="right", rotation=90, color="green")
    else:
        expectedCutoff = 10 ** threshDecade

    if expectedAttenuation != None:
        # c = y + (-m)x
        expectC = threshGain + expectedAttenuation * math.log(expectedCutoff, 10)
        print(yIntercept, expectC)
        eqDecadeExpected = (max(gain) - expectC) / -expectedAttenuation
        plt.plot([eqDecadeExpected, eqDecade2], [expectC - expectedAttenuation * eqDecadeExpected, expectC - expectedAttenuation * eqDecade2], linestyle="--", color="green")
        
    
    plt.xlabel("log Frequency")
    plt.ylabel("Gain (dB)")

    plt.text(threshDecade, min(gain), "\n  {:.4g} Hz".format(threshFreq), horizontalalignment="left", rotation=90, color="orange")
    plt.text((eqDecade + eqDecade2) / 2, yIntercept - attenuation * (eqDecade + eqDecade2) / 2, " {:.4g} dB/decade \n  r^2 = {:.4g} ".format(attenuation, r))
    if secondOrder:
        plt.text((eqDecade2 + max(decade)) / 2, c2 - m2 * (eqDecade2 + max(decade)) / 2, " {:.4g} dB/decade ".format(m2), rotation=65)

    plt.scatter(decade, gain, marker=".", color="blue")
    
    print()
    print()
    print(filename)
    print("Threshold Frequency:", threshFreq)
    if secondOrder:
        print("Attenuation 1:", attenuation, "dB/decade")
        print("Attenuation 2:", m2, "dB/decade")
    else:
        print("Attenuation:", attenuation, "dB/decade")





graph("1st order.csv", 1061, 20)
graph("2nd order.csv", 1061, 40, True)
graph("thermometer.csv")

plt.show()
