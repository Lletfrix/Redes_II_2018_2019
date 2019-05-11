/**
 * @brief Provides a threadpool interface.
 *
 * This file contains the needed functions to use a pool of threads to execute
 * the same given routine. Depends on linkedlist.h.
 *
 * @file thrpool.h
 * @author Rafael Sánchez, Sergio Galán
 * @version 0.9
 * @date 11-02-2019
 */
#ifndef THRPOOL_H
#define THRPOOL_H

#include "linkedlist.h"
/** @defgroup thrpool ThreadPool module
*
* This module provides a the needed functions to use a pool of threads to execute
* the same given routine. Depends on linkedlist.h.
*/

/**
 * Contains all the information related to the thread pool and its state.
 * @ingroup thrpool
 */
struct thrpool{
    int n_free;  /*!< Number of threads that are not doing any job */
    int n_alive; /*!< Number of threads that are alive */
    unsigned int max; /*!< Maximum number of threads */
    short need_resz; /*!< Flag that tells if the thread needs a resize */
    void * (*thread_routine) (void *); /*!< Routine to be executed by each thread */
    llist *free; /*!< Linked List containing references to every free thread */
    llist *busy; /*!< Linked List containing references to every busy thread */
    pthread_mutex_t freemtx; /*!< Mutex that controls the access to llist *free */
    pthread_mutex_t busymtx; /*!< Mutex that controls the access to llist *busy */
};

/**
 * Allocates memory for, and initialise a new thread pool
 *
 * @param max maximum number of threads
 * @param thr_routine reference to the routine that will be executed by the threads
 * @return pointer to thread pool structure
 * @ingroup thrpool
 */
struct thrpool *thrpool_new(const unsigned int max, void *(*thr_routine) (void *));

/**
 * Frees all the resources allocated by thrpool_new.
 *
 * @param pool reference to the pool to be freed
 * @ingroup thrpool
 */
void thrpool_free(struct thrpool* pool);

//int thrpool_resize(struct thrpool *pool);

/**
 * Starts the execution of the function associated in the pool by a number
 * of threads given by the initial parameter.
 *
 * @param pool reference to the pool that will start the threads
 * @param initial number of threads to start running
 * @return 0 on error, 1 on success
 * @ingroup thrpool
 */
int thrpool_execute(struct thrpool *pool, unsigned int initial);

/**
 * End the execution of the function associated in the pool of all busy threads.
 *
 * @param pool reeference to the pool to end the execution
 * @return 0 on error, 1 on success
 * @ingroup thrpool
 */
int thrpool_terminate(struct thrpool *pool);

#endif
