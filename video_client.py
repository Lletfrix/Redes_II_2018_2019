# import the library
from appJar import gui
from PIL import Image, ImageTk
from controllink import *
from udpthreads import *
import numpy as np
import cv2
import socket
import requests
import getpass
import queue

MAX_SIZE = 1048576
ds_addr = ("vega.ii.uam.es", 8000)
get_users = b"LIST_USERS"
quit = b"QUIT"
ds_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ds_sock.connect(ds_addr)
versions = "V1"
ipPrivada = None
ipPublica = None
port = "15951" #Random, maybe we can ask the user for it
udpInPort = 15851
class VideoClient(object):

    def __init__(self, window_size, bufferIn, bufferOut, udpConn, tcpCtrl):

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
        self.app.addButtons(["Colgar", "Pausar"], self.buttonsCallback)
        self.app.setPollTime(20)
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
        self.app.setPollTime(20)
        self.app.registerEvent(self.capturaVideo)

        # Añadir los botones
        self.app.addButtons(["Conectar", "Salir"], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2)

    def start(self):
        self.app.go(startWindow="login")

    # Función que captura el frame a mostrar en cada momento
    def capturaVideo(self):

        # Capturamos un frame de la cámara o del vídeo
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (640,480))
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

        # Lo mostramos en el GUI
        self.app.setImageData("video", img_tk, fmt = 'PhotoImage')

        # Aquí tendría que el código que envia el frame a la red
        # ...

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
            outAddr = (data[3], int(data[4]))
            #tcpConnections.call(outAddr)
            #udpConn.start(peerAddr, peerPort)
        elif button == "Colgar":
            pass
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
                self.app.showSubWindow("list")
        elif button == "Cancelar":
            self.app.hideSubWindow("list")
            self.app.removeGrid("Lista de Usuarios")

    def inCalling(self, usr):
        mess = "El usuario " + usr + " le está llamando. ¿Aceptar la llamada?"
        return self.app.yesNoBox("Llamada entrante", mess)

    def infoBox(self, title, msg):
        self.app.infoBox(title, msg)

    def recibeVideo(self):
        try:
            self.bufferIn.get(block=False)
            tcpConnections.check()

        except queue.Empty:
            pass
        #show

    def getUsrDetails(self, usr):
        message = "QUERY " + usr
        binm = bytes(message, "ascii")
        ds_sock.sendall(binm)
        data = ds_sock.recv(MAX_SIZE)
        if(data[:3] == b"NOK"):
            return None
        return data.decode("ascii").split(" ")

    def startCall():
        #iniciar los hilos de UDP

        self.udpThreads.start()
        self.app.openSubWindow("inVideo")
        #espera por feedback de usuario
        #si hace pause - llamar a la funcion del modelo que envia la señal de pause
        #si cuelga - llama a la funcion del modelo que envia la señal de pause
        self.app.hideSubWindow("inVideo")
        ##########   sale de la ejecución
        pass

if __name__ == '__main__':

    bufferIn = queue.Queue()
    bufferOut = queue.Queue()

    udpConn = UdpThreads(bufferIn, bufferOut)
    tcpCtrl = ControlLink()

    vc = VideoClient("640x520", bufferIn, bufferOut, udpConn, tcpCtrl)

    ipPublica = requests.get('https://api.ipify.org').text
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0],
    s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]    #Gotten from Stackoverflow
    ipPrivada = ip

    # Lanza el bucle principal del GUI
    # El control ya NO vuelve de esta función, por lo que todas las
    # acciones deberán ser gestionadas desde callbacks y threads
    vc.start()
