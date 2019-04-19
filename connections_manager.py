import cv2

MAX_SIZE = 1048576
RECV_PORT = 45654
class connmanag:
    def __init__(self, nick, ip):
        self.ds_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ds_sock.connect(("vega.ii.uam.es", 8000))
        self.list_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loc_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0],
        s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]     #Suponemos que estamos tras una NAT
        self.list_sock.bind((loc_ip, RECV_PORT))
        self.peer_sock = None
        self.versions = "V1"    #Cambiar esto si soportamos más versiones
        self.working_ver = None #Versión acordada al establecer la llamada
        self.out_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.in_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.in_udp.bind((loc_ip, RECV_PORT))
        self.peer_ip = None
        self.nick = nick
        self.usr_called = None
        self.dest_udp_port = None
        self.in_call = False

    def reg_or_upd_usr(self, ip, port, password):
        message = "REGISTER " + self.nick + " " + ip + " " + str(RECV_PORT) + " " + passw + " " + self.versions
        binm = bytes(message, "utf-8")
        self.ds_sock.sendall(binm)
        return self.ds_sock.recv(MAX_SIZE)

    def get_lst_usr(self):
        self.ds_sock.sendall(b"LIST_USERS")
        users = self.ds_sock.recv(MAX_SIZE)
        table = [["Nick", "IP", "Port"]]
        if users[:2] == b"OK":
            users = users[14:]  #Con el 13 quitamos el header fijo
            while(users[0] != b" "):
                users = users[1:]
            users = users[1:]      #Con esto quitamos el número de usuarios
            splitted = users.decode("utf-8").split("#")

            for i in range(len(splitted)-1):
                aux_split = splitted[i].split()
                table.append([])
                for j in range(3):
                    table[i+1].append(aux_split[j])
        return table

    def get_usr_details(self, usr):
        message = "QUERY " + usr
        binm = bytes(message, "utf-8")
        self.ds_sock.sendall(binm)
        data = self.ds_sock.recv(MAX_SIZE)
        if(data[3:] == b"NOK"):
            return None
        return data[:14].decode("utf-8").split(" ") #Quitamos el header y nos devuelve los datos en una lista


    def establ_call(self, usr):
        if self.in_call is True:
            return False    #Check
        self.in_call = True #Avisar también al tcp de escucha
        details = self.get_usr_details(self, usr)
        if details is None:
            return False    #Check
        our_vers = self.versions.split("#").reverse()
        their_vers = self.versions.split("#").reverse() #Ordenamos por "altura" de versión
        for o_ver in our_vers:
            for t_ver in their_vers:
                if o_ver.lower() == t_ver.lower():  #Case insensitive
                    self.working_ver = o_ver
                    break
        if self.working_ver is None:
            return False    #Check
        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_sock.connect((details[1],details[2]))   #TODO Check exception
        init_message = "CALLING " + self.nick + str(RECV_PORT)
        init_message = bytes(init_message, "utf-8")
        self.peer_sock.sendall(init_message)
        status = self.peer_sock.recv(MAX_SIZE)
        if status[:13] is b"CALL_ACCEPTED":
            self.peer_ip = details[1]
            self.usr_called = usr
            splitted = status[:15].split(" ")
            self.dest_udp_port = splitted[1]
            return
        if status[:11] is b"CALL_DENIED":
            return  #TODO
        if status[:9] is b"CALL_RESUME":
            return  #TODO

    def send_frame(self, frame):
        if self.usr_called is None or self.udp_port is None:
            return
        #Poner cabeceras
        encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
        result,encimg = cv2.imencode('.jpg',img,encode_param)
        if result == False:
            pass    #Check error
        encimg = encimg.tobytes()
        self.out_udp.sendto(encimg, (self.peer_ip, self.dest_udp_port))
