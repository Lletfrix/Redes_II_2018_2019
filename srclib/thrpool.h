typedef enum thread_status{
    DEAD, FREE, BUSY
} thr_status;

typedef struct thr{
    int tid;
    thr_status st;
    //TODO: Add whats needed
} thr;

struct thrpool{
    thr *threads;
    int free;
    int allocated;
    int max;
    short need_resz;
};
