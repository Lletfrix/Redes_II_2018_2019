/**
 * @brief Interface of logical line read.
 *
 * (These functions have been extracted from the library "cfg"
 * Vers 1.0, (C) Simone Santini, 2005.
 *
 * @file lineread.h
 * @author Simone Santini
 * @version 1.0
 * @date 09-10-2013
 */

#ifndef _____LINE__READ_____
#define _____LINE__READ_____

#include <stdio.h>

/** @defgroup lineread Lineread Library
*
* This module offers a better version, or at least more useful to us, of
* the regular functions that are used to read from file.
*/

/**
 * This function reads a "logical" line from a file. A logical
 * line is a line possibly composed of several lines (provided each
 * line but the last ends with the character '\') and read ignoring
 * comments (a comment is introduced by a character '#' and runs to
 * the end of the physical line).
 *
 *  NOTE:
 *  The behavior of this function has three major differences from that of
 *  the standard library function fgets:
 *
 *  1. unlike fgets, fgetll does not return the '\n' character at the
 *     end of the line.
 *  2. when the end of file is reached, the function returns NULL rather
 *     that EOF; this is related to
 *  3. fgets reads into a pre-allocated buffer, this function allocates a
 *     buffer and returns is: the calling program is in charge of free-ing
 *     the buffer.
 * @ingroup lineread
 * @param f file pointer from which the line will be read
 * @return pointer to read line
 */
char *fgetll(FILE *f);

#endif
