import socket as sck
import threading

class ControlLink:
    timeoutDelay = 60
    def __init__(self, ownAddr):
        # TCP peer socket
        peerSocket = None
        # TCP server socket
        svSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        svSocket.bind((ownAddr))
        # TCP server thread
        svThr = threading.Thread(target=tcpSv, daemon=True, args=(self))
        # Connection info
        udpInPort = udpInPort
        usrCalled = None
        udpOutPort = None
        alive=False
        self.busy = False
        self.busymtx = Lock()

    def hold(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_HOLD" + self.usrCalled)

    def resume(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_RESUME " + self.usrCalled)

    def setDest(self, userCalled, udpOutPort):
        self.userCalled = userCalled
        self.udpOutPort = udpOutPort

    def call(self, addr, userCalled, udpOutPort):
        if self.getBusyState():
            return False
        self.toggleBusy()
        # TODO: Handle sck.timeout
        self.setDest(userCalled, updOutPort)
        self.peerSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.peerSocket.settimeout(timeout)
        self.peerSocket.connect(addr)
        self.peerSocket.send(b"CALLING " + self.userCalled + b" " + self.udpInPort)
        resp = self.peerSocket.recv()
        (cmd, nick, port) = resp.decode('ascii').split(' ')
        if cmd == "CALL_ACCEPTED":
            self.usrCalled = nick.encode('ascii')
            self.port = port.encode('ascii')
            return True
        self.peerSocket.close()
        self.toggleBusy()
        return False

    def start(self):
        self.alive = True
        svThr.start()

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
            self.peerSocket.send(b"CALL_ACCEPTED " + self.usrCalled + b" " + self.udpInPort)
        else:
            self.peerSocket.send(b"CALL_DENIED " + nick)
            self.peerSocket.close()
            self.peerSocket = None
            self.toggleBusy()

    def hang(self):
        self.peerSocket.send(b"CALL_END " + self.usrCalled)
        self.peerSocket.shutdown(SHUT_RDWR)
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
