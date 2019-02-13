#ifndef CONNECTIONS_H
#define CONNECTIONS_H

int tcp_listen(char* if_addr, int port);
int accept_connection(int listen_fd, struct sockaddr* client_sock, socklen_t* clilen);
int close_connection(int fd);

#endif
