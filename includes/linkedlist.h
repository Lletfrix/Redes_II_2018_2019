#ifndef LINKEDLIST_H
#define LINKEDLIST_H

struct lnode{
    void *val;
    struct lnode *next;
};

typedef struct _likedlist{
    struct lnode *first;
} llist;


/**
 * @brief Initialise a new linked list
 *
 * Allocates memory for a new linked list
 *
 * @return pointer to linked list
 */
llist *llist_new();

void llist_free(llist *);

void llist_destroy(llist *);

void *llist_head(llist *);

int llist_add(llist *, void *elem);

void *llist_pop(llist *l);

/**
 * @brief Destroy first internal node with given elem as val.
 *
 * Free internal lnode memory and gets it out of the list.
 *
 * @param l Linked list to work with
 * @param elem Value to find and delete
 * @param cmp_func Function used to compare values. Must return 0 if equal.
 * @return error code.
 */
int llist_del(llist *l, void *elem, int (*cmp_func) (void *, void *));

int llist_print(FILE *f, llist *l, char * (*to_string) (void *));
#endif
