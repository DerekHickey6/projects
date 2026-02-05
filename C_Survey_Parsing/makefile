
CC=gcc

# The line with -DDEBUG can be used for development. When
# building your code for evaluation, however, the line *without*
# the -DDEBUG will be used.
#

CFLAGS=-c -Wall -g -DDEBUG -D_GNU_SOURCE -std=c11 -O0


all: dyn_survey

dyn_survey: dyn_survey.o emalloc.o input_handling.o processing.o output.o
	$(CC) dyn_survey.o emalloc.o input_handling.o processing.o output.o -o dyn_survey

dyn_survey.o: dyn_survey.c dyn_survey.h emalloc.h input_handling.h processing.h output.h
	$(CC) $(CFLAGS) dyn_survey.c

input_handling.o: input_handling.c dyn_survey.h input_handling.h emalloc.h
	$(CC) $(CFLAGS) input_handling.c

processing.o: processing.c dyn_survey.h processing.h emalloc.h
	$(CC) $(CFLAGS) processing.c

output.o: output.c dyn_survey.h input_handling.h emalloc.h
	$(CC) $(CFLAGS) output.c

emalloc.o: emalloc.c emalloc.h
	$(CC) $(CFLAGS) emalloc.c

clean:
	rm -rf *.o dyn_survey 
