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

MAX_SIZE = 1048576  #Máximo tamaño de lista de usuarios (1MB)
ds_addr = ("vega.ii.uam.es", 8000)  #Dirección del servidor de descubrimiento
get_users = b"LIST_USERS"   #Macros con comandos para el servidor
quit = b"QUIT"
ds_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ds_sock.connect(ds_addr)    #Creación de socket y conexión al servidor de descubrimiento
versions = "V0"     #Versiones soportadas
ipPrivada = None
ipPublica = None    #Declaramos las ip pública y privada como variable global
port = "15951"  #Puerto escogido para recibir tcp
udpInPort = 15851   #Puerto escogido para recibir udp
vc = None   #Declaramos el video client como variable global
imgManager = FrameHandler() #Creamos un FrameHandler(Se encargará de tratar los frames)

#Handler de la señal SIGINT o SIGUSR1(según sistema)
def newCallPetition(signum, frame):
    vc.inCalling()

#Definición de la clase VideoClient
class VideoClient(object):
    #Función de instanciación
    def __init__(self, window_size, bufferIn, bufferOut, udpConn, tcpCtrl):
        self.paused = False #Flag que representa si la llamada está en pausa o no
        self.ip = None  #Ip con la que se registra el usuario
        self.nick = None    #Nick con el que se registra el ususario
        self.pwd = None     #Contraseña con la que se registra el usuario
        self.bufferIn = bufferIn    #Buffer de recepción de frames
        self.bufferOut = bufferOut  #Buffer de salida de frames
        self.udpConn = udpConn  #Controlador de conexión UDP
        self.tcpCtrl = tcpCtrl  #Controlador de conexión TCP
        self.table = None   #Tabla de usuarios
        # Creamos una variable que contenga el GUI principal
        self.app = gui("Redes2 - P2P", window_size) #Inicializamos la gui
        self.app.setGuiPadding(10,10)

        # Preparación del interfaz
        self.app.addLabel("title", "Cliente Multimedia P2P")
        self.app.addImage("video", "imgs/webcam.gif")

        self.app.startSubWindow("list", modal=True)
        self.app.setGeometry(400, 400)
        self.app.addLabel("lu", "Lista de Usuarios")
        self.app.addButtons(["Cancelar", "Llamar"], self.buttonsCallback)
        self.app.stopSubWindow()    #Definimos la ventana y los botones de la lista de usuarios

        self.app.startSubWindow("inVideo", modal=True)
        self.app.setGeometry(640,520)
        self.app.addLabel("video", "Video entrante")
        self.app.addImage("peerCam", "imgs/webcam.gif")
        self.app.addButtons(["Colgar", "Pausar"], self.videoCallback)
        self.app.setPollTime(40)
        self.app.registerEvent(self.recibeVideo)    #Establecemos el polltime y la función de recepción de video
        self.app.stopSubWindow()    #Definimos la ventana y los botones del video entrante

        self.app.startSubWindow("login", modal=True)
        self.app.setGeometry(400, 200)
        self.app.addLabelEntry("Usuario")
        self.app.addLabelSecretEntry("Contraseña")
        self.app.addRadioButton("ipOption", "Privada")
        self.app.addRadioButton("ipOption", "Publica")
        self.app.setRadioButton("ipOption", "Privada")
        self.app.addNamedButton("Login/Registrar", "Login", self.loginButtons)
        self.app.addNamedButton("Salir", "SalirLog", self.loginButtons)
        self.app.stopSubWindow()    #Definimos la ventana y los botones de login
        # Registramos la función de captura de video
        # Esta misma función también sirve para enviar un vídeo
        self.cap = cv2.VideoCapture("timer.mp4")  #Capturamos la imagen de la webcam disponible
        self.app.setPollTime(40)
        self.app.registerEvent(self.capturaVideo)   #Establecemos el polltime y la función de captura de video

        # Añadir los botones
        self.app.addButtons(["Conectar", "Salir"], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2)

    def start(self):
        self.app.go(startWindow="login")    #Se inicializa la aplicación

    #Función que gestiona los callback de los botones de la ventana de login
    def loginButtons(self, button):

        if button == "Login":
            if self.app.getRadioButton("ipOption") == "Privada":
                self.ip = ipPrivada
            else:
                self.ip = ipPublica     #Establecemos la ip
            self.nick = self.app.getEntry("Usuario")
            self.pwd = self.app.getEntry("Contraseña")  #Establecemos el nick y la contraseña
            if self.doLogin() == True:
                self.udpConn.setINET(ipPrivada, udpInPort)
                self.tcpCtrl.start(self.nick.encode("ascii"), (ipPrivada.encode("ascii"), int(port)), udpInPort) #Bindeamos siempre el socket de escucha a la ip privada
                self.app.infoBox("Bienvenido", "Su cuenta se ha registrado o actualizado satisfactoriamente.")
                self.app.show() #Mostramos la pantalla principal del programa
                self.app.hideSubWindow("login") #Terminamos el login

        elif button == "SalirLog":
            ds_sock.sendall(quit)   #Notificamos al DS que nos vamos a desconectar
            ds_sock.close() #Cerramos el socket
            self.app.stop() #Si le da a salir, terminamos la ejecución

    #Función que registra un usuario en el servidor si no lo está, o actualiza su información si la contraseña es correcta
    def doLogin(self):
        message = "REGISTER " + self.nick + " " + self.ip + " " + port + " " + self.pwd + " " + versions    #Construimos el mensaje de registro
        binm = bytes(message, "ascii")
        ds_sock.sendall(binm)   #Enviamos el registro
        resp = ds_sock.recv(MAX_SIZE)
        if resp[:3].decode("ascii") == "NOK":
            self.app.warningBox("Error Registro", "La contraseña introducida es incorrecta.")
            return False    #Si el servidor devuelve NOK, informamos al usuario de que ha habido un error
        return True

    # Función que gestiona los callbacks de los botones
    def buttonsCallback(self, button):
        if button == "Salir":
            # Salimos de la aplicación
            ds_sock.sendall(quit)   #Notificamos al servidor que nos desconectamos
            ds_sock.close() #Cerramos el socket con el DS
            self.app.stop() #Cerramos la aplicación
        elif button == "Llamar":
            # Entrada del nick del usuario a conectar
            nick = self.app.textBox("Conexión",
                "Introduce el nick del usuario a llamar")

            data = self.getUsrDetails(nick) #Obtenemos todos los datos del ususario a llamar

            if data is None:    #Si no hay ningún usuario con ese nick, informamos
                self.app.infoBox("Error", "No hay ningún usuario con ese nick, revisa la lista.")
                return
            # Código para conectar con el usuario
            outAddr = (data[3], int(data[4]))   #Dirección del cliente
            if not tcpCtrl.call(outAddr):   #Si no se puede establecer la conexión, informamos
                self.app.infoBox("Error", "No ha sido posible realizar la conexión.")
            else:
                self.startCall()    #Si hemos podido conectar, comenzamos la llamada
            #tcpConnections.call(outAddr)
            #udpConn.start(peerAddr, peerPort)

        elif button == "Conectar":  #Rutina de conexión
            ds_sock.sendall(get_users)
            users = ds_sock.recv(MAX_SIZE)  #Obtenemos la lista de usuarios

            if users[:3] == b"NOK": #Si no hay ningún usuario registrado, informamos
                self.app.infoBox("Error", "No hay ningún usuario registrado")
            else:
                splitted = users[16:].decode("ascii").split("#")    #Con el 16 quitamos el header
                self.table = [["Nick", "IP", "Port"]]    #Primera fila de la tabla
                err = 0 #Contador de usuarios erroneos
                for i in range(len(splitted)-1):
                    aux_split = splitted[i].split() #Obtenemos los campos de cada usuario
                    if len(aux_split) < 3:  #Si tiene menos de tres campos es un error del DS, pero lo asumimos
                        err += 1    #Contador errores para indexar bien en la tabla
                        continue    #Pasamos al siguiente usuario
                    self.table.append([])
                    for j in range(3):
                        self.table[i+1-err].append(aux_split[j]) #Añadimos a la tabla los datos del usuario
                self.app.openSubWindow("list")
                self.app.addGrid("Lista de Usuarios", self.table, action=self.callByRow)    #Añadimos la grid a su SubWindow
                self.app.stopSubWindow()
                self.app.showSubWindow("list")  #Mostramos la SubWindow de la lista de usuarios
        elif button == "Cancelar":
            self.app.hideSubWindow("list")  #Escondemos la SubWindow
            self.app.removeGrid("Lista de Usuarios")    #Borramos la lista de usuarios

    #Función que llama a un usuario tras pulsar su botón en la lista de usuarios
    def callByRow(self, row):
        outAddr = (self.table[row+1][1], int(self.table[row+1][2]))  #Obtenemos la dirección de la tabla
        if not tcpCtrl.call(outAddr):   #Si no se puede establecer la conexión, informamos
            self.app.infoBox("Error", "No ha sido posible realizar la conexión.")
        else:
            self.startCall()

    #Función que gestiona los callback de los botones de gestión de la llamada
    def videoCallback(self, button, pressed=True):
        if button == "Pausar":
            if self.paused: #Si está en pausa
                if pressed:
                    tcpCtrl.resume()    #Si hemos sido nosotros los que hemos pulsado el botón, notificamos al otro
                udpConn.resume()    #Continuamos la emisión de frames
                self.app.setButton("Pausar", "Pausar") #Ponemos el botón a pausar
                self.paused = False #Cambiamos la flag de pausa
            else: # Si no está en pausa
                udpConn.hold()  #Pausamos la emisión de frames
                if pressed:
                    tcpCtrl.hold()  #Si hemos pulsado el botón nosotros, notificamos al otro
                self.app.setButton("Pausar", "Continuar")   #Ponemos el botón a continuar
                self.paused = True  #Cambiamos el flag de pausa

        elif button == "Colgar":
            udpConn.hang()  #Terminamos la emisión de frames
            if pressed: #Si lo hemos pulsado nosotros
                tcpCtrl.hang()  #Notificamos al otro que queremos colgar
            if self.paused: #Si estaba en pausa la llamada
                udpConn.resume()    #TODO
                self.app.setButton("Pausar", "Pausar")  #Cambiamos el botón a Pausar para la siguiente llamada
                self.paused = False #Cambiamos la flag de pausa
            self.app.hideSubWindow("inVideo")   #Escondemos la ventana de video entrante

    #Función que informa al usuario de que está recibiendo una llamada y le permite cogerla o rechazarla
    def inCalling(self):
        usr = self.tcpCtrl.getPeerNick().decode("ascii")    #Obtenemos el nick del llamador
        mess = "El usuario " + usr + " le está llamando. ¿Aceptar la llamada?"
        ans = self.app.yesNoBox("Llamada entrante", mess)   #Preguntamos al usuario si quiere coger la llamada
        self.tcpCtrl.answerCall(ans)
        if ans:
            self.startCall()    #En caso afirmativo, empezamos la comunicación

    #Función que encapsula la primitiva infoBox de appJar
    def infoBox(self, title, msg):
        self.app.infoBox(title, msg)

    #Función que obtiene los frames del buffer de entrada y los muestra en la ventana correspondiente
    def recibeVideo(self):
        try:    #Intentamos sacar del buffer y mostrar por pantalla
            data = self.bufferIn.get(block=False)[1]
            data = data.split(b"#", 4)
            headers, inetFrame = data[:-1], data[-1]
            guiFrame = imgManager.inet2GUI(inetFrame)   #Preparamos el frame
            self.app.setImageData("peerCam", guiFrame, fmt = 'PhotoImage')  #Lo mostramos en la gui
        except queue.Empty: #Si está vacía no hacemos nada
            pass
        cmd, flag = tcpCtrl.check() #TODO
        if cmd is not None:
            if flag != self.paused:
                self.videoCallback(cmd, False)
        #show

    # Función que captura el frame a mostrar en cada momento
    def capturaVideo(self):

        ret, frame = self.cap.read() # Capturamos un frame de la cámara o del vídeo

        inetFrame, guiFrame = imgManager.prepareFrame(frame)    #Lo preparamos para mostrar y enviar

        self.app.setImageData("video", guiFrame, fmt = 'PhotoImage')    # Lo mostramos en el GUI

        # Lo mandamos a enviar por UDP
        if not self.paused: #Si la llamada no está pausada
            try:
                self.bufferOut.put(inetFrame, block=False)  #Metemos el frame en el buffer de envio
            except queue.Full:  #Si la cola está llena, desechamos el frame
                pass
    # Establece la resolución de la imagen capturada
    def setImageResolution(self, resolution):   #TODO
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

    #Función que, dado un nick, obtiene todos los datos de dicho usuario del DS
    #input: usr Nick del usuarios
    #output: Lista con los datos del usuario, None si no se encuentra al usuario
    def getUsrDetails(self, usr):
        message = "QUERY " + usr
        binm = bytes(message, "ascii")
        ds_sock.sendall(binm)
        data = ds_sock.recv(MAX_SIZE)
        if(data[:3] == b"NOK"):
            return None
        return data.decode("ascii").split(" ")

    #Función que inicia una llamada
    def startCall(self):    #TODO
        self.udpConn.start(self.tcpCtrl.getDest())  #iniciar los hilos de UDP
        self.paused = False #Inicializamos la flag de pausa
        self.app.setButton("Pausar", "Pausar")  #Inicializamos el botón de pausa
        #self.udpThreads.start()
        #self.app.openSubWindow("inVideo")
        self.app.showSubWindow("inVideo")   #Mostramos la SubWindow del video entrante
        #espera por feedback de usuario
        #si hace pause - llamar a la funcion del modelo que envia la señal de pause
        #si cuelga - llama a la funcion del modelo que envia la señal de pause
        ##########   sale de la ejecución
        pass

if __name__ == '__main__':

    bufferIn = queue.Queue()
    bufferOut = queue.PriorityQueue()   #Inicializamos los buffers de frames

    udpConn = UdpThreads(bufferIn, bufferOut)
    tcpCtrl = ControlLink() #Inicializamos los controladores de TCP y UDP

    vc = VideoClient("640x520", bufferIn, bufferOut, udpConn, tcpCtrl)  #Inicializamos el VideoClient

    ipPublica = requests.get('https://api.ipify.org').text  #Obtenemos la IP pública de un servicio web
    #Código obtenido de w3resource.com Python Exercise 55 para obtener ip privada
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0],
    s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    ipPrivada = ip

    operatingSystem = platform.system()

    if operatingSystem == 'Linux' or operatingSystem == 'Darwin':   #Si el sistema es Linux o Darwin
        signal.signal(signal.SIGUSR1, newCallPetition)  #Usaremos la señal USR1
    elif operatingSystem == 'Windows':  #Si es Windows
        signal.signal(signal.SIGINT, newCallPetition)   #Usaremos la señal SIGINT
    # Lanza el bucle principal del GUI
    # El control ya NO vuelve de esta función, por lo que todas las
    # acciones deberán ser gestionadas desde callbacks y threads
    vc.start()
