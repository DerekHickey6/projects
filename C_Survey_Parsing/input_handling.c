/* input_handling.c */
#include "dyn_survey.h"

// reads input of survey and stores in allocated arrays
void read_input(SurveyData *survey)

{
    char line[MAX_LINE_LEN];
    int line_number = 1;

    survey->num_questions = 0;
    survey->num_respondents = 0;
    survey->num_und_options = 0;
    survey->num_res_options = 0;
    survey->num_answer_options = 0;
    survey->num_responses_filled = 0;

    survey->questions = NULL;
    survey->und_options = NULL;
    survey->res_options = NULL;
    survey->answer_options = NULL;
    survey->responses = NULL;
    
    // iterates through input to gather data
    while (fgets(line, sizeof(line), stdin)) {  
        // skips comments        
        if (line[0] == '#') {                           
            line_number++;                                                    
            continue;
        }

        // removes carriage returns and newline characters from line
        line[strcspn(line, "\r\n")] = 0;                
        
        // scan 'line' to parse test_bits
        if (line_number == 5) {
            sscanf(line, "%d,%d,%d",                    
                &survey->test_bits[0],                  
                &survey->test_bits[1],
                &survey->test_bits[2]);
        }

        // parses undergrad options
        else if (line_number == 7) {                    
            char *token = strtok(line, ",");            
            while (token) {
                // reallocates memory based on number of undergrad options counted
                survey->und_options = realloc(survey->und_options,
                    (survey->num_und_options + 1) * sizeof(char *));
                // uses strdup which allocates new memory for duplicate
                survey->und_options[survey->num_und_options] = strdup(token);
                survey->num_und_options++;
                token = strtok(NULL, ",");
            }
        }

        // parses residence status
        else if (line_number == 9) {
            char *token = strtok(line, ",");
            while (token) {
                // reallocates memory based on number of residence options counted
                survey->res_options = realloc(survey->res_options,
                    (survey->num_res_options + 1) * sizeof(char *));
                    // uses strdup which allocates new memory for duplicate
                survey->res_options[survey->num_res_options] = strdup(token);
                survey->num_res_options++;
                token = strtok(NULL, ",");
            }
        }
        
        // parses questions from file and stores them in a 2D questions array
        else if (line_number == 11) {
            char *token = strtok(line, ";");
            while (token) {
                // reallocates memory based on number of questions counted
                survey->questions = realloc(survey->questions,
                    (survey->num_questions + 1) * sizeof(char *));
                    // uses strdup which allocates new memory for duplicate
                survey->questions[survey->num_questions] = strdup(token);
                survey->num_questions++;
                token = strtok(NULL, ";");
            }
        }
        
        // parses possible answers
        else if (line_number == 13) {
            char *token = strtok(line, ",");
            while (token) {
                // reallocates memory based on number of answers counted
                survey->answer_options = realloc(survey->answer_options,
                    (survey->num_answer_options + 1) * sizeof(char *));
                    // uses strdup which allocates new memory for duplicate
                survey->answer_options[survey->num_answer_options] = strdup(token);
                survey->num_answer_options++;
                token = strtok(NULL, ",");
            }
        }
        // parses number of respondents
        else if (line_number == 15) {
            // converts string to int for number of respondents
            survey->num_respondents = atoi(line);
            // allocates memory based on number of respondents
            survey->responses = emalloc(survey->num_respondents * sizeof(Response));
            // initializes all respondent information as 'empty' or null, indicating no data yet
            for (int i = 0; i < survey->num_respondents; i++) {
                survey->responses[i].respondent.undergrad_program = NULL;
                survey->responses[i].respondent.residence_status = NULL;
                survey->responses[i].answers = NULL;
            }
        }


        // parses each respondants answers to the questions and stores in answers array
        else if (line_number > 16) {
            // response counter
            int i = survey->num_responses_filled++;
            // allocates memory for answers based on number of questions
            survey->responses[i].answers = emalloc(survey->num_questions * sizeof(char *));

            char *token = strtok(line, ",");
            int token_idx = 0;
            
            // parses each respondents answers and stores in appropriate array 
            while (token) {
                if (token_idx == 0)
                    survey->responses[i].respondent.undergrad_program = strdup(token);
                else if (token_idx == 1)
                    survey->responses[i].respondent.residence_status = strdup(token);
                else {
                    int ans_idx = token_idx - 2;
                    survey->responses[i].answers[ans_idx] = strdup(token);
                }
                token_idx++;
                token = strtok(NULL, ",");
            }
        }
        // moves to next line for control flow
        line_number++; 
    }
}

void free_survey(SurveyData *survey) {
    // frees all questions memmory
    for (int i = 0; i < survey->num_questions; i++)
        free(survey->questions[i]);
    free(survey->questions);

    // frees all answer option memory 
    for (int i = 0; i < survey->num_answer_options; i++)
        free(survey->answer_options[i]);
    free(survey->answer_options);

    // frees all undergrad option memory 
    for (int i = 0; i < survey->num_und_options; i++)
        free(survey->und_options[i]);
    free(survey->und_options);

    // frees all residence option memory
    for (int i = 0; i < survey->num_res_options; i++)
        free(survey->res_options[i]);
    free(survey->res_options);

    // free respondents and their answers
    for (int i = 0; i < survey->num_respondents; i++) {
        free(survey->responses[i].respondent.undergrad_program);
        free(survey->responses[i].respondent.residence_status);

        for (int j = 0; j < survey->num_questions; j++)
            free(survey->responses[i].answers[j]);
        free(survey->responses[i].answers);
    }
    free(survey->responses);
}
