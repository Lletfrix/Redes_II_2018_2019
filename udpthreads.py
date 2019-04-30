import queue
import threading
import socket as sck

class UdpThreads:
    def __init__(self, bufferIn, bufferOut):
        # Connection info
        self.ip = None
        self.inPort = None
        self.outPort = None
        self.alive = None
        # Buffers
        self.bufferIn = bufferIn
        self.bufferOut = bufferOut
        # Locks
        self.lockIn = threading.Lock()
        self.lockOut = threading.Lock()
        # UDP Sockets
        self.udpInSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        self.udpOutSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)

        self.udpInSocket.setblocking(0)
        self.udpOutSocket.setblocking(0)
        # UDP Threads
        self.udpInThr = None
        self.udpOutThr = None

    def setINET(self, ip, udpInPort):
        self.ip = ip
        self.inPort = udpInPort
        self.udpInSocket.bind((ip, udpInPort))
        self.udpOutSocket.bind((ip, 0))

    def udpSend(self):
        while(self.alive):
            self.lockOut.acquire()
            try:
                data = self.bufferOut.get(block=False)
            except queue.Empty:
                self.lockOut.release()
                continue
            try:
                self.udpOutSocket.sendto(data, self.sendTo)
            except sck.error:
                self.lockOut.release()
                continue
            self.lockOut.release()

        try:
            self.lockOut.release()
        except threading.ThreadError:
            pass
        print("VOY A DEJAR DE ENVIAR")

    def udpRecv(self):
        while(self.alive):
            self.lockIn.acquire()
            try:
                data, sender = self.udpInSocket.recvfrom(1048576)
            except sck.error:
                self.lockIn.release()
                continue
            if sender[0] != self.sendTo[0]:
                self.lockIn.release()
                continue
            try:
                queueData = (int(data.split(b"#")[0]), data)
            except ValueError:
                self.lockIn.release()
                continue
            try:
                self.bufferIn.put(queueData, block=False)
            except queue.Full:
                self.lockIn.release()
                continue
            self.lockIn.release()

        try:
            self.lockIn.release()
        except threading.ThreadError:
            pass
        print("VOY A DEJAR DE RECIBIR")

    def hold(self):
        self.lockIn.acquire()
        self.lockOut.acquire()

    def resume(self):
        self.lockIn.release()
        self.lockOut.release()

    def start(self, peerInfo):
        if self.alive:
            return

        self.alive=True
        self.udpInThr = threading.Thread(target=self.udpRecv, daemon=True)
        self.udpOutThr = threading.Thread(target=self.udpSend, daemon=True)
        self.sendTo = peerInfo

        self.udpInThr.start()
        self.udpOutThr.start()

    def hang(self):
        self.alive=False
