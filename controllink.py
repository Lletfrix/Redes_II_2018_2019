import socket as sck
import threading
import signal
import os
import platform

RECV_SZ = 4096
timeoutDelay = 60
class ControlLink:
    def __init__(self):
        #Operating System
        self.operatingSystem = platform.system()
        # TCP peer socket
        self.peerSocket = None
        self.peerPort = None
        self.peerAddr = None
        self.usrCalled = None
        # TCP server socket
        self.svSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        # TCP server thread
        self.svThr = threading.Thread(target=self.tcpSv, daemon=True)
        # Connection info
        self.ownNick = None
        self.ownAddr = None
        self.udpInPort = None
        self.alive=False
        self.busy = False
        self.busymtx = threading.Lock()

    def getDest(self):
        return (self.peerAddr, self.peerPort)

    def getPeerNick(self):
        return self.usrCalled

    def setNick(self, nick):
        self.ownNick = nick

    def setINET(self, addr, udpInPort):
        self.ownAddr = addr
        self.udpInPort = udpInPort

    def setDest(self, usrCalled, peerPort, peerAddr):
        self.usrCalled = usrCalled
        self.peerPort = peerPort
        self.peerAddr = peerAddr

    def call(self, addr):
        if self.getBusyState():
            return False
        self.toggleBusy()
        # TODO: Handle sck.timeout
        self.peerSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.peerSocket.settimeout(timeoutDelay)
        try:
            self.peerSocket.connect(addr)
            self.peerSocket.send(b"CALLING " + self.ownNick + b" " + str(self.udpInPort).encode('ascii'))
            resp = self.peerSocket.recv(RECV_SZ) # TODO: Handle invalid resp
            (cmd, nick, port) = resp.decode('ascii').split(' ')
        except sck.timeout:
            return False
        except ConnectionError:
            return False

        if cmd == "CALL_ACCEPTED":
            self.setDest(nick.encode('ascii'), int(port), addr[0])
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
            print("ACEPTAR")
            (pSocket, pAddr) = self.svSocket.accept()
            if self.getBusyState():
                pSocket.send(b"CALL_BUSY")
                pSocket.close()
            else: # I'm free to be called
                self.toggleBusy()
                self.peerSocket = pSocket # TODO: THIS MIGHT NOT WORK
                self.peerSocket.settimeout(timeoutDelay) #TODO: Reduce time
                print("RECIBIR CALLING")
                try:
                    data = self.peerSocket.recv(RECV_SZ)
                except sck.timeout:
                    self.peerSocket.close()
                    self.peerSocket = None
                    self.toggleBusy()
                    return
                print("DECODIFICAR CALLING")
                try:
                    (cmd, nick, udpInPort) = data.decode("ascii").split(" ")
                except ValueError:
                    self.peerSocket.close()
                    self.peerSocket = None
                    self.toggleBusy()
                    return
                if cmd == "CALLING":
                    print("ENVIAR SEÑAL")
                    self.setDest(nick.encode("ascii"), int(udpInPort), pAddr[0])
                    # send signal to Main Thread
                    if self.operatingSystem == 'Windows':
                        os.kill(os.getpid(), signal.CTRL_C_EVENT)
                    elif self.operatingSystem == 'Linux' or operatingSystem == 'Darwin':
                        os.kill(os.getpid(), signal.SIGUSR1)

    def answerCall(self, answer):
        if answer:
            self.peerSocket.send(b"CALL_ACCEPTED " + self.ownNick + b" " + str(self.udpInPort).encode("ascii"))
        else:
            self.peerSocket.send(b"CALL_DENIED " + self.ownNick)
            self.peerSocket.close()
            self.peerSocket = None
            self.toggleBusy()

    def check(self):
        if self.peerSocket is None:
            return None, None
        self.peerSocket.settimeout(0)
        try:
            data = self.peerSocket.recv(RECV_SZ)
        except sck.error:
            data  = b"NONE NONE"
        self.peerSocket.settimeout(timeoutDelay)
        try:
            (cmd, nick) = data.decode('ascii').split(' ')
        except ValueError:
            cmd = data.decode('ascii')
        if cmd == "CALL_END":
            return "Colgar", None
        elif cmd == "CALL_HOLD":
            return "Pausar", True
        elif cmd == "CALL_RESUME":
            return "Pausar", False
        return None, None

    def hold(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_HOLD " + self.ownNick)

    def resume(self):
        # TODO: Handle errors
        self.peerSocket.send(b"CALL_RESUME " + self.ownNick)

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
