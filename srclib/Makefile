########################################################
CC := gcc
CFLAGS := -g -Wall
LFLAGS := -lpthread -lm
########################################################
INCDIR := ../includes
LIBDIR := ../lib
LIBS := my_lib.a
OBJECTS := connections.o daemon.o thrpool.o linkedlist.o
#######################################################

all: $(LIBS)

my_lib.a: $(OBJECTS)
	ar rcs $(LIBDIR)/$@ $?

connections.o: connections.c
	$(CC) $(CFLAGS) -c $?

daemon.o: daemon.c
	$(CC) $(CFLAGS) -c $?

thrpool.o : thrpool.c
	$(CC) $(CFLAGS) -c $?

linkedlist.o : linkedlist.c
	$(CC) $(CFLAGS) -c $?

test-thrpool: test-thrpool.o $(LIBDIR)/$(LIBS)
	$(CC) $(CFLAGS) -o test-thrpool $? $(LFLAGS)

test-thrpool.o: test-thrpool.c
	$(CC) $(CFLAGS) -c $?

test-llist: test-llist.o linkedlist.o
	$(CC) $(CFLAGS) -o test-llist $? $(LFLAGS)

test-llist.o: test-llist.c
	$(CC) $(CFLAGS) -c $?

clean:
	rm *.o test-thrpool
