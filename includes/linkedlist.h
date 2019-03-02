#ifndef LINKEDLIST_H
#define LINKEDLIST_H

struct lnode{
    void *val;
    struct lnode *next;
};

typedef struct _likedlist{
    struct lnode *first;
} llist;

llist *llist_new();

void llist_free(llist *);

void llist_destroy(llist *);

void *llist_head(llist *);

int llist_add(llist *, void *elem);

void *llist_pop(llist *l);

int llist_del(llist *l, void *elem, int (*cmp_func) (void *, void *));
#endif
