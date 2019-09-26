import sys

DATA = 0x0
ACK = 0x1
FIN = 0x2
FIN_ACK = 0x3

class Packet:
    def __init__(self, dataType, dataId, sequenceNumber, length, checksum, packet):
        self.dataType = dataType
        self.dataId = dataId
        self.sequenceNumber = sequenceNumber
        self.length = sys.getsizeof(packet)
        self.checksum = checksum
        self.packet = packet
    def printPacket(self):
        print("Data type : ", self.dataType)
        print("Data Id : ", self.dataId)
        print("Sequence number : ", self.sequenceNumber)
        print("Packet length : ", self.length)
        print("Checksum : ", self.checksum)