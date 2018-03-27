
###############################
import subprocess
import numpy as np
import shutil
import re
import math

tphl_prev=0
tphl_next=0







def getTPprev():
    p=subprocess.Popen(["hspice","InvChain1.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()
    print(" *** Running hspice InvChain1.sp command ***\n", output)
    
    Data = np.recfromcsv("InvChain1.mt0.csv",comments="$",skip_header=3)
    print(Data["tphl_inv"])
    tphl_prev = Data["tphl_inv"]    
    return tphl_prev


def getTPnext():
    p=subprocess.Popen(["hspice","InvChain1.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()
    print(" *** Running hspice InvChain1.sp command ***\n", output)

    Data = np.recfromcsv("InvChain1.mt0.csv",comments="$",skip_header=3)
    print(Data["tphl_inv"])
    tphl_next = Data["tphl_inv"]
    return tphl_next



def varyfan():
    f = open('InvChain1.sp', 'r')
    f1 = open('InvChain2.sp','w')
    fannumber=0
    for line in f:
        match = re.search(r'(param\sfan\s=\s)(\d)',line)
        if match: 
            numbertxt = match.group(2)
            fannumber=int(numbertxt)
            newnumber = int(numbertxt) + 1
            newnumbertxt = str(newnumber)
            line = re.sub(r'\d',newnumbertxt,line)
            f1.write(line)
        else:
            f1.write(line)
    
    f.close()
    f1.close()
    
    shutil.copyfile('InvChain2.sp', 'InvChain1.sp') 
    return fannumber



def varyN(beta, index):
    f = open('InvChain1.sp', 'r')
    f1 = open('InvChain2.sp','w')
    index=int(index)
    beta=int(beta)

    for line in f:
        match = re.search(r'^X',line)
        if match: 
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M='+str(beta)+'\n'
            f1.write(line)
            for j in np.arange(1,index-1,1):
                line = 'Xinv'+str(int(j+1))+' '+str(int(j+1))+' '+str(int(j+2))+' inv M=pow('+str(beta)+','+str(int(j+1))+')\n'
                f1.write(line)
            
            line = 'Xinv'+str(index+1)+' '+str(index+1)+' z inv M=pow('+str(beta)+','+str(index+1)+')\n'
            f1.write(line)
    f.close()
    f1.close()

    shutil.copyfile('InvChain2.sp', 'InvChain1.sp') 








R=50
tpPrev=getTPprev()
tpOriginal=tpPrev
#########First Iteration
varyfan()
####################
tpNext=getTPnext()



##while loop
while tpNext < tpPrev:
    R=varyfan()
    tpPrev = tpNext
    tpNext= getTPnext()



N=math.floor(np.log(R))
fan=math.floor(R**(1/N))
varyN(fan,N)
tpNext=getTPnext()
tpPrev=tpOriginal

while tpNext < tpPrev:
    varyN(fan,N)
    N+=2
    tpPrev = tpNext
    tpNext= getTPnext()
    
    






