/**
 * @brief Provides a function and macros to demonize a calling process
 *
 * @file daemon.h
 * @author Rafael Sánchez, Sergio Galán
 * @version 1.0
 * @date 11-02-2019
 */
#ifndef DAEMON_H
#define DAEMON_H

/** @defgroup daemon Daemon library
*
* This module offers the required interface to allow a process
* to run daemonized
*/

/**
 * @ingroup daemon
 * Maximum length of cwd's path
 */
#define PATHMAX 1024

/**
*
* Demonizes calling process, change the working directory to '/' and
* opens up a syslog.
*
* @ingroup daemon
* @param service service name
* @param cwd memory pointer where cwd will be stored
*
* @return 0 on success, negative value on error
*/
int demonizar(const char *service, char *cwd);

#endif
