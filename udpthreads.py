import Queue
import threading
import socket as sck

class UdpThreads:
    def __init__(self, bufferIn, bufferOut, ip, inPort, outPort):
        # Connection info
        self.ip = ip
        self.inPort = inPort
        self.outPort = outPort
        self.peerAddr = (None, None)
        self.alive = None
        # Buffers
        self.bufferIn = bufferIn
        self.bufferOut = bufferOut
        # Locks
        self.lockIn = threading.Lock()
        self.lockOut = threading.Lock()
        # UDP Sockets
        self.udpInSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        self.updInSocket.bind((ip, inPort))
        self.udpOutSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        self.updOutSocket.bind((ip, outPort))
        # UDP Threads
        self.udpInThr = None
        self.udpOutThr = None

    def udpSend(self):
        while(self.alive):
            lockOut.acquire()

            data = self.bufferOut.get()
            self.udpOutSocket.sendto(data, self.sendTo)

            lockOut.release()

        try:
            lockOut.release()
        except ThreadError:
            pass

    def udpRecv(self):
        while(self.alive):
            lockIn.acquire()

            data, sender = self.udpInSocket.recvfrom()
            if sender[0] is not self.peerAddr[0]:
                continue
            self.bufferIn.put(data)

            lockIn.release()

        try:
            lockIn.release()
        except ThreadError:
            pass

    def pause(self):
        self.lockIn.acquire()
        self.lockOut.acquire()

    def resume(self):
        self.lockIn.release()
        self.lockOut.release()

    def start(self, peerAddr, peerPort):
        if self.alive:
            return

        self.alive=True
        self.udpInThr = threading.Thread(target=udpRecv, daemon=True, args=(self))
        self.udpOutThr = threading.Thread(target=udpSend, daemon=True, args=(self))
        self.sendTo = (peerAddr, peerPort)
        self.udpInThr.start()
        self.udpOutThr.start()

    def hang(self):
        self.alive=False
