import socket
import select
import pickle
import time
from packet import *

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

UDP_IP = socket.gethostname()
IN_PORT = int(sys.argv[1])
UDP_PORT = int(sys.argv[2])
buf = 33792

def data_receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, IN_PORT))
    f = []
    filename = []
    sequenceWritten = []
    for i in range(3, len(sys.argv)):
        filename.append(str(sys.argv[i]))
        f.append(open(sys.argv[i], 'wb'))
        sequenceWritten.append([None])
    timeout = 10
    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            print("Receiving data...")
            data, addr = sock.recvfrom(buf)
            datar = pickle.loads(data)
            if(datar.dataType == DATA and datar.checksum == checksum(datar.packet)):
                sock2.sendto(pickle.dumps(Packet(ACK, datar.dataId, datar.sequenceNumber, None, None, None)), (UDP_IP, UDP_PORT))
                for i in range(0, len(filename)):
                    if(datar.dataId == i and datar.sequenceNumber not in sequenceWritten[i]):
                        print("Writing %s..." % filename[i])
                        f[i].write(datar.packet)
                        sequenceWritten[i].append(datar.sequenceNumber)
                        print()
            elif(datar.dataType == FIN and datar.checksum == checksum(datar.packet)):
                sock2.sendto(pickle.dumps(Packet(FIN_ACK, datar.dataId, datar.sequenceNumber, None, None, None)), (UDP_IP, UDP_PORT))
                for i in range(0, len(filename)):
                    if(datar.dataId == i and datar.sequenceNumber not in sequenceWritten[i]):
                        print("Writing %s..." % filename[i])
                        f[i].write(datar.packet)
                        sequenceWritten[i].append(datar.sequenceNumber)
                        print("%s Finish!" % filename[i])
                        f[i].close()
                        print()
        else:
            break
        timeout = 2
    sock2.close()
print("Receiver host name : ", UDP_IP)
input("Press enter to continue...")
data_receive()