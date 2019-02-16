########################################################
CC := gcc
CFLAGS := -g -Wall
########################################################
INCDIR := ../includes
LIBDIR := ../lib
LIBS := my_lib.a picohttpparser.a
LIB1 := my_lib.a
LIB2 := picohttpparser.a
PICOL := picohttpparser.a
OBJECTS := connections.o daemon.o process.o
PICO := picohttpparser.o
TEST := test-http-request
#######################################################

all: $(LIBS)

test: $(LIBS) $(TEST)

my_lib.a: $(OBJECTS)
	ar rcs $(LIBDIR)/$@ $?

picohttpparser.a: $(PICO)
	ar rcs $(LIBDIR)/$@ $?

picohttpparser.o: picohttpparser.c
	$(CC) $(CFLAGS) -c $?

connections.o: connections.c
	$(CC) $(CFLAGS) -c $?

daemon.o: daemon.c
	$(CC) $(CFLAGS) -c $?

process.o: process.c
	$(CC) $(CFLAGS) -c $?

test-http-request: test-http-request.o $(LIBDIR)/$(LIB1) $(LIBDIR)/$(LIB2)
	$(CC) $(CFLAGS) -o $@ $?

#tester: tester.o $(LIBDIR)/$(LIB1) $(PICO)
#	$(CC) $(CFLAGS) -o tester $?

test-http-request.o: test-http-request.c
	$(CC) $(CFLAGS) -c $?

clean:
	rm *.o $(TEST)
