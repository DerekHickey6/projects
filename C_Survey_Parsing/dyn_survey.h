#ifndef _DYN_SURVEY_H_
#define _DYN_SURVEY_H_

/* add your library includes, constants and typedefs here*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "emalloc.h"

#define MAX_LINE_LEN 1000

// struct defining Respondants and their demographic information
typedef struct {
    char *undergrad_program;
    char *residence_status;
} Respondent;

// struct defining Response and their respondent and array of answers
typedef struct {
    Respondent respondent;
    char **answers;
} Response;

// struct defining survey data, this encompases all data for each survey processed
typedef struct {
    char **questions;
    char **answer_options;
    char **und_options;
    char **res_options;
    Response *responses;

    int num_questions;
    int num_respondents;
    int num_responses_filled;
    int num_und_options;
    int num_res_options;
    int num_answer_options;
    int test_bits[3];
} SurveyData;

/* Function prototypes */
void read_input(SurveyData *survey);
void print_intro(const SurveyData *survey);
void print_relative_percents(const SurveyData *survey);
void print_average_stats(const SurveyData *survey);
void print_demo_data(const SurveyData *survey);
void free_survey(SurveyData *survey);     

#endif
