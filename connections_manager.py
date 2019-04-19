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
        self.nick = nick
        self.in_call = False

    def reg_or_upd_usr(self, ip, port, password):
        message = "REGISTER " + self.nick + " " + ip + " " + str(RECV_PORT) + " " + passw + " " + self.versions
        binm = bytes(message, "utf-8")
        self.ds_sock.sendall(binm)
        return self.ds_sock.recv(MAX_SIZE)
