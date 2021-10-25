from datetime import datetime
from factorfinder import factorfinder
import random

def DateTime4Log():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    del now
    return dt_string

def PrintList(pnumberlength):
    global file2
    for j in range(0, pnumberlength):
        file2.write(str(i_hor[j]).zfill(pnumberlength) + "\n")
        print(str(i_hor[j]).zfill(pnumberlength))
    file2.write("---- " + DateTime4Log() + " ----\n")
    print("---- " + DateTime4Log() + " ----")

def LegalFirst(pnumber, pnumberlength):
    s = str(pnumber).zfill(pnumberlength)
    if s.find("0") > -1:
        return False
    else:
        return True

def Derive_i_ver(pnumberlength):
    global i_hor
    global i_ver

    s = []
    cs = []

    for j in range(0, pnumberlength):
        s.append("")
        cs.append("")

    for j in range(0, pnumberlength):
        s[j] = str(i_hor[j]).zfill(pnumberlength)

    for j1 in range(0, pnumberlength):
        cs[j1] = ""
        for j2 in range(0, pnumberlength):
            cs[j1] = cs[j1] + s[j2][j1]
    
    for j in range(0, pnumberlength):
        i_ver[j] = int(cs[j])

def OneRandomTransPrimeList(pnumberlength):
    global i_hor
    global i_ver


    for j in range(0, pnumberlength - 4):
        n = n_start

        while not ((j > 0 or LegalFirst(n, pnumberlength) == True) and myfactorfinder.IsPrime(n) == True):
            n = random.randint(n_start, n_end + 1)
        
        i_hor[j] = n

    Derive_i_ver(pnumberlength)

    for j in range(0, pnumberlength - 4):
        n = i_ver[j]
        while not ((j > 0 or LegalFirst(n, pnumberlength) == True) and myfactorfinder.IsPrime(n) == True):
            n = random.randint(i_ver[j], i_ver[j] + (10 ** 4))

        for j2 in range(pnumberlength - 4, pnumberlength):
            s = str(n).zfill(pnumberlength)
            myd = int(s[j2])
            i_hor[j2] = i_hor[j2] + (myd * (10 ** (pnumberlength - (j + 1))))


    for i1 in range(1, 10000):
        if myfactorfinder.IsPrime(i_hor[pnumberlength - 4] + i1) == True:
            for i2 in range(1, 10000):
                if myfactorfinder.IsPrime(i_hor[pnumberlength - 3] + i2) == True:
                    print(str(i1) + "," + str(i2) + "," + DateTime4Log())
                    for i3 in range(1, 10000):
                        if myfactorfinder.IsPrime(i_hor[pnumberlength - 2] + i3) == True:
                            for i4 in range(0, 10000):
                                if myfactorfinder.IsPrime(i_hor[pnumberlength - 1] + i4) == True:
                                    i_hor[pnumberlength - 4] += i1
                                    i_hor[pnumberlength - 3] += i2
                                    i_hor[pnumberlength - 2] += i3
                                    i_hor[pnumberlength - 1] += i4
                                    Derive_i_ver(pnumberlength)
                                    if (myfactorfinder.IsPrime(i_ver[pnumberlength - 4]) == True and
                                        myfactorfinder.IsPrime(i_ver[pnumberlength - 3]) == True and
                                        myfactorfinder.IsPrime(i_ver[pnumberlength - 2]) == True and
                                        myfactorfinder.IsPrime(i_ver[pnumberlength - 1]) == True):
                                        print("Found one !!")
                                        PrintList(pnumberlength)
                                    i_hor[pnumberlength - 4] -= i1
                                    i_hor[pnumberlength - 3] -= i2
                                    i_hor[pnumberlength - 2] -= i3
                                    i_hor[pnumberlength - 1] -= i4
    


global file2
global AttemptCounter

AttemptCounter = 0

myfactorfinder = factorfinder()

file1 = open("TransPrimeListBatchInput.txt", 'r')
Lines = file1.readlines()
file1.close()

mynumberlength = int(Lines[0])

i_hor = []
i_ver = []
for j in range(0, mynumberlength):
    i_hor.append(0)
    i_ver.append(0)

n_start = 10 ** (mynumberlength - 1)
n_end = (10 ** mynumberlength) - 1

file2 = open("TransPrimeListBatchOutput.txt", 'w')
file3 = open("TransPrimeListBatchOutput.log", 'w')
file3.write("Started\n")
file3.close()

OneRandomTransPrimeList(mynumberlength)

file2.close()
