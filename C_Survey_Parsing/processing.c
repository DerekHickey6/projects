/* processing.c */
#include "dyn_survey.h"

// Calculates and prints the demo data for undergraduate program and residence status
void print_demo_data(const SurveyData *survey) {

    // allocate memory and initializes it to avoid storing 'garbage' values
    int *und_count = calloc(survey->num_und_options, sizeof(int));
    int *res_count = calloc(survey->num_res_options, sizeof(int));

    // prints section intro
    printf("#####\n");
    printf("FOR EACH DEMOGRAPHIC CATEGORY BELOW, RELATIVE PERCENTUAL FREQUENCIES ARE COMPUTED FOR EACH ATTRIBUTE VALUE\n\n");

    // dynamically counts frequencies of undergraduate and resident info
    for (int i = 0; i < survey->num_respondents; i++) {
        char *ug = survey->responses[i].respondent.undergrad_program;
        char *res = survey->responses[i].respondent.residence_status;

        // undergrad info
        for (int j = 0; j < survey->num_und_options; j++)
            if (strcmp(ug, survey->und_options[j]) == 0)
                und_count[j]++;

        // resident info
        for (int j = 0; j < survey->num_res_options; j++)
            if (strcmp(res, survey->res_options[j]) == 0)
                res_count[j]++;
    }

    // prints the frequency with related undergraduate program
    printf("UNDERGRADUATE PROGRAM\n");
    for (int i = 0; i < survey->num_und_options; i++)
        printf("%2.2f: %s\n", (100.0 * und_count[i]) / survey->num_respondents, survey->und_options[i]);

    // prints the frequency with related resident status
    printf("\nRESIDENCE STATUS\n");
    for (int i = 0; i < survey->num_res_options; i++)
        printf("%2.2f: %s\n", (100.0 * res_count[i]) / survey->num_respondents, survey->res_options[i]);

    // frees the memory used by und_count and res_count
    free(und_count);
    free(res_count);
}

// Prints the average statistics for each question
void print_average_stats(const SurveyData *survey) {

    int *ans_count = calloc(survey->num_answer_options, sizeof(int));
    // prints intro to the section
    printf("#####\n");
    printf("FOR EACH QUESTION/ASSERTION BELOW, THE AVERAGE RESPONSE IS SHOWN (FROM 1-DISAGREEMENT TO 4-AGREEMENT)\n\n");

    // counts and tabulates answers and prints average for each question
    for (int i = 0; i < survey->num_questions; i++) {
        // reset counts for each question
        for (int j = 0; j < survey->num_answer_options; j++)
            ans_count[j] = 0;

        for (int j = 0; j < survey->num_respondents; j++) {
            char *ans = survey->responses[j].answers[i];
        
            // increments count if answer matches the answer in answers array index
            for (int k = 0; k < survey->num_answer_options; k++) {
                if (strcmp(ans, survey->answer_options[k]) == 0)
                    ans_count[k]++;
            }
        }
        // prints the average based on tabulated answer counts
        double avg = (double)(ans_count[0] + ans_count[1]*2 + ans_count[2]*3 + ans_count[3]*4) / survey->num_respondents;
        printf("%d. %s - %.2f\n", i + 1, survey->questions[i], avg);
    }
    
    free(ans_count);
}


// Prints the relative percentual frequencies for each question
void print_relative_percents(const SurveyData *survey) {
    int *ans_count = calloc(survey->num_answer_options, sizeof(int));
    
    // prints intro to section
    printf("#####\n");
    printf("FOR EACH QUESTION/ASSERTION BELOW, RELATIVE PERCENTUAL FREQUENCIES ARE COMPUTED FOR EACH LEVEL OF AGREEMENT\n\n");

    // counts and tabulates answers and prints average for each question
    for (int i = 0; i < survey->num_questions; i++) {
        // reset counts for each question
        for (int j = 0; j < survey->num_answer_options; j++)
            ans_count[j] = 0;

        for (int j = 0; j < survey->num_respondents; j++) {
            char *ans = survey->responses[j].answers[i];

            // increments count if answer matches the answer in answers array index
            for (int k = 0; k < survey->num_answer_options; k++) {
                if (strcmp(ans, survey->answer_options[k]) == 0)
                    ans_count[k]++;
            }
        }

        // calculates relative percents and print results
        printf("%d. %s\n", i + 1, survey->questions[i]);
        for (int i = 0; i < survey->num_answer_options; i++) {
            double percent = (100.0 * ans_count[i]) / survey->num_respondents;
            printf("%2.2f: %s\n", percent, survey->answer_options[i]);
        }

        if (i < survey->num_questions - 1)
            printf("\n");
    }

    free(ans_count);
}

