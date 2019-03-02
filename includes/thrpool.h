#ifndef THRPOOL_H
#define THRPOOL_H

typedef enum thread_status{
    DEAD, FREE, BUSY
} thr_status;

typedef struct thr{
    pthread_t tid;
    thr_status st;
    //TODO: Add whats needed
} thr;

struct thrpool{
    thr *threads;
    int free;
    int allocated;
    unsigned int max;
    short need_resz;
    void * (*thread_routine) (void *);
};

struct thrpool *thrpool_new(const unsigned int max, void *(*thr_routine) (void *));

void thrpool_free(struct thrpool* pool);

int thrpool_resize(struct thrpool *pool);

int thrpool_execute(struct thrpool *pool, unsigned int initial);

int thrpool_terminate();

#endif
