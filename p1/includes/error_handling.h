/**
 * @brief Error handling library
 *
 * Define ERROR handling constants and functions
 *
 * @file error_handling.h
 * @author Elías Hernandis, Rafael Sánchez, Sergio Cordero, Miguel Baquedano
 * @version 1.0
 * @date 17-01-2018
 */

#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>

/** @defgroup errhandl Error handling module
*
* This module defines ERROR handling constants and functions to make create a
* unified way of notify errors.
*/

/**
 * Returned by the program if no memory could be allocated.
 * @ingroup errhandl
 */
#define OOPSALLOC_ERROR 1

/**
 * UINT_ERROR should be returned by functions that encounter an error and are
 * suposed to return a positive integer, such as the number of operations
 * performed. Please take care not to return UINT_ERROR if your function may
 * return negative integers or if your return type is unsigned.
 * @ingroup errhandl
 */
#define UINT_ERROR -1

/**
 * INT_ERROR should be returned when a function which returns an int throws an error.
 * @ingroup errhandl
 */
#define INT_ERROR INT_MAX

/**
 * Instructs handle_error to output error information to the given file or
 * stream.
 * @ingroup errhandl
 */
#define ERROR_LOG_FILE stderr

/**
 * Instructs log_msg to output debug information to the given file or stream.
 * If this is the same as ERROR_LOG_FILE, debug messages will be prefixed with
 * DEBUG:
 * @ingroup errhandl
 */
#define DEBUG_LOG_FILE stderr

/**
 * If set to false, any call to log_msg will have no effect. Else, log messages
 * will be written to DEBUG_LOG_FILE.
 * @ingroup errhandl
 */
#define DEBUG true

/**
 * This macro is a wrapper arround handle_error. It only works with the
 * detailed way of handling errors, that is, it must be given a function name.
 * It will automatically substitute the appropriate file and line numbers for
 * you in the call to handle error. Note that it does not need to be appended
 * with a semicolon when it is called as it already includes it.
 * @ingroup errhandl
 */
#define HE(msg, func) handle_error(msg, func, __FILE__, __LINE__);

/**
 * This function should handle all errors encountered by the program. This
 * function can either be run with one or four arguments. The first one is
 * always required. If the first one ends with a new line ('\n'), then the rest
 * are ignored and the given error message is handled. Else, the rest are used
 * to craft an appropriate error message. The arguments handle_error may
 * receive are the following:
 *
 *  - const char *error_msg
 *  - cont char *function_name
 *  - const char *file_name
 *  - int line_number
 *
 * file_name and line_number can be automatically obtained thanks to the
 * preprocessor. Just call the function with __FILE__ and __LINE__ as these
 * arguments, e.g. handle_error("some error message", "load_resources",
 * __FILE__, __LINE__); Do not explicitly state neither of the previous, as
 * they may change over time.
 *
 * Please note that because this function does not belong in the standard
 * library, the compiler will not be as descriptive as it is with fprintf on
 * its error messages.
 *
 * @param error_msg error message to print out
 * @ingroup errhandl
 */
void handle_error(const char *error_msg, ...);

/**
 * Logging can be performed through this function. It works in the same way as
 * handle_error, but it'll writes to a separate stream from handle_error. The
 * stream this function writes to depends on the DEBUG_LOG_FILE constant
 * declared above.
 *
 * @param msg error message to log
 * @ingroup errhandl
 */
void log_msg(const char *msg, ...);

/**
 * Wrapper around calloc that will print an error when it fails and will
 * exit the program afterwards
 *
 * @param num number of items to alloc
 * @param size size of the items to alloc
 * @param caller name of the function that called oopsalloc
 * @return pointer to the newly alloc'd memory
 * @ingroup errhandl
 */
void *oopsalloc(size_t num, size_t size, const char *caller);
