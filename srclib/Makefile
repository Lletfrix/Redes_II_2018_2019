########################################################
CC := gcc
CFLAGS := -g -Wall
########################################################
INCDIR := ../includes
OBJECTS := connections.o
#######################################################

all: $(OBJECTS)

connections.o: connections.c $(INCDIR)/connections.h
	$(CC) $(CFLAGS) -c $?

tester: tester.o connections.o
	$(CC) $(CFLAGS) -o tester $?

tester.o: tester.c
	$(CC) $(CFLAGS) -c $?

clean:
	rm *.o tester
