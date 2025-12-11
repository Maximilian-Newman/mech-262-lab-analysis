import numpy as np
import matplotlib.pyplot as plt
import math

plt.rcParams["font.family"] = "Times New Roman"

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



def get_phase(time, data, freq, amplitude, known):
    bestPhase = 0
    bestR = 0
    for phase in range(0, 1000):
        phase /= freq * 1000
        
        time = np.array(time)
        fit = amplitude * np.sin(2 * math.pi * freq * (time + phase))
        
        for wave in known:
            if wave[0] == freq:
                continue
            fit += wave[1] * np.sin(2 * math.pi * wave[0] * (time + wave[2]))

            
        r2 = r_squared(data, fit)
        if r2 > bestR:
            bestR = r2
            bestPhase = phase

    return bestPhase







def graph_pair(name, start = None, end = None, textx = 0, texty = 1.2, amplitudeModifyer = 1, forceAmplitude = None, showFourier=True, phaseShift=0, color="blue", forceFreq = None):
    file = open(name + ".csv", "r")
    data = file.read().split("\n")[1:]
    file.close()

    time = []
    amplitude = []
    for line in data:
        line = line.split("\t")
        t = float(line[0])
        if (start == None or t >= start) and (end == None or t <= end):
            time.append(t - phaseShift)
            amplitude.append(float(line[1]))

    file = open(name + " fourier.csv", "r")
    data = file.read().split("\n")[1:]
    file.close()

    freqs = []
    fourierAmplitude = []
    fourierMean = 0
    for line in data:
        line = line.split("\t")
        if float(line[0]) <= 25 or name == "guitar":
            freqs.append(float(line[0]))
            fourierAmplitude.append(float(line[1]))
            fourierMean += float(line[1])

    fourierMean /= len(freqs)

    start = min(time)
    end = max(time)

    if showFourier:
        new_graph()
        plt.scatter(freqs, fourierAmplitude, marker=".", color="blue")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("ln Amplitude")

    fourierPeaks = []
    totalPeakFreq = 0
    currentPeakAmp = 0
    currentPeakNum = 0
    if forceFreq == None:
        for i in range(len(freqs)):
            a = fourierAmplitude[i]
            f = freqs[i]
            if a > 4 * fourierMean:
                # merge smoothened peaks into discrete ones

                currentPeakAmp += math.e ** a
                totalPeakFreq += f
                currentPeakNum += 1
                    
            elif currentPeakAmp > 0:
                
                if showFourier: # show discrete line
                    lineHeight = currentPeakAmp * amplitudeModifyer**1.7 / 7
                    plt.plot([totalPeakFreq / currentPeakNum, totalPeakFreq / currentPeakNum], [0, lineHeight], color="orange", linewidth=0.5)
                    plt.text(totalPeakFreq / currentPeakNum, lineHeight, "{} Hz".format(f))
                                         
                if forceAmplitude == None:
                    fourierPeaks.append([totalPeakFreq / currentPeakNum, amplitudeModifyer * currentPeakAmp])
                else:
                    fourierPeaks.append([totalPeakFreq / currentPeakNum, forceAmplitude])
                
                totalPeakFreq = 0
                currentPeakAmp = 0
                currentPeakNum = 0

    else:
        fourierPeaks = [[forceFreq, forceAmplitude]]
                




            

    
    if showFourier: new_graph()
    plt.scatter(time, amplitude, marker=".", color=color)
    plt.xlabel("Time (s)")
    plt.ylabel("Potential Difference (V)")


    highestFreq = 0
    # get phase of sin waves
    for i in range(len(fourierPeaks)):
        peak = fourierPeaks[i]
        peak.append(get_phase(time, amplitude, peak[0], peak[1], fourierPeaks[:i]))
        if peak[0] > highestFreq and peak[0] > 0:
            highestFreq = peak[0]

    # iteratively improve on phase guesses (for guitar)
    if len(fourierPeaks) > 1:
        for _ in range(5):
            for i in range(len(fourierPeaks)):
                peak = fourierPeaks[i]
                peak[2] = get_phase(time, amplitude, peak[0], peak[1], fourierPeaks)


    eqText = "V = "
    step = 1 / (5000 * highestFreq)
    t = np.array(range(int(start/step), int(end / step))) * step
    time = np.array(time)
    fit = np.zeros(t.shape)
    r2fit = np.zeros(time.shape)
    for peak in fourierPeaks:
        fit += peak[1] * np.sin(2 * math.pi * peak[0] * (t + peak[2]))
        r2fit += peak[1] * np.sin(2 * math.pi * peak[0] * (time + peak[2]))
        eqText += "{:#.4g} sin({:#.4g}π (t + {:#.4g})) + ".format(peak[1], 2*peak[0], peak[2])

    eqText = eqText[:-3] # remove last "+"
    eqText += "        r^2 = {:#.4g}".format(r_squared(amplitude, r2fit))
    
    plt.plot(t, fit, linestyle="--", color=color, linewidth=0.5)
    plt.text(textx, texty, eqText, color=color)

    





graph_pair("5 Hz", None, None, 0, 0.15, forceAmplitude = 1, forceFreq = 1/53)
graph_pair("50 Hz", 0, 0.25, forceAmplitude = 1)
graph_pair("500 Hz", 0, 0.2, forceAmplitude = 1)
graph_pair("part 3", 0, 0.2, 0, 1.3, forceAmplitude = 1.07335)
graph_pair("guitar", 1, 1.05, 1, 0.4, 0.0205)


graph_pair("500 Hz", 0, 1, 0, 1.2, forceAmplitude = 1, color="dodgerblue")
graph_pair("50 Hz", 0, 1, 0.3, 1.2, forceAmplitude = 1, phaseShift = 0.00365, showFourier = False, color="black")
graph_pair("5 Hz", 0, 1, 0.6, 1.2, forceAmplitude = 1, phaseShift = -0.0065, showFourier = False, color="red", forceFreq = 1/53)








new_graph()

file = open("normalized.csv", "r")
data = file.read().split("\n")
file.close()

labels = data[0].split("\t")
data = data[1:]
lines = [ [], [], [], [] ]

for line in data:
    if line == "": continue
    line = line.split("\t")
    for i in range(len(line)):
        lines[i].append(float(line[i]))

for i in range(1, len(lines)):
    plt.scatter(lines[0], lines[i], marker = ".")
    plt.plot(lines[0], lines[i], label=labels[i])

plt.xlabel("Sample Frequency")
plt.ylabel("Normalized Value Relative to Oscilloscope")
plt.legend()
plt.show()
