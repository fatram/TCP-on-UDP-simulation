import socket
import time
import sys
import os
import pickle
import select
from math import ceil as ceil
from packet import *

UDP_IP = socket.gethostbyname(sys.argv[1])
UDP_PORT = 5005
IN_PORT = 6006
timeout = 5

def progress_bar(length, percentage):
    print("|", end = "")
    for i in range(int(percentage*length/100)):
        print("#", end = "")
    for i in range(int(percentage*length/100), length):
        print(" ", end = "")
    print("| " + str(percentage) + "%")


def carry_around_add(num_1, num_2):
    c = num_1 + num_2
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    """Compute and return a checksum of the given data"""
    value = int.from_bytes(msg, byteorder='big')
    lth = len(msg)
    if len(msg) % 2:
        value = value << 1
        lth += 1
    msg = value.to_bytes(lth, byteorder='big')
    
    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + (msg[i + 1] << 8)
        s = carry_around_add(s, w)
    return s

buf = 32768

def data_transfer():
    file_name = []
    i = 2
    while(i < len(sys.argv)):
        file_name.append(sys.argv[i])
        i += 1

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind((UDP_IP, IN_PORT))
    tempId = 0b0000

    data = []
    datanext = [None]*len(file_name)
    seqnum = []
    datas = []
    datasend = []
    f = []
    numofpacket = []

    for i in range(0, len(file_name)):
        numofpacket.append(ceil(os.path.getsize(file_name[i])/32768))
        seqnum.append(0b0001)
        f.append(open(file_name[i], "rb"))
        dt = f[i].read(buf)
        data.append(dt)
        if(data[i]):
            datanext[i] = f[i].read(buf)

    while(True):
        os.system('cls' if os.name == 'nt' else 'clear')
        for i in range(0, len(file_name)):
            if(seqnum[i] >= numofpacket[i]):
                print("Sending %s..." % file_name[i])
                print("%d of %d" % (numofpacket[i], numofpacket[i]))
                progress_bar(50, 100)
                print()
                print("FIN-ACK")
                print()
            if(data[i]):
                if(not(datanext[i])):
                    datas = Packet(FIN, i, seqnum[i], sys.getsizeof(data[i]), checksum(data[i]), data[i])
                else:
                    datas = Packet(DATA, i, seqnum[i], sys.getsizeof(data[i]), checksum(data[i]), data[i])
                datasend = pickle.dumps(datas)
                if(sock.sendto(datasend, (UDP_IP, UDP_PORT))):
                    print("Sending %s..." % file_name[i])
                    print("%d of %d" % (seqnum[i], numofpacket[i]))
                    progress_bar(50, ceil(seqnum[i]*100/numofpacket[i]))
                    print()
                    ready = select.select([sock2], [], [], timeout)
                    dtar = Packet(None, None, None, None, None, None)
                    if(ready[0]):
                        dta, adr = sock2.recvfrom(1024)
                        dtar = pickle.loads(dta)
                        if(dtar is None):
                            sock.sendto(datasend, (UDP_IP, UDP_PORT))
                            print("Sending %s..." % file_name[i])
                            print("%d of %d" % (seqnum[i], numofpacket[i]))
                            progress_bar(50, ceil(seqnum[i]*100/numofpacket[i]))
                            print()
                            dta, adr = sock2.recvfrom(1024)
                        else:
                            while(dtar.dataType != ACK and dtar.dataType != FIN_ACK):
                                sock.sendto(datasend, (UDP_IP, UDP_PORT))
                                print("Sending %s..." % file_name[i])
                                print("%d of %d" % (seqnum[i], numofpacket[i]))
                                progress_bar(50, ceil(seqnum[i]*100/numofpacket[i]))
                                print()
                                dta, adr = sock2.recvfrom(1024)
                    if(dtar.dataType == ACK):
                        print("ACK")
                        data[i] = datanext[i]
                        seqnum[i] += 1
                        datanext[i] = f[i].read(buf)
                    elif(dtar.dataType == FIN_ACK):
                        print("FIN-ACK")
                        data[i] = datanext[i]
                        seqnum[i] += 1
                        datanext[i] = f[i].read(buf)
                    print()
            else:
                if(f[i]):
                    f[i].close()
                    f[i] = None
        count = 0
        for i in range(0, len(file_name)):
            if(f[i] is None):
                count += 1
        if(count == len(file_name)):
            break
    sock.close()

    """for filename in file_name:
        seqnum = 0b0000
        print("Sending %s ..." % filename)
        f = open(filename, "rb")
        data = f.read(buf)
        while(data):
            datanext = f.read(buf)
            if(not(datanext)):
                datas = Packet(FIN, tempId, seqnum, sys.getsizeof(data), checksum(data), data)
            else:
                datas = Packet(DATA, tempId, seqnum, sys.getsizeof(data), checksum(data), data)
            datasend = pickle.dumps(datas)
            if(sock.sendto(datasend, (UDP_IP, UDP_PORT))):
                print("Sending...")
                datas.printPacket()
                print()
                time.sleep(0.5) # Give receiver a bit time to save
                ready = select.select([sock2], [], [], timeout)
                if(ready[0]):
                    dta, adr = sock2.recvfrom(4096)
                    dtar = pickle.loads(dta)
                    if(dtar is None):
                        sock.sendto(datasend, (UDP_IP, UDP_PORT))
                        print("Sending...")
                        datas.printPacket()
                        print()
                        dta, adr = sock2.recvfrom(4096)
                    else:
                        while(dtar.dataType != ACK and dtar.dataType != FIN_ACK):
                            sock.sendto(datasend, (UDP_IP, UDP_PORT))
                            print("Sending...")
                            datas.printPacket()
                            print()
                            dta, adr = sock2.recvfrom(4096)
                if(dtar.dataType == ACK):
                    print("ACK")
                elif(dtar.dataType == FIN_ACK):
                    print("FIN-ACK")
                print()
                seqnum += 1
            data = datanext
        tempId += 1

    sock.close()
    f.close()"""

data_transfer()