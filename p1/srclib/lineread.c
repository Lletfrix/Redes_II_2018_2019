/*------------------------------------------------------------------
   Project:  General C utilities
   File:     lineread.c
   Rev.      1.0
   Date:     Oct. 9, 2013

   (These functions have been extracted from the library "cfg"
   Vers 1.0, (C) Simone Santini, 2005.)

   (C) Simone Santini, 2012

  -------------------------------------------------------------------
*/

#include "../includes/lineread.h"

#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAXLINE  10000

/*
 * Wrap strdup inside guards for MacOS systems, which include strdup by
 * default.
 */
#ifndef __DARWIN_C_LEVEL
//char *strdup(char *);
#endif

/*-------------------------------------------------------------------
            I N T E R N A L    F U N C T I O N S
  -------------------------------------------------------------------*/


/*
  Given a string, removes from it all the initial and the trailing blanks.
  Returns a newly allocated string.
*/
char *_clean_up_string(char *string) {
  char *ptr;

  /* Remove the trailing blanks */
  ptr = string + strlen(string);   /* This makes ptr point to the "0" at the end of the string */
  ptr--;
  while( isspace(*ptr) )
    *ptr = *ptr - 1; // changed this line from *ptr-- to this to silence a waring
  *(ptr+1) = 0;

  /* Remove the initial blanks */
  ptr = string;
  while( isspace(*ptr) )
    ptr++;

  return strdup(ptr);
}

/*
  Reads a "physical" line from a configuration file, removes from it all the
  comments and all the trailing blanks before the comments.
*/
char *_read_physical_line(FILE *fp) {
  if (fp == NULL) return NULL;
  char buf[MAXLINE], c, *ptr;
  int i=0;
  c = fgetc(fp);
  if (c == EOF) return NULL;
  while(c != '\n' && c != EOF) {
    buf[i++] = c;
    if (i >= MAXLINE) {
      fprintf(stderr, "Line too long in the input file.");
      exit(1);
    }
    c = fgetc(fp);
  }
  buf[i] = 0;

  ptr = strchr(buf, '#');
  if (ptr != NULL) *ptr = 0;
  ptr = buf + strlen(buf);   /* This makes ptr point to the "0" at the end of buf */
  ptr--;
  if (ptr < buf)            /* This is true if the line only had a comment */
    return _read_physical_line(fp);
  while(isspace(*ptr) && ptr > buf)
    ptr--;
  if (ptr < buf)           /* The line is empty or it contains nothing but comments */
    return _read_physical_line(fp);
  *(ptr+1) = 0;
  return strdup(buf);
}


/*
  Reads a "logical" line, that is, a line that end where the comments start
  (the functions keeps reading until a non-empty line that doesn't start with
  # or the end of file is found), and can span multiple lines by ending the
  previous line (excluding the comment) with a "\". So the following four
  lines are read as a single line

  par1    string   "this is a very very long string \ #note that the quites are not closed
                   that I continue on several lines \
  # note: the spaces before the "that" on the previous line are ignored
                   and I finally close."   # and this is the end of the "logical" line

*/
char *_read_logical_line(FILE *fp) {
  char *q_acc;
  char *q = _read_physical_line(fp);
  if (q == NULL) return NULL;
  if (*(q + strlen(q) - 1) != '\\') return q;

  q_acc = q;
  while (*(q_acc + strlen(q_acc) - 1) == '\\') {
    *(q_acc + strlen(q_acc) - 1) = 0;
    q = _read_physical_line(fp);
    if (q == NULL) {
      fprintf(stderr, "Error: end of file encountered before the end of the line\n%s\n", q_acc);
      exit(1);
    }
    char *q1 = _clean_up_string(q);
    free(q);
    q = q_acc;
    q_acc = (char *) malloc((strlen(q) + strlen(q1))*sizeof(char));
    int k=0;
    for (int i=0; i<strlen(q); i++) q_acc[k++] = q[i];
    for (int i=0; i<strlen(q1); i++) q_acc[k++] = q1[i];
    q_acc[k] = 0;
    free(q);
    free(q1);
  }
  return q_acc;
}

/*-------------------------------------------------------------------
            P U B L I C    F U N C T I O N S
  -------------------------------------------------------------------*/

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
char *fgetll(FILE *f) {
  return _read_logical_line(f);
}
