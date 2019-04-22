import threading
import cv2
import socket as sck
import time as time
MAX_SIZE = 1048576

class receptionSV:

    def __init__(self, nick, ip, port, passw, controller):
        self.nick = nick.encode('ascii')
        self.ip = ip
        self.port = port
        self.passw = passw
        self.controller = controller
        self.alive = True
        self.busy = False
        self.busymtx = Lock()
        self.versions = "V1"
        self.workingVer = None
        self.pause = False
        self.finished = False
        self.destUdpPort = None
        self.dsSock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.dsSock.connect(("vega.ii.uam.es", 8000))
        self.tcpThr = threading.Thread(target=tcpRec, daemon=True, args=(self))
        # TCP reception socket
        self.tcpSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.tcpSocket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)
        self.peerSocket = None
        # UDP reception socket
        self.udpInSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        self.udpOutSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)

    def toggleBusy(self):
        self.busymtx.acquire()
        self.busy = not self.busy
        self.busymtx.release()

    def getBusyState(self):
        self.busymtx.acquire()
        ret = self.busy
        self.busymtx.release()
        return ret

    def regOrUpdUsr(self):
        message = "REGISTER " + self.nick.decode("ascii") + " " + self.ip + " " + self.port + " " + self.passw + " " + self.versions
        binm = bytes(message, "ascii")
        self.dsSock.sendall(binm)
        return self.dsSock.recv(MAX_SIZE)

    def getLstUsrs(self):
        self.dsSock.sendall(b"LIST_USERS")
        users = self.dsSock.recv(MAX_SIZE)
        table = [["Nick", "IP", "Port"]]
        if users[:2] == b"OK":
            users = users[14:]  #Con el 13 quitamos el header fijo
            while(users[0] != b" "):
                users = users[1:]
            users = users[1:]      #Con esto quitamos el número de usuarios
            splitted = users.decode("ascii").split("#")

            for i in range(len(splitted)-1):
                aux_split = splitted[i].split()
                table.append([])
                for j in range(3):
                    table[i+1].append(aux_split[j])
        return table

    def getUsrDetails(self, usr):
        message = "QUERY " + usr
        binm = bytes(message, "ascii")
        self.dsSock.sendall(binm)
        data = self.dsSock.recv(MAX_SIZE)
        if(data[3:] == b"NOK"):
            return None
        return data[:14].decode("ascii").split(" ") #Quitamos el header y nos devuelve los datos en una lista

    def establCall(self, usr):
        if self.getBusyState() is True:
            return False    #Check
        self.toggleBusy() #Avisar también al tcp de escucha
        details = self.getUsrDetails(self, usr)
        if details is None:
            return False    #Check
        ourVers = self.versions.split("#").reverse()
        theirVers = details[3].split("#").reverse() #Ordenamos por "altura" de versión
        for oVer in ourVers:
            for tVer in theirVers:
                if oVer.lower() == tVer.lower():  #Case insensitive
                    self.workingVer = oVer
                    break
        if self.workingVer is None:
            return False    #Check
        self.peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peerSocket.connect((details[1],details[2]))   #TODO Check exception
        init_message = "CALLING " + self.nick.decode("ascii") + self.port
        init_message = bytes(init_message, "ascii")
        self.peerSocket.sendall(init_message)
        status = self.peerSocket.recv(MAX_SIZE)
        if status[:13] is b"CALL_ACCEPTED":
            self.peerIp = details[1]
            self.usrCalled = usr.tobytes()
            splitted = status[:15].split(" ")
            self.destUdpPort = splitted[1]
            self.call()
            return
        if status[:11] is b"CALL_DENIED":
            self.controller.infoBox("Llamada rechazada", "El usuario ha rechazado la llamada")
            return

    def sendFrame(self, frame):
        if self.usrCalled is None or self.destUdpPort is None:
            return
        mess = str(i) + "#" + str(time.time()) + "#" + "Resol" + "#" + "FPS" + "#" + frame
        self.udpOutSocket.sendto(mess, (self.peerIp, self.destUdpPort))

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
                self.usrCalled = data[1].tobytes()
                self.destUdpPort = int(data[2])
                accept = self.controller.inCalling(self.usrCalled)
                if(accept):
                    peerSocket.send(b"CALL_ACCEPT "+ self.nick)
                    self.call()
                    while self.finished is False:
                        data = peerSocket.recv(MAX_SIZE)
                        if data[:9] == b"CALL_HOLD" + self.usrCalled:
                            self.pause = True
                        if data[:11] == b"CALL_RESUME " + self.usrCalled:
                            self.pause = False
                        if data[:8] == b"CALL_END " + self.usrCalled:
                            self.finished = True
                else:
                    peerSocket.send(b"CALL_DENIED "+ self.nick)
                    peerSocket.close()

    def call():
        i = 0
        if self.finished is True:
            self.usrCalled = None
            self.destUdpPort = None
            self.peerSocket.close()
            self.peerSocket = None
            return
        while self.pause is False:
            self.sendFrame(self.getFrame())
            time.sleep(0.01666)  #60 fps aprox

    def start(self):
        # Start TCP listening
        self.tcpThr.start()

    def getFrame():
        ret, frame = self.controller.cap.read()
        encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
        result,encimg = cv2.imencode('.jpg',img,encode_param)
        return encimg.tobytes()

    def recvFrame(self):
        data = self.udpInSocket.recvfrom(MAX_SIZE).split("#")
        #Ignoramos cabeceras de momento
        decframe = cv2.imdecode(np.frombuffer(data[-1],np.uint8), 1)
        return cv2.cvtColor(decframe,cv2.COLOR_BGR2RGB)

    def kill(self):
        self.alive=False
