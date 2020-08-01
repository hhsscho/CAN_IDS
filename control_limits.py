from matplotlib import pyplot as plt
import numpy as np
import matplotlib, math


    #['34 ', 1000], ['42 ', 1000], ['43 ', 1000], ['44 ', 1000], ['5A0', 1000], ['5A2', 1000], 
    #['50 ', 200], ['120', 200], ['5F0', 200], ['517', 200], ['18 ', 200], ['51A', 200],
    #['690', 100], ['2C0', 100], ['587', 100], ['59B', 100], ['5E4', 100], ['A1 ', 100], ['A0 ', 100], ['510', 100], ['4F1', 100], ['110', 100], 
    #['350', 20], ['1F1', 20], ['382', 20], ['4F0', 20], ['4B1', 20], ['4F2', 20], ['4B0', 20], 
    #['260', 10], ['220', 10], ['2A0', 10], ['2B0', 10], ['165', 10], ['164', 10],  ['316', 10], ['153', 10], ['329', 10], 
    #['370', 10], ['545', 10], ['43F', 10], ['440', 10], ['81 ', 10], ['18F', 10], ['80 ', 10]

matplotlib.style.use('ggplot')

path = "D:\\Driving.asc"

# Put in CAN ID you want to analyze
CAN_ID = [['120', 100]]

f = open(path, 'r')
read_data = f.readlines()

TIME = [] # for timestamp
INTERVAL = []  #Timestamp Interval
AVG_INTERVAL = [] #Average Timestamp interval
ACC_OFFSET = [] 
TIMESTAMP = []
SKEW = []
OFFSET = []
TEMP_T = []
ERROR = []
N = 20
P = []
SKEW = []
lamb = 0.9995
G = []
CLP = []
CLM = []
div = []
for j in range(len(CAN_ID)):
    SKEW.append(0)
    P.append(0.000001)
    temp_acc = 0
    find_id = CAN_ID[j][0]
    print("Finding CAN ID : 0x", find_id)
    for i in read_data[4:]:
        i.split(" ", maxsplit = 3)
        id = str(i[15:18])
        time = float(i[0:11])
        if (id == find_id):
            TIME.append(time)

    # Get Timestamp Interval
    for i in range(len(TIME)-1):
        intv = round(TIME[i+1]-TIME[i], 6) # Tn
        INTERVAL.append(intv)

    for i in range(round((len(TIME)-N)/N)):
        TIMESTAMP.append(sum(TIME[0+N*i : N+N*i])/N)
        AVG_INTERVAL.append(round(sum(INTERVAL[ 0+N*i : N+N*i ])/N, 6)) 
    
    for i in range(len(AVG_INTERVAL)):
        offset = (sum(TIME[1+20*i:20+20*i])/19) - (10 * AVG_INTERVAL[i]) - TIME[0 + 20*i]
        OFFSET.append(abs(offset))
        #OFFSET.append(offset)
        
    for i in range(len(OFFSET)):
        temp_acc = temp_acc + OFFSET[i]
        ACC_OFFSET.append(round(temp_acc,10))

    for i in range(round(len(ACC_OFFSET)/20)):
        TEMP_T.append(TIMESTAMP[i*20])

    for i in range(len(TIME)):
        gain = ((1/lamb) * P[i] * TIME[i]) / (1 + (1/lamb) * TIME[i] * TIME[i] * P[i])
        p = (1/lamb)*(P[i] - gain * TIME[i] * P[i])
        G.append(gain)
        P.append(p)

    for i in range(len(ACC_OFFSET)):
        err = ACC_OFFSET[i] - (SKEW[i] * TIMESTAMP[i])
        ERROR.append(err)
        SKEW.append(SKEW[i] + (G[i] * err))

    #print(ERROR[0:20])
    mean = np.mean(ERROR)
    var = math.sqrt(np.var(ERROR))
    print(mean, var)
    clp = 0
    clm = 0
    for error in range(len(ERROR)):
        if abs((ERROR[error] - mean) / var) > 0:
            clp = ((ERROR[error] - mean) / var)
            CLP.append(abs(clp))

    if np.max(CLP) >= 5:
        plt.plot(TIMESTAMP[0:len(CLP)], CLP, label=find_id)
        plt.xlabel("Time", fontsize=10)
        plt.ylabel("Control Limit", fontsize=10)
        plt.legend(loc="upper right")

    TIME.clear()
    TIMESTAMP.clear()
    INTERVAL.clear()
    AVG_INTERVAL.clear()
    ACC_OFFSET.clear()
    OFFSET.clear()
    SKEW.clear()
    TEMP_T.clear()
    P.clear()
    G.clear()
    ERROR.clear()
    CLP.clear()
    CLM.clear()
    div.clear()
plt.show()
f.close

