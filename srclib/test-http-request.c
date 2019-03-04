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

int sockfd, clientfd;
void handle_sigint(int sig)
{
    close_connection(sockfd);
    close_connection(clientfd);
    exit(EXIT_SUCCESS);
}

int main(void){
    char ip[] = "127.0.0.1";
    int port = 5001;
    struct sockaddr_in client;
    socklen_t addrlen = sizeof(client);

    sockfd = tcp_listen(ip, port);
    printf("Estamos escuchando\n");

    signal(SIGINT, handle_sigint);

    while(1){
        clientfd = accept_connection(sockfd, (struct sockaddr*)&client, &addrlen);
        printf("Conexión recibida: %s:%d\n", inet_ntoa(client.sin_addr), ntohs(client.sin_port));
        process_http(clientfd);
        close_connection(clientfd);
    }
}
