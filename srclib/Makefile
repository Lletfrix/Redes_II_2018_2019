########################################################
CC := gcc
CFLAGS := -g -Wall
########################################################
INCDIR := ../includes
OBJECTS := daemon.o
#######################################################

all: $(OBJECTS)

daemon.o: daemon.c $(INCDIR)/daemon.h
	$(CC) $(CFLAGS) -c $?

clean:
	rm *.o
