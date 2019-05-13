import socket as sck
import threading
import signal
import os
import platform

#Macros
RECV_SZ = 4096
timeoutDelay = 60
class ControlLink:
    def __init__(self):
        #Sistema operativo en el que se está ejecutando el programa
        self.operatingSystem = platform.system()
        self.peerSocket = None # TCP peer socket
        self.peerPort = None # Puerto del usuario con quien nos conectamos
        self.peerAddr = None # IP del usuario con quien nos conectamos
        self.usrCalled = None   #Nick del usuario con quien nos conectamos
        # Socket del servidor TCP
        self.svSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.svSocket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)
        # Thread del servidor TCP
        self.svThr = threading.Thread(target=self.tcpSv, daemon=True)

        self.ownNick = None
        self.ownAddr = None
        self.udpInPort = None   #Puerto UDP de recepción
        self.alive=False    #Estado del thread de recepción TCP
        self.busy = False   #Flag ocupado/no ocupado
        self.busymtx = threading.Lock()

    #Getter de la dirección (IP, puerto) del peer
    #output Tupla IP, Puerto del peer
    def getDest(self):
        return (self.peerAddr, self.peerPort)

    #Getter del nick del peer
    #output Nick del peer
    def getPeerNick(self):
        return self.usrCalled

    #Setter del nick del peer
    #input nick Nick del peer
    def setNick(self, nick):
        self.ownNick = nick

    #Setter de la dirección (IP, puerto) UDP propios
    #input addr Dirección IP propia, udpInPort Puerto de recepción UDP
    def setINET(self, addr, udpInPort):
        self.ownAddr = addr
        self.udpInPort = udpInPort

    #Setter del nick y dirección (IP, puerto) del peer
    #input usrCalled Nick del peer, peerPort Puerto del peer,
    #      peerAddr IP del peer
    def setDest(self, usrCalled, peerPort, peerAddr):
        self.usrCalled = usrCalled
        self.peerPort = peerPort
        self.peerAddr = peerAddr

    #Función que llamará a un peer
    #input addr Tupla (IP, Puerto) a la que llamar
    def call(self, addr):
        #Error si ya estamos en llamada
        if self.getBusyState():
            return False
        #Si no, actualizamos la flag de ocupado
        self.toggleBusy()
        # Creamos socket para llamar
        self.peerSocket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.peerSocket.settimeout(timeoutDelay)
        #Intentamos establecer la conexión y llamar
        try:
            self.peerSocket.connect(addr)
            self.peerSocket.send(b"CALLING " + self.ownNick + b" " + str(self.udpInPort).encode('ascii'))
            resp = self.peerSocket.recv(RECV_SZ)
            (cmd, nick, port) = resp.decode('ascii').split(' ')
        except (sck.timeout, ConnectionError, ValueError, OSError):
            self.toggleBusy()
            return False #Si ha habido errores de socket o conexión, error
        #Si nos responde con CALL_ACEPTED, establecemos la comunicación
        if cmd == "CALL_ACCEPTED":
            self.setDest(nick.encode('ascii'), int(port), addr[0])
            return True
        #Si no, cerramos la conexión y actualizamos la flag de ocupado
        self.peerSocket.close()
        self.toggleBusy()
        return False

    #Función que inicia el servidor de escucha
    #input nick Nick del usuario de la app, addr Dirección del usuario de la app,
    #      udpInPort Puerto de recepción UDP
    def start(self, nick, addr, udpInPort):
        self.setNick(nick)
        self.setINET(addr, udpInPort)
        self.alive = True
        self.svSocket.bind(self.ownAddr)
        self.svThr.start()  #Iniciamos el thread de recepción TCP

    #Rutina del thread del servidor de recepción TCP
    def tcpSv(self):
        self.svSocket.listen(5) #Escuchamos 5 conexiones como máximo (Las de busy son rápidas)
        while self.alive:
            (pSocket, pAddr) = self.svSocket.accept()
            #Si estamos en llamada, devolvemos CALL_BUSY y cerramos conexión
            if self.getBusyState():
                try:
                    pSocket.send(b"CALL_BUSY")
                except ConnectionError:
                    pass

                pSocket.close()
            #Si no estamos en llamada
            else:
                self.toggleBusy()
                self.peerSocket = pSocket # TODO: THIS MIGHT NOT WORK
                self.peerSocket.settimeout(timeoutDelay) #TODO: Reduce time
                #Intentamos recibir comando
                try:
                    data = self.peerSocket.recv(RECV_SZ)
                #Si hay timeout cerramos la conexión
                except (sck.timeout, ConnectionError):
                    self.peerSocket.close()
                    self.peerSocket = None
                    self.toggleBusy()
                    return
                #Miramos si el comando recibido tiene la estructura apropiada
                try:
                    (cmd, nick, udpInPort) = data.decode("ascii").split(" ")
                #Si no, cerramos conexión
                except ValueError:
                    self.peerSocket.close()
                    self.peerSocket = None
                    self.toggleBusy()
                    return
                #Si el comando es CALLING
                if cmd == "CALLING":
                    self.setDest(nick.encode("ascii"), int(udpInPort), pAddr[0])
                    #Señalizamos al usuario que le están llamando
                    if self.operatingSystem == 'Windows':
                        os.kill(os.getpid(), signal.CTRL_C_EVENT)
                    elif self.operatingSystem == 'Linux' or operatingSystem == 'Darwin':
                        os.kill(os.getpid(), signal.SIGUSR1)

    #Función que recibe el input del usuario a la solicitud de llamada y actúa en consecuencia
    #input answer Valor lógico dado por el usuario (Aceptar/Rechazar llamada)
    def answerCall(self, answer):
        #Si la acepta, notificamos al peer de que la hemos aceptado
        if answer:
            try:
                self.peerSocket.send(b"CALL_ACCEPTED " + self.ownNick + b" " + str(self.udpInPort).encode("ascii"))
            except ConnectionError:
                pass
        #Si no, avisamos al peer que la hemos rechazado y cerramos la conexión
        else:
            try:
                self.peerSocket.send(b"CALL_DENIED " + self.ownNick)
            except ConnectionError:
                pass
            self.peerSocket.close()
            self.peerSocket = None
            self.toggleBusy()

    #Función que, dado un comando recibido, comprueba si es correcto y actúa en consecuencia
    def check(self):
        #Si no hay peerSocket, no hay ni siquiera conexión
        if self.peerSocket is None:
            return None, None
        self.peerSocket.settimeout(0)
        #Intentamos recibir comando
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

    #Función que envía el comando CALL_HOLD al peer
    def hold(self):
        try:
            self.peerSocket.send(b"CALL_HOLD " + self.ownNick)
        except ConnectionError:
            pass

    #Función que envía el comando CALL_RESUME al peer
    def resume(self):
        try:
            self.peerSocket.send(b"CALL_RESUME " + self.ownNick)
        except ConnectionError:
            pass

    #Función que envía el comando CALL_END al peer y cierra la conexión
    def hang(self):
        try:
            self.peerSocket.send(b"CALL_END " + self.ownNick)
        except ConnectionError:
            pass
        self.peerSocket.close()
        self.peerSocket = None
        self.toggleBusy()

    #Función que cambia el valor lógico de la flag de ocupado por su opuesto
    def toggleBusy(self):
        self.busymtx.acquire()
        self.busy = not self.busy
        print("El estado de busy es:", self.busy)
        self.busymtx.release()

    #Función que devuelve el valor de la flag de ocupado
    #output Valor lógico de la flag de ocupado
    def getBusyState(self):
        self.busymtx.acquire()
        ret = self.busy
        self.busymtx.release()
        return ret
