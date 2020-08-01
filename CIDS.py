from matplotlib import pyplot as plt
import numpy as np
import matplotlib

matplotlib.style.use('ggplot')
path = "D:\\Idle_4243.asc"

# CAN ID : 45개 (0 ~ 44), 단위 : ms
CAN_ID = [['42 ', 1000], ['43 ', 1000], ['44 ', 1000]]
    #['34 ', 1000], ['42 ', 1000], ['43 ', 1000], ['44 ', 1000], ['5A0', 1000], ['5A2', 1000], 
    #['50 ', 200], ['120', 200], ['5F0', 200], ['517', 200], ['18 ', 200], ['51A', 200],
    #['690', 100], ['2C0', 100], ['587', 100], ['59B', 100], ['5E4', 100], ['A1 ', 100], ['A0 ', 100], ['510', 100], ['4F1', 100], ['110', 100], 
    #['350', 20], ['1F1', 20], ['382', 20], ['4F0', 20], ['4B1', 20], ['4F2', 20], ['4B0', 20], 
    #['260', 10], ['220', 10], ['2A0', 10], ['2B0', 10], ['165', 10], ['164', 10],  ['316', 10], ['153', 10], ['329', 10], 
    #['370', 10], ['545', 10], ['43F', 10], ['440', 10], ['81 ', 10], ['18F', 10], ['80 ', 10]
    #]
    #['2C0', 1000], ['5A0', 1000], ['5A2', 1000]
    #['180', 1000], ['340', 1000], ['500', 1000], ['110', 20], ['120', 1000], ['510', 1000], ['517', 1000]

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
X = []
Y = []
ERROR = []
N = 20

P = []
SKEW = []

lamb = 0.9995
G = []

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

    # Get Average Timestamp Interval (uTn)
    for i in range(round((len(TIME)-N)/N)):
        TIMESTAMP.append(sum(TIME[0+N*i : N+N*i])/N)
        AVG_INTERVAL.append(round(sum(INTERVAL[ 0+N*i : N+N*i ])/N, 6)) 
    
    for i in range(len(AVG_INTERVAL)):
        offset = (sum(TIME[1+20*i:20+20*i])/19) - (10 * AVG_INTERVAL[i]) - TIME[0 + 20*i]
        #OFFSET.append(abs(offset))
        OFFSET.append(offset)
        
    for i in range(len(OFFSET)):
        temp_acc = temp_acc + OFFSET[i]
        ACC_OFFSET.append(round(temp_acc,10))

    for i in range(round(len(ACC_OFFSET)/20)):
        TEMP_T.append(TIMESTAMP[i*20])
    #    skew = ACC_OFFSET[i*20] / TIMESTAMP[i*20]
    #    SKEW.append(skew) 


    for i in range(len(TIME)):
        gain = ((1/lamb) * P[i] * TIME[i]) / (1 + (1/lamb) * TIME[i] * TIME[i] * P[i])
        p = (1/lamb)*(P[i] - gain * TIME[i] * P[i])
        G.append(gain)
        P.append(p)
    #print(P)
    #print(G)

    #if (len(SKEW) != 0):
    #    plt.plot(TIMESTAMP, ACC_OFFSET, label=find_id)
    #    plt.legend()
    #    print(ACC_OFFSET[-1])
    
    print(len(ACC_OFFSET), len(P), len(G), len(TIME), len(TIMESTAMP))


    for i in range(len(ACC_OFFSET)):
        err = ACC_OFFSET[i] - (SKEW[i] * TIMESTAMP[i])
        ERROR.append(err)
        SKEW.append(SKEW[i] + (G[i] * err))

    if (find_id == "43 "):
        X = list(OFFSET)
    if (find_id == "44 "):
        Y = list(OFFSET)
    #plt.plot(TIMESTAMP, SKEW[0:len(TIMESTAMP)], label=find_id)
    #plt.xlabel("Time", fontsize=10)
    #plt.ylabel("Skew", fontsize=10)
    #plt.legend()

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

COR = np.corrcoef(X[0:900], Y[0:900])
print(COR[0][1])

plt.scatter(X, Y)
plt.title(round(COR[0][1], 5), fontsize=12)
plt.xlabel('Accumulated Offset of 0x43', fontsize=12)
plt.ylabel('Accumulated Offset of 0x44', fontsize=12)
plt.show()
f.close

