########################################################
CC := gcc
CFLAGS := -g -Wall
LFLAGS := -lpthread -lm
########################################################
INCDIR := ../includes
LIBDIR := ../lib
LIBS := my_lib.a picohttpparser.a config.a
LIB1 := my_lib.a
LIB2 := picohttpparser.a
OBJECTS := connections.o daemon.o process.o thrpool.o linkedlist.o
CONFIG := config.o error_handling.o lineread.o
PICO := picohttpparser.o
TEST := test-http-request test-llist test-thrpool
#######################################################
all: $(TEST)

test-thrpool: test-thrpool.o $(LIBDIR)/$(LIB1) $(LIBDIR)/$(LIB2)
	$(CC) $(CFLAGS) -o test-thrpool $? $(LFLAGS)

test-thrpool.o: test-thrpool.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

test-llist: test-llist.o ../srclib/linkedlist.o
	$(CC) $(CFLAGS) -o test-llist $? $(LFLAGS)

test-llist.o: test-llist.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

test-http-request: test-http-request.o $(LIBDIR)/$(LIB1) $(LIBDIR)/$(LIB2) $(LIBDIR)/config.a
	$(CC) $(CFLAGS) -o $@ $? $(LFLAGS)

test-http-request.o: test-http-request.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

clean:
	rm *.o
