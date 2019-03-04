#ifndef THRPOOL_H
#define THRPOOL_H

struct thrpool{
    int n_free;
    int n_alive;
    unsigned int max;
    short need_resz;
    void * (*thread_routine) (void *);
    llist *free;
    llist *busy;
    pthread_mutex_t freemtx;
    pthread_mutex_t busymtx;
};

struct thrpool *thrpool_new(const unsigned int max, void *(*thr_routine) (void *));

void thrpool_free(struct thrpool* pool);

int thrpool_resize(struct thrpool *pool);

int thrpool_execute(struct thrpool *pool, unsigned int initial);

int thrpool_terminate(struct thrpool *pool);

#endif
