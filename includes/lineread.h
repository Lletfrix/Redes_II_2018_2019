/*------------------------------------------------------------------
   Project:  General C utilities
   File:     lineread.h
   Rev.      1.0
   Date:     Oct. 9, 2013

   (These functions have been extracted from the library "cfg"
   Vers 1.0, (C) Simone Santini, 2005.)

   (C) Simone Santini, 2012

  -------------------------------------------------------------------
*/
#ifndef _____LINE__READ_____
#define _____LINE__READ_____

#include <stdio.h>

/*
  This function reads a "logical" line from a file. A logical
  line is a line possibly composed of several lines (provided each
  line but the last ends with the character '\') and read ignoring
  comments (a comment is introduced by a character '#' and runs to
  the end of the physical line).

  Example:

  Given a file f containing the lines

       This is the first
       This is the second

  calling the function fgetll will have the same result as calling
  fgets. That is, the program

       for(i=0; i<2; i++)
          printf("%s\n", fgetll(f));

  will print

       This is the first
       This is the second

  Comments will be ignored, so runing the previous program on the file

       This is the first  #here I comment the first line
       #
       #
       #I am about to introduce the second
       This is the second

  will produce exactly the same result.

  A "logical line" can be broken into several "physical lines" by ending
  each line but the last with a '\' character. So, reading the following
  file with the previous program will still produce the same result: TWO
  lines are read, the first being "This is the first", the second
  "This is the second"

      This is the first  #here I comment the first line
       #
       #
       #I am about to introduce the second
       This \   #this comment too will be ignored
            is \  #spaces at the beginning will be ignored
       the second

   NOTE:
   The behavior of this function has three major differences from that of
   the standard library function fgets:

   1. unlike fgets, fgetll does not return the '\n' character at the
      end of the line.
   2. when the end of file is reached, the function returns NULL rather
      that EOF; this is related to
   3. fgets reads into a pre-allocated buffer, this function allocates a
      buffer and returns is: the calling program is in charce of free-ing
      the buffer.
*/
char *fgetll(FILE *f);

#endif
