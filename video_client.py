# import the library
from appJar import gui
from PIL import Image, ImageTk
from controllink import *
from udpthreads import *
from frame_handler import *
import numpy as np
import cv2
import socket
import requests
import getpass
import queue
import signal
import platform

MAX_SIZE = 1048576
ds_addr = ("vega.ii.uam.es", 8000)
get_users = b"LIST_USERS"
quit = b"QUIT"
ds_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ds_sock.connect(ds_addr)
versions = "V0"
ipPrivada = None
ipPublica = None
port = "15951" #Random, maybe we can ask the user for it
udpInPort = 15851
vc = None
imgManager = FrameHandler()

def newCallPetition(signum, frame):
    vc.inCalling()

class VideoClient(object):

    def __init__(self, window_size, bufferIn, bufferOut, udpConn, tcpCtrl):
        self.paused = False
        self.ip = None
        self.nick = None
        self.pwd = None
        self.bufferIn = bufferIn
        self.bufferOut = bufferOut
        self.udpConn = udpConn
        self.tcpCtrl = tcpCtrl
        # Creamos una variable que contenga el GUI principal
        self.app = gui("Redes2 - P2P", window_size)
        self.app.setGuiPadding(10,10)

        # Preparación del interfaz
        self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
        self.app.addImage("video", "imgs/webcam.gif")

        self.app.startSubWindow("list", modal=True)
        self.app.setGeometry(400, 400)
        self.app.addLabel("lu", "Lista de Usuarios")
        self.app.addButtons(["Cancelar", "Llamar"], self.buttonsCallback)
        self.app.stopSubWindow()

        self.app.startSubWindow("inVideo", modal=True)
        self.app.setGeometry(640,520)
        self.app.addLabel("video", "Video entrante")
        self.app.addImage("peerCam", "imgs/webcam.gif")
        self.app.addButtons(["Colgar", "Pausar"], self.videoCallback)
        self.app.setPollTime(40)
        self.app.registerEvent(self.recibeVideo)
        self.app.stopSubWindow()

        self.app.startSubWindow("login", modal=True)
        self.app.setGeometry(400, 200)
        self.app.addLabelEntry("Usuario")
        self.app.addLabelSecretEntry("Contraseña")
        self.app.addRadioButton("ipOption", "Privada")
        self.app.addRadioButton("ipOption", "Publica")
        self.app.setRadioButton("ipOption", "Privada")
        self.app.addNamedButton("Login/Registrar", "Login", self.loginButtons)
        self.app.addNamedButton("Salir", "SalirLog", self.loginButtons)
        self.app.stopSubWindow()
        # Registramos la función de captura de video
        # Esta misma función también sirve para enviar un vídeo
        self.cap = cv2.VideoCapture(0)
        self.app.setPollTime(40)
        self.app.registerEvent(self.capturaVideo)

        # Añadir los botones
        self.app.addButtons(["Conectar", "Salir"], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2)

    def start(self):
        self.app.go(startWindow="login")

    def loginButtons(self, button):

        if button == "Login":
            if self.app.getRadioButton("ipOption") == "Privada":
                self.ip = ipPrivada
            else:
                self.ip = ipPublica
            self.nick = self.app.getEntry("Usuario")
            self.pwd = self.app.getEntry("Contraseña")
            if self.doLogin() == True:
                self.udpConn.setINET(ipPrivada, udpInPort)
                self.tcpCtrl.start(self.nick.encode("ascii"), (ipPrivada.encode("ascii"), int(port)), udpInPort)
                self.app.infoBox("Bienvenida", "Su cuenta se ha registrado o actualizado satisfactoriamente.")
                self.app.show()
                self.app.hideSubWindow("login")

        elif button == "SalirLog":
            ds_sock.sendall(quit)
            ds_sock.close()
            self.app.stop()

    def doLogin(self):
        message = "REGISTER " + self.nick + " " + self.ip + " " + port + " " + self.pwd + " " + versions
        binm = bytes(message, "ascii")
        ds_sock.sendall(binm)
        resp = ds_sock.recv(MAX_SIZE)
        if resp[:3].decode("ascii") == "NOK":
            self.app.warningBox("Error Registro", "La contraseña introducida es incorrecta.")
            return False
        return True

    # Función que gestiona los callbacks de los botones
    def buttonsCallback(self, button):

        if button == "Salir":
            # Salimos de la aplicación
            ds_sock.sendall(quit)
            ds_sock.close()
            self.app.stop()
        elif button == "Llamar":
            # Entrada del nick del usuario a conectar
            nick = self.app.textBox("Conexión",
                "Introduce el nick del usuario a llamar")

            data = self.getUsrDetails(nick)

            if data is None:
                self.app.infoBox("Error", "No hay ningún usuario con ese nick, revisa la lista.")
                return
            # Código para conectar con el usuario
            outAddr = (data[3].encode("ascii"), int(data[4]))
            if not tcpCtrl.call(outAddr):
                self.app.infoBox("Error", "No ha sido posible realizar la conexión.")
            else:
                self.startCall()
            #tcpConnections.call(outAddr)
            #udpConn.start(peerAddr, peerPort)
        elif button == "Conectar":
            ds_sock.sendall(get_users)
            users = ds_sock.recv(MAX_SIZE)

            if users[:3] == b"NOK":
                self.app.infoBox("Error", "No hay ningún usuario registrado")
            else:
                splitted = users[16:].decode("utf-8").split("#")    #Con el 16 quitamos el header
                table = [["Nick", "IP", "Port"]]
                for i in range(len(splitted)-1):
                    aux_split = splitted[i].split()
                    table.append([])
                    for j in range(3):
                        table[i+1].append(aux_split[j])
                self.app.openSubWindow("list")
                self.app.addGrid("Lista de Usuarios", table)
                self.app.stopSubWindow()
                self.app.showSubWindow("list")
        elif button == "Cancelar":
            self.app.hideSubWindow("list")
            self.app.removeGrid("Lista de Usuarios")

    def videoCallback(self, button, pressed=True):
        if button == "Pausar":
            if self.paused: # Continue
                if pressed:
                    tcpCtrl.resume()
                udpConn.resume()
                self.app.setButton("Pausar", "Pausar")
                self.paused = False
            else: # Pause
                udpConn.hold()
                if pressed:
                    tcpCtrl.hold()
                self.app.setButton("Pausar", "Continuar")
                self.paused = True

        elif button == "Colgar":
            print("VOY A COLGAR")
            udpConn.hang()
            if pressed:
                tcpCtrl.hang()
            if self.paused:
                udpConn.resume()
                self.app.setButton("Pausar", "Pausar")
                self.paused = False
            self.app.hideSubWindow("inVideo")

    def inCalling(self):
        usr = self.tcpCtrl.getPeerNick().decode("ascii")
        mess = "El usuario " + usr + " le está llamando. ¿Aceptar la llamada?"
        ans = self.app.yesNoBox("Llamada entrante", mess)
        self.tcpCtrl.answerCall(ans)
        if ans:
            self.startCall()


    def infoBox(self, title, msg):
        self.app.infoBox(title, msg)

    def recibeVideo(self):
        try:
            data = self.bufferIn.get(block=False)[1]
            headers, inetFrame = data[:-1], data[-1]
            guiFrame = imgManager.inet2GUI(inetFrame)
            # Lo mostramos en el GUI
            self.app.setImageData("peerCam", guiFrame, fmt = 'PhotoImage')
        except queue.Empty:
            pass
        cmd, flag = tcpCtrl.check()
        if cmd is not None:
            if flag != self.paused:
                self.videoCallback(cmd, False)
        #show

    # Función que captura el frame a mostrar en cada momento
    def capturaVideo(self):

        # Capturamos un frame de la cámara o del vídeo
        ret, frame = self.cap.read()

        inetFrame, guiFrame = imgManager.prepareFrame(frame)

        # Lo mostramos en el GUI
        self.app.setImageData("video", guiFrame, fmt = 'PhotoImage')

        # Lo mandamos a enviar por UDP
        if not self.paused:
            try:
                self.bufferOut.put(inetFrame, block=False)
            except queue.Full:
                pass
    # Establece la resolución de la imagen capturada
    def setImageResolution(self, resolution):
        # Se establece la resolución de captura de la webcam
        # Puede añadirse algún valor superior si la cámara lo permite
        # pero no modificar estos
        if resolution == "LOW":
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
        elif resolution == "MEDIUM":
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        elif resolution == "HIGH":
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def getUsrDetails(self, usr):
        message = "QUERY " + usr
        binm = bytes(message, "ascii")
        ds_sock.sendall(binm)
        data = ds_sock.recv(MAX_SIZE)
        if(data[:3] == b"NOK"):
            return None
        return data.decode("ascii").split(" ")

    def startCall(self):
        #iniciar los hilos de UDP
        self.udpConn.start(self.tcpCtrl.getDest())
        self.paused = False
        self.app.setButton("Pausar", "Pausar")
        #self.udpThreads.start()
        #self.app.openSubWindow("inVideo")
        self.app.showSubWindow("inVideo")
        #espera por feedback de usuario
        #si hace pause - llamar a la funcion del modelo que envia la señal de pause
        #si cuelga - llama a la funcion del modelo que envia la señal de pause
        ##########   sale de la ejecución
        pass

if __name__ == '__main__':

    bufferIn = queue.Queue()
    bufferOut = queue.PriorityQueue()

    udpConn = UdpThreads(bufferIn, bufferOut)
    tcpCtrl = ControlLink()

    vc = VideoClient("640x520", bufferIn, bufferOut, udpConn, tcpCtrl)

    ipPublica = requests.get('https://api.ipify.org').text
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0],
    s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]    #Gotten from Stackoverflow
    ipPrivada = ip

    operatingSystem = platform.system()

    if operatingSystem == 'Linux' or operatingSystem == 'Darwin':
        signal.signal(signal.SIGUSR1, newCallPetition)
    elif operatingSystem == 'Windows':
        signal.signal(signal.SIGINT, newCallPetition)
    # Lanza el bucle principal del GUI
    # El control ya NO vuelve de esta función, por lo que todas las
    # acciones deberán ser gestionadas desde callbacks y threads
    vc.start()
