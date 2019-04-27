import socket as sck
import threading

class ControlLink:
    timeoutDelay = 60
    def __init__(self):
        # TCP peer socket
        self.peerSocket = None
        # TCP server socket
        self.svSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        # TCP server thread
        self.svThr = threading.Thread(target=self.tcpSv, daemon=True)
        # Connection info
        self.ownNick = None
        self.ownAddr = None
        self.udpInPort = None
        self.usrCalled = None
        self.udpOutPort = None
        self.alive=False
        self.busy = False
        self.busymtx = threading.Lock()

    def setNick(self, nick):
        self.ownNick = nick

    def setINET(self, addr, udpInPort):
        self.ownAddr = addr
        self.udpInPort = udpInPort

    def setDest(self, userCalled, udpOutPort):
        self.userCalled = userCalled
        self.udpOutPort = udpOutPort

    def hold(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_HOLD " + self.ownNick)

    def resume(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_RESUME " + self.ownNick)

    def call(self, addr):
        if self.getBusyState():
            return False
        self.toggleBusy()
        # TODO: Handle sck.timeout
        self.peerSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.peerSocket.settimeout(timeout)
        self.peerSocket.connect(addr)
        self.peerSocket.send(b"CALLING " + self.ownNick + b" " + self.udpInPort)
        resp = self.peerSocket.recv() # TODO: Handle invalid resp
        (cmd, nick, port) = resp.decode('ascii').split(' ')
        if cmd == "CALL_ACCEPTED":
            self.usrCalled = nick.encode('ascii')
            self.udpOutPort = port.encode('ascii')
            return True
        self.peerSocket.close()
        self.toggleBusy()
        return False

    def start(self, nick, addr, udpInPort):
        self.setNick(nick)
        self.setINET(addr, udpInPort)
        self.alive = True
        self.svSocket.bind(self.ownAddr)
        self.svThr.start()

    def tcpSv(self):
        self.svSocket.listen(5)
        while self.alive:
            (pSocket, pAddr) = self.svSocket.accept()
            if self.getBusyState():
                pSocket.send(b"CALL_BUSY")
                pSocket.close()
            else:
                self.toggleBusy()
                self.peerSocket = pSocket # TODO: THIS MIGHT NOT WORK
                # send signal to Main Thread

    def answerCall(self, answer):
        if answer:
            self.peerSocket.send(b"CALL_ACCEPTED " + self.ownNick + b" " + self.udpInPort)
        else:
            self.peerSocket.send(b"CALL_DENIED " + self.ownNick)
            self.peerSocket.close()
            self.peerSocket = None
            self.toggleBusy()

    def hang(self):
        self.peerSocket.send(b"CALL_END " + self.ownNick)
        self.peerSocket.close()
        self.peerSocket = None
        self.toggleBusy()

    def toggleBusy(self):
        self.busymtx.acquire()
        self.busy = not self.busy
        self.busymtx.release()

    def getBusyState(self):
        self.busymtx.acquire()
        ret = self.busy
        self.busymtx.release()
        return ret
