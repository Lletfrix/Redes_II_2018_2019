#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>

#include "../includes/connections.h"
#include "../includes/process.h"

int main(void){
    char ip[] = "127.0.0.1";
    int port = 80;
    int sockfd, clientfd;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(client);

    sockfd = tcp_listen(ip, port);
    printf("Estamos escuchando\n");

    clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
    printf("Conexión recibida: %s:%d\n", inet_ntoa(client.sin_addr), ntohs(client.sin_port));

    process_http(clientfd);

    close_connection(clientfd);
    close_connection(sockfd);


}
