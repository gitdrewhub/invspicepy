###############################
import subprocess
import numpy as np
import shutil
import re
import math

tphl_prev = 0
tphl_next = 0


def getTPprev():
    p = subprocess.Popen(["hspice", "InvChain1.sp"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    print(" *** Running hspice InvChain1.sp command ***\n", output)

    Data = np.recfromcsv("InvChain1.mt0.csv", comments="$", skip_header=3)
    print(Data["tphl_inv"])
    tphl_prev = Data["tphl_inv"]
    return tphl_prev


def getTPnext():
    p = subprocess.Popen(["hspice", "InvChain1.sp"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    print(" *** Running hspice InvChain1.sp command ***\n", output)

    Data = np.recfromcsv("InvChain1.mt0.csv", comments="$", skip_header=3)
    print(Data["tphl_inv"])
    tphl_next = Data["tphl_inv"]
    return tphl_next


def varyfan(invFile1, invFile2):
    f = open(invFile1, 'r')
    f1 = open(invFile2, 'w')
    f = open('InvChain1.sp', 'r')
    f1 = open('InvChain2.sp', 'w')
    fannumber = 0
    for line in f:
        match = re.search(r'(param\sfan\s=\s)(\d+)', line)
        if match:
            numbertxt = match.group(2)
            fannumber = int(numbertxt)
            newnumber = int(numbertxt) + 1
            newnumbertxt = str(newnumber)
            line = re.sub(r'\d+', newnumbertxt, line)
            f1.write(line)
        else:
            f1.write(line)

    f.close()
    f1.close()

    return fannumber


def varyN(beta, index, invFile1, invFile2):
    f = open(invFile1, 'r')
    f1 = open(invFile2, 'w')
    index = int(index)
    beta = int(beta)

    for line in f:
        match = re.search(r'^X', line)
        if match:
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M=' + str(
                    int(beta ** (0))) + '\n'
            f1.write(line)
            for j in np.arange(1, index - 1, 1):
                line = 'Xinv' + str(int(j + 1)) + ' ' + str(int(j + 1)) + ' ' + str(int(j + 2)) + ' inv M=' + str(
                    int(beta ** (j))) + '\n'
                f1.write(line)

            line = 'Xinv' + str(index) + ' ' + str(index) + ' z inv M=' + str(int(beta ** (index-1))) + '\n'
            f1.write(line)
    f.close()
    f1.close()


R = 50
shutil.copyfile('InvChain.sp', 'InvChain1.sp')
shutil.copyfile('InvChain1.sp', 'InvChain2.sp')
shutil.copyfile('InvChain1.sp', 'InvChain3.sp')

#tpPrev = getTPprev()
#tpOriginal = tpPrev

#########First Iteration
#varyfan('InvChain1.sp', 'InvChain2.sp')
#shutil.copyfile('InvChain2.sp', 'InvChain1.sp')
####################
#tpNext = getTPnext()




'''






##while loop
while tpNext < tpPrev:
    R = varyfan('InvChain1.sp', 'InvChain2.sp')
    shutil.copyfile('InvChain2.sp', 'InvChain1.sp')
    tpPrev = tpNext
    tpNext = getTPnext()

N = math.floor(np.log(R))
#N = N + (N % 2)
fan = math.floor(R ** (1 / N))
varyN(fan, N, 'InvChain3.sp', 'InvChain1.sp')
tpNext = getTPnext()
tpPrev = tpOriginal
'''
Nfinal=1
fan=2

tpNextN=0.999
tpPrevN=1
tpNextF=0.999
tpPrevF=1





f = open('comments.txt', 'w')
N = 1
tpPrevF = getTPprev()
while tpNextN < tpPrevN:
    tpPrevN = tpNextN

    varyN(fan, N + 2, 'InvChain1.sp', 'InvChain2.sp')
    N += 2

    shutil.copyfile('InvChain2.sp', 'InvChain1.sp')

    tpNextN = getTPnext()
    if N > 15:
        break

tpNextF = getTPnext()
fan += 1
line = 'Initial while: tpPrevF = ' + str(tpPrevF) + ' tpNextF = ' + str(tpNextF) + '\n'
f.write(line)
f.close()

tpNextN=0.999
tpPrevN=1
while tpNextF < tpPrevF:
    f = open('comments.txt', 'w')
    N=1
    fan += 1
    tpPrevF=tpNextF
    while tpNextN < tpPrevN:
        tpPrevN = tpNextN

        varyN(fan, N+2, 'InvChain1.sp', 'InvChain2.sp')
        N += 2

        shutil.copyfile('InvChain2.sp', 'InvChain1.sp')

        tpNextN = getTPnext()
        if N>100:
            break

        line='N='+str(N)+'\n'
        f.write(line)

    tpNextF = getTPnext()

    line = str(fan-1)+ 'Iteration While: tpPrevF = ' + str(tpPrevF) + ' tpNextF = ' + str(tpNextF) + '\n'
    f.write(line)
    f.close()

varyN(fan - 1, N-2, 'InvChain2.sp', 'InvChain1.sp')


# Problem: while loop (F) won't run a 2nd time. >>>>>   [tpNextF<tpPrevF]
# 0.999 < 6.071 e -10
# Compare data types