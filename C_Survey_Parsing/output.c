/* output.c */
#include "dyn_survey.h"

// Prints the introduction and number of respondents
void print_intro(const SurveyData *survey) {
    printf("ECS Student Survey\n");
    printf("SURVEY RESPONSE STATISTICS\n\n");
    printf("NUMBER OF RESPONDENTS: %d\n", survey->num_respondents);
}

