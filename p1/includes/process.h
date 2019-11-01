/**
 * @brief Necessary functions to process different http requests
 *
 * @file process.h
 * @author Sergio Galán, Rafael Sánchez
 * @version 1.0
 * @date 11-02-2019
 */
#ifndef PROCESS_H
#define PROCESS_H

/** @defgroup process Process Library
*
* This module offers a function that gets an HTTP package and processes
* it. It supports both HTTP 1.0 and 1.1, CGI scripting in Python and PHP,
* and the verbs GET, POST and OPTIONS
*/

/**
 * Receives a request, parses it with picohttpparser aid, checks if we support
 * the verb we have received and acts in consequence if we support it.
 * If we don't, then we answer with 501 NOT IMPLEMENTED
 *
 * @param clientfd Client connection descriptor
 * @return EXIT_SUCCESS if we succesfully answer the request, EXIT_FAILURE in other case.
 * @ingroup process
 */
int process_http(int clientfd);

#endif
