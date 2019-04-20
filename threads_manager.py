import threading
import socket as sck
MAX_SIZE = 1048576

class receptionSV:

    def __init__(self, nick, ip, port, controller):
        self.nick = nick.encode('ascii')
        self.ip = ip
        self.port = port
        self.controller = controller
        self.alive = True
        self.busy = False
        self.busymtx = Lock()
        self.tcpThr = threading.Thread(target=tcpRec, daemon=True, args=(self))
        # TCP reception socket
        self.tcpSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.tcpSocket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)
        # UDP reception socket
        self.udpInSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)

    def toggleBusy(self):
        self.busymtx.acquire()
        self.busy = not self.busy
        self.busymtx.release()

    def getBusyState(self):
        self.busymtx.acquire()
        ret = self.busy
        self.busymtx.release()
        return ret

    def tcpRec(self):
        self.tcpSocket.bind((self.ip, self.port))
        self.tcpSocket.listen(5)
        while(self.alive):
            peerSocket, peerAddr = self.tcpSocket.accept()
            if(self.getBusyState()):
                peerSocket.send(b"CALL_BUSY")
                peerSocket.close()
            else:
                self.toggleBusy()
                data = self.recv(MAX_SIZE).decode("ascii").split(" ")
                accept = self.controller.inCalling(data[1])
                if(accept):
                    peerSocket.send(b"CALL_ACCEPT "+ self.nick)
                    ## Establecer Llamada
                else
                    peerSocket.send(b"CALL_DENY "+ self.nick)
                    peerSocket.close()

    def start(self):
        # Start TCP listening
        self.tcpThr.start()

    def kill(self):
        self.alive=False
