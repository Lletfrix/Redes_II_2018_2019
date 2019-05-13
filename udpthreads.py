import queue
import threading
import socket as sck

class UdpThreads:
    def __init__(self, bufferIn, bufferOut):
        # Información de la conexión
        self.ip = None  #Ip a la que bindear nuestros sockets
        self.inPort = None  #Puerto UDP de recepción
        self.outPort = None
        self.alive = None   #Indicador del estado de la llamada
        # Buffers
        self.bufferIn = bufferIn
        self.bufferOut = bufferOut
        # Locks
        self.lockIn = threading.Lock()
        self.lockOut = threading.Lock()
        # UDP Sockets
        self.udpInSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        self.udpOutSocket = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        # Sockets no bloqueantes
        self.udpInSocket.setblocking(0)
        self.udpOutSocket.setblocking(0)
        # UDP Threads
        self.udpInThr = None
        self.udpOutThr = None

    # Función que configura los sockets y las variables para la conexión
    # input: ip a la que bindear los socket de UDP
    #       udpInPort Puerto de recepción de UDP
    def setINET(self, ip, udpInPort):
        self.ip = ip
        self.inPort = udpInPort
        self.udpInSocket.bind((ip, udpInPort))
        self.udpOutSocket.bind((ip, 0)) #Para enviar, escogemos un puerto aleatorio libre

    # Función que envía frames UDP mientras que la llamada no esté en pausa y
    # haya frames en el buffer de salida
    def udpSend(self):
        while(self.alive):  #Mientras la llamada esté "viva"
            self.lockOut.acquire()  #Bajamos el mutex
            self.lockOut.release()
            try:
                data = self.bufferOut.get(block=False)  #Obtenemos un frame del buffer de envío
            except queue.Empty: #Si la cola está vacía
                #self.lockOut.release()  #Subimos el mutex
                continue
            try:
                print("He enviado un frame")
                self.udpOutSocket.sendto(data, self.sendTo) #Enviamos el frame
            except sck.error:   #Si hay algún error en el socket
                #self.lockOut.release()  #Subimos el mutex
                continue
            #self.lockOut.release()  #Subimos el mutex tras enviar el frame
        #Si la llamada ha terminado, intentamos levantar el mutex
        try:
            self.lockOut.release()
        except threading.ThreadError:
            pass

    # Función que recibe un frames y los introduce en el buffer de entrada
    def udpRecv(self):
        while(self.alive):  #Mientras la llamada esté "viva"
            self.lockIn.acquire()   #Bajamos el mutex
            try:
                data, sender = self.udpInSocket.recvfrom(1048576)   #Recibimos frame por UDP
            except sck.error:
                self.lockIn.release()   #Si hay error, subimos el mutex
                continue
            if sender[0] != self.sendTo[0]:
                self.lockIn.release()   #Si el paquete nos lo manda otra persona, lo desechamos
                continue
            try:
                queueData = (int(data.split(b"#")[0]), data)
            except ValueError:
                self.lockIn.release()   #Si el frame no tiene la estructura apropiada, lo desechamos
                continue
            try:
                self.bufferIn.put(queueData, block=False)   #Introducimos el frame en la cola de prioridad
            except queue.Full:
                self.lockIn.release()   #Si está llena, levantamos el mutex
                continue
            self.lockIn.release()   #Subimos el mutex tras recibir el frame
        #Si la llamada ha terminado, intentamos levantar el mutex
        try:
            self.lockIn.release()
        except threading.ThreadError:
            pass

    # Función que pausa el envío y recepción de frames
    def hold(self):
        self.lockIn.acquire()
        self.lockOut.acquire()  #Bajamos los mutex de recepción y envío

    # Función que reanuda el envío y recepción de frames
    def resume(self):
        self.lockIn.release()
        self.lockOut.release()  #Levantamos los mutex de recepción y envío

    # Función que prepara los threads de recepción y envío de UDP
    # input: peerInfo Datos del otro usuario
    def start(self, peerInfo):
        if self.alive:
            return  #Si ya estamos en llamada, no hacemos nada

        self.alive=True #Cambiamos la flag del estado de la llamada
        #Creamos los threads de recepción y envío de frames por UDP
        self.udpInThr = threading.Thread(target=self.udpRecv, daemon=True)
        self.udpOutThr = threading.Thread(target=self.udpSend, daemon=True)
        self.sendTo = peerInfo  #Guardamos la información del otro usuario
        #Iniciamos los threads
        self.udpInThr.start()
        self.udpOutThr.start()

    # Función que termina la llamada
    def hang(self):
        self.alive=False    #Cambia el flag del estado de la llamada
