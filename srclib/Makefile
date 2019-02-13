########################################################
CC := gcc
CFLAGS := -g -Wall
########################################################
INCDIR := ../includes
LIBDIR := ../lib
LIBS := my_lib.a
OBJECTS := connections.o daemon.o
#######################################################

all: $(LIBS)

my_lib.a: $(OBJECTS)
	ar rcs $(LIBDIR)/$@ $?

connections.o: connections.c
	$(CC) $(CFLAGS) -c $?

daemon.o: daemon.c
	$(CC) $(CFLAGS) -c $?

tester: tester.o $(LIBDIR)/$(LIBS)
	$(CC) $(CFLAGS) -o tester $?

tester.o: tester.c
	$(CC) $(CFLAGS) -c $?

clean:
	rm *.o tester
