# import the library
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import socket
import requests
import getpass

MAX_SIZE = 1048576
ds_addr = ("vega.ii.uam.es", 8000)
get_users = b"LIST_USERS"
quit = b"QUIT"
ds_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ds_sock.connect(ds_addr)
versions = "V1"
port = "15951" #Random, maybe we can ask the user for it

class VideoClient(object):

    def __init__(self, window_size):

        # Creamos una variable que contenga el GUI principal
        self.app = gui("Redes2 - P2P", window_size)
        self.app.setGuiPadding(10,10)

        # Preparación del interfaz
        self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
        self.app.addImage("video", "imgs/webcam.gif")

        self.app.startSubWindow("list", modal=True)
        self.app.setGeometry(400, 400)
        self.app.addLabel("lu", "Lista de Usuarios")
        self.app.addButtons(["OK"], self.buttonsCallback)
        self.app.stopSubWindow()

        # Registramos la función de captura de video
        # Esta misma función también sirve para enviar un vídeo
        self.cap = cv2.VideoCapture(0)
        self.app.setPollTime(20)
        self.app.registerEvent(self.capturaVideo)

        # Añadir los botones
        self.app.addButtons(["Usuarios", "Conectar", "Colgar", "Salir"], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2)

    def start(self):
        self.app.go()

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

    # Función que gestiona los callbacks de los botones
    def buttonsCallback(self, button):

        if button == "Salir":
            # Salimos de la aplicación
            ds_sock.sendall(quit)
            ds_sock.close()
            self.app.stop()
        elif button == "Conectar":
            # Entrada del nick del usuario a conectar
            nick = self.app.textBox("Conexión",
                "Introduce el nick del usuario a buscar")
            # Código para conectar con el usuario

        elif button == "Colgar":
            pass
        elif button == "Usuarios":
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
                #self.app.infoBox("Lista de usuarios", table)
                #self.app.addTable("Lista de Usuarios", table)
        elif button == "OK":
            self.app.hideSubWindow("list")
            self.app.removeGrid("Lista de Usuarios")

    def inCalling(usr):
        mess = "El usuario " + usr + " le está llamando. ¿Aceptar la llamada?"
        return self.app.yesNoBox("Llamada entrante", mess)



if __name__ == '__main__':

    vc = VideoClient("640x520")

    # Crear aquí los threads de lectura, de recepción y,
    # en general, todo el código de inicialización que sea necesario
    # ...
    nick = input("Introduce tu nick: ")
    passw = getpass.getpass("Introduce tu contraseña: ")
    pub_or_priv = None
    while pub_or_priv != "B" and pub_or_priv != "V":
        pub_or_priv = input("Introduce B para usar tu ip pública o V para usar tu ip privada: ")
    if pub_or_priv == "B":
        ip = requests.get("http://ipecho.net/plain?").text
    else:
        ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0],
        s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]    #Gotten from Stackoverflow
    message = "REGISTER " + nick + " " + ip + " " + port + " " + passw + " " + versions
    binm = bytes(message, "utf-8")
    ds_sock.sendall(binm)
    resp = ds_sock.recv(MAX_SIZE)
    if resp[:3].decode("utf-8") == "NOK":
        print("La contraseña introducida es incorrecta.")
        exit()
    print("Bienvenido " + nick + ", tu cuenta ha sido registrada o actualizada correctamente.")

    # Lanza el bucle principal del GUI
    # El control ya NO vuelve de esta función, por lo que todas las
    # acciones deberán ser gestionadas desde callbacks y threads
    vc.start()
