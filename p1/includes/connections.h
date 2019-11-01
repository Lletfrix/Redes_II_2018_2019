/**
 * @brief Offers a interface around <socket.c>
 *
 * @file connections.h
 * @author Sergio Galán
 * @version 1.0
 * @date 11-02-2019
 */
#ifndef CONNECTIONS_H
#define CONNECTIONS_H

/** @defgroup connections Connections module
*
* This module offers a interface around <socket.c> in the case we need to expand
* and build a wrapper around those functions.
*/


/**
 * Maximum number of connections that can be buffered until accepted
 * @ingroup connections
 */
#define MAXQUEUE 20

/**
 * Starts a tcp socket, bind it and start to listen until a maximum of
 * MAXQUEUE petitions
 *
 * @ingroup connections
 * @param if_addr Address to bind the socket
 * @param port Port to bind the socket
 * @return socket descriptor on success, -1 on error
 */
int tcp_listen(char* if_addr, int port);

/**
 * Accepts a TCP connection. For more information, see man accept
 *
 * @ingroup connections
 * @param listen_fd File descriptor of a listening socket
 * @param client_sock Struct information about the client address
 * @param clilen Size in bytes of client_sock structure
 * @return connected socket descriptor, -1 on error
 */
int accept_connection(int listen_fd, struct sockaddr* client_sock, socklen_t* clilen);

/**
 * Close file descritor fd
 *
 * @ingroup connections
 * @param fd File descriptor to be closed
 * @return connected socket descriptor, -1 on error
 */
int close_connection(int fd);

#endif
