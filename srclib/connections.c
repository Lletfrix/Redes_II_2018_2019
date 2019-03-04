#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <sys/socket.h>

#include "../includes/connections.h"

#define MAXBUF 1024
#define MAXQUEUE 20

int tcp_listen(char* if_addr, int port){
    int sockfd;
    struct sockaddr_in sock;

    /*Creamos Socket TCP*/
    if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
        //TODO
    }

    /*Inicializamos Socket*/
    bzero(&sock, sizeof(sock));
    sock.sin_family = AF_INET;
    sock.sin_port = htons(port);
    if(inet_aton(if_addr, &(sock.sin_addr)) == 0){
        //TODO
    }

    /*Asociamos el Puerto al Socket*/
    if(bind(sockfd, (struct sockaddr*)&sock, sizeof(sock))){
        //TODO
    }

    /*Escuchamos*/
    if(listen(sockfd, MAXQUEUE)){
        //TODO
    }
    return sockfd;
}

int accept_connection(int listen_fd, struct sockaddr* client_sock, socklen_t* clilen){
    /*int clientfd;
    if((clientfd = accept(listen_fd, client_sock, clilen)) == -1){
        //TODO
    }
    return client_fd;*/
    return accept(listen_fd, client_sock, clilen);
}

int close_connection(int fd){
    return close(fd);
}
