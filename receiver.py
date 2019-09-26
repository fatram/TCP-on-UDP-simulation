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

UDP_IP = "127.0.0.1"
IN_PORT = 5005
UDP_PORT = 6006
timeout = 5
buf = 33792


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))
f = []
filename = []
for i in range(1, len(sys.argv)):
    filename.append(str(sys.argv[i]))
    f.append(open(sys.argv[i], 'wb'))

while True:
    ready = select.select([sock], [], [], timeout)
    if ready[0]:
        print("Receiving data...")
        data, addr = sock.recvfrom(buf)
        datar = pickle.loads(data)
        if(datar.dataType == DATA and datar.checksum == checksum(datar.packet)):
            sock2.sendto(pickle.dumps(Packet(ACK, datar.dataId, datar.sequenceNumber, 0, 0, None)), (UDP_IP, UDP_PORT))
            for i in range(0, len(filename)):
                if(datar.dataId == i):
                    print("Writing %s..." % filename[i])
                    f[i].write(datar.packet)
                    print()
        elif(datar.dataType == FIN and datar.checksum == checksum(datar.packet)):
            sock2.sendto(pickle.dumps(Packet(FIN_ACK, datar.dataId, datar.sequenceNumber, 0, 0, None)), (UDP_IP, UDP_PORT))
            for i in range(0, len(filename)):
                if(datar.dataId == i):
                    print("Writing %s..." % filename[i])
                    f[i].write(datar.packet)
                    print("%s Finish!" % filename[i])
                    f[i].close()
                    print()
        time.sleep(0.5)
    else:
        break
sock2.close()