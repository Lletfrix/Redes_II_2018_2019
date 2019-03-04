########################################################
CC := gcc
CFLAGS := -g -Wall
LFLAGS := -lpthread -lm
########################################################
INCDIR := ../includes
LIBDIR := ../lib
LIBS := my_lib.a picohttpparser.a
LIB1 := my_lib.a
LIB2 := picohttpparser.a
OBJECTS := connections.o daemon.o process.o thrpool.o linkedlist.o
PICO := picohttpparser.o
TEST := test-http-request test-llist test-thrpool
#######################################################

all: $(LIBS)

test: $(LIBS) $(TEST)

my_lib.a: $(OBJECTS)
	ar rcs $(LIBDIR)/$@ $?

picohttpparser.a: $(PICO)
	ar rcs $(LIBDIR)/$@ $?

picohttpparser.o: picohttpparser.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

connections.o: connections.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

daemon.o: daemon.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

thrpool.o : thrpool.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

linkedlist.o : linkedlist.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

test-thrpool: test-thrpool.o $(LIBDIR)/$(LIB1) $(LIBDIR)/$(LIB2)
	$(CC) $(CFLAGS) -o test-thrpool $? $(LFLAGS)

test-thrpool.o: test-thrpool.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

test-llist: test-llist.o linkedlist.o
	$(CC) $(CFLAGS) -o test-llist $? $(LFLAGS)

test-llist.o: test-llist.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

process.o: process.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

test-http-request: test-http-request.o $(LIBDIR)/$(LIB1) $(LIBDIR)/$(LIB2)
	$(CC) $(CFLAGS) -o $@ $? $(LFLAGS)

test-http-request.o: test-http-request.c
	$(CC) $(CFLAGS) -c $? $(LFLAGS)

clean:
	rm *.o $(TEST)
