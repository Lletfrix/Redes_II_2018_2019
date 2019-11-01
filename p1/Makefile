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
PICO := picohttpparser.o
TEST := test-http-request test-llist test-thrpool
#######################################################

all: server

server: src/server.o makelib
	$(CC) $(CFLAGS) -o $@ src/server.o lib/my_lib.a lib/picohttpparser.a lib/config.a $(LFLAGS)

src/server.o: src/server.c
	$(CC) $(CFLAGS) -c src/server.c -o $@

makelib:
	cd srclib && $(MAKE)

test: makelib
	cd tests && $(MAKE)

clean:
	cd srclib && make clean && cd ..
	rm src/*.o server
	rm lib/*.a
	sudo rm assets/temp/out*.txt

clean_test:
	cd tests && make clean
