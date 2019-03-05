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

all: server

server: src/server.o makelib
	$(CC) $(CFLAGS) -o $@ src/server.o lib/my_lib.a lib/picohttpparser.a $(LFLAGS)

src/server.o: src/server.c
	$(CC) $(CFLAGS) -c src/server.c -o $@

makelib:
	cd srclib && $(MAKE)

clean:
	rm src/*.o server
