import time
import cv2
import numpy as np
from PIL import Image, ImageTk

#Definición de resoluciones admitidas
hQ = (640, 480)
mQ = (320, 240)
lQ = (160, 120)
class FrameHandler:
    def __init__(self):
        self.fps = 25   #FPS de video recibido
        #self.res = "HIGH"
        self.res = str(hQ[0])+"x"+str(hQ[1])   #Calidad del video recibido
        self.ratio = 50    #Ratio de compresión
        self.order = 0  #Número de secuencia

    # Función que prepara un frame para ser enviado por UDP y para ser mostrado en la gui
    # input frame Frame a ser procesado
    # output frame para ser enviado y frame para ser mostrado
    def prepareFrame(self, frame):
        message = str(self.order)+'#'+str(time.time())+'#'+self.res+'#'+str(self.fps)+'#'
        message = message.encode('ascii')   #Construimos la cabecera
        frame = self.resizeFrame(frame)
        guiFrame = self.frameFormat(frame)  #Se formatea para ser mostrado en la gui
        inetFrame = self.compress(frame)    #Se comprime para ser enviado por UDP
        if inetFrame is None:
            return None #Si hay error al comprimir, no enviamos a internet
        self.order += 1 #Incrementamos el número de secuencia
        return message+inetFrame, guiFrame

    # Función que ajusta el tamaño de un frame
    # input frame Frame a ser ajustado
    # output frame ajustado
    def resizeFrame(self, frame):
        return cv2.resize(frame, self._res2tuple(self.res))
    # Función que formatea el frame para ser mostrado por la gui
    # input frame Frame a ser formateado
    # output frame formateado
    def frameFormat(self, frame):
        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        return ImageTk.PhotoImage(Image.fromarray(cv2_im))

    # Función que prepara un frame recibido por UDP para mostrarlo por la gui
    # input inetFrame Frame recibido de otro usuario
    # output frame formateado
    def inet2GUI(self, inetFrame):
        frame = self.decompress(inetFrame)
        return self.frameFormat(frame)

    # Función que comprime un frame y lo devuelve en bytes
    # input frame Frame a comprimir
    # output frame comprimido en bytes
    def compress(self, frame):
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.ratio]
        result, encimg = cv2.imencode('.jpg', frame, encode_param)  #Comprime según el ratio establecido
        if result == False:
            return None
        return encimg.tobytes()

    # Función que descomprime un frame
    # input frame Frame a descomprimir
    # output frame descomprimido
    def decompress(self, frame):
        return cv2.imdecode(np.frombuffer(frame,np.uint8),1)

    # Setter del campo FPS
    # input fps Nuevo fps
    def updateFps(self, fps):
        self.fps = fps

    # Setter del ratio de compresión
    # input ratio Nuevo ratio de compresión
    def updateRatio(self, ratio):
        self.ratio = ratio

    # Reset del contador del número de secuencia
    def resetCount(self):
        self.order = 0

    def _res2tuple(self, res):
        return tuple([int(i) for i in res.split('x')])
