/* survey.c */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
 * Compile-time constants
 */
#define MAX_WORD_LEN 30
#define MAX_LINE_LEN 1000
#define MAX_QUESTIONS 20
#define MAX_QUESTION_LEN 1000
#define MAX_ANSWERS 20
#define RESPONDENTS 20

/*
 * Function prototypes
 */
void print_intro(int num_respondents);
void print_average_stats(int answer_count, 
                         int respondent_count, 
                         char answers[RESPONDENTS][MAX_ANSWERS][MAX_WORD_LEN],
                         char questions[MAX_QUESTIONS][MAX_QUESTION_LEN]);
void print_relative_percents(int answer_count, 
                             int respondent_count,
                             char answers[RESPONDENTS][MAX_ANSWERS][MAX_WORD_LEN],
                             char questions[MAX_QUESTIONS][MAX_QUESTION_LEN]);

int main(int argc, char *argv[]){

    // Cancels program if no parameters are given
     if (argc != 1) {
            printf("Usage: %s\n", argv[0]);
            printf("Should receive no parameters\n");
            printf("Read from the stdin instead\n");
            exit(1);
    }

    // define variable
    int question_count = 0;
    int answer_count = 0;
    int respondent_count = 0;
    int test_bits[2];

    char questions[MAX_QUESTIONS][MAX_QUESTION_LEN];
    char answers[RESPONDENTS][MAX_ANSWERS][MAX_WORD_LEN];
    char line[MAX_LINE_LEN];

    // iterates through file line-by-line and stores in 'line' variable
    while ( fgets(line, sizeof(char) * MAX_LINE_LEN, stdin) ) {

        // Checks if line is a comment and skips if it is 
        if (line[0] == '#') continue;
            
        // compares last digit in string to 0 or 1 ( skipping \n ), to check test bits for differentiating in01, in02, in03
        if(line[0] == '1' || line[0] == '0'){
            test_bits[0] = line[0];
            test_bits[1] = line[2];
        }

        // parses questions from file and stores them in a 2D questions array
        if (line[0] == 'M'){
            
            // instantiates a pointer that points to the first token of tokenized 'line'
            char *question = strtok(line, ";");      

            // Runs while question (pointer) is not NULL and that max questions is not exceeded.
            while(question && question_count < MAX_QUESTIONS){    

                // trims carriage returns or new line characters
                question[strcspn(question, "\r\n")] = 0;       

                strncpy(questions[question_count], question, MAX_QUESTION_LEN - 1);  // copies question (with max length) to the questions array
                questions[question_count][MAX_QUESTION_LEN - 1] = '\0';              // set the null terminator at the end of each string
                question_count++;
                
                // gets next token
                question = strtok(NULL, ";");  
            }
        }

        // parses each respondants answers to the questions and stores in answers array
        if (line[0] == 'd' || line[0] == 'p' || line[0] == 'a'){    
            
            answer_count = 0;

            //points to the first token in a tokenized 'line' variable
            char *token = strtok(line, ",");  
            
            //runs while there is another token available & ensures max answers is not exceeded
            while(token && answer_count < MAX_ANSWERS){  

                // removes any carriage returns or new line characters
                token[strcspn(token, "\r\n")] = 0; 

                strncpy(answers[respondent_count][answer_count], token, MAX_QUESTION_LEN); // copies the token into answers array for each respondant
                answers[respondent_count][answer_count][MAX_QUESTION_LEN - 1] = '\0';      // ensures a null terminator at the end of every answer

                answer_count++;
                token = strtok(NULL, ","); // gets next token
            }
            respondent_count++;
        }
    }
    
    print_intro(respondent_count);

    // prints output based on test bits in input
    if(test_bits[0] == '1'){
        print_relative_percents(answer_count, respondent_count, answers, questions);
        if(test_bits[1] == '1'){
            printf("\n");
            print_average_stats(answer_count, respondent_count, answers, questions);
        }
    }
    if(test_bits[0] == '0') print_average_stats(answer_count, respondent_count, answers, questions);

    exit(0);
}


// Prints the average statistics for each question
void print_average_stats(int answer_count, int respondent_count, char answers[RESPONDENTS][MAX_ANSWERS][MAX_WORD_LEN], char questions[MAX_QUESTIONS][MAX_QUESTION_LEN]){
    
    printf("#####\n");
    printf("FOR EACH QUESTION/ASSERTION BELOW, THE AVERAGE RESPONSE IS SHOWN (FROM 1-DISAGREEMENT TO 4-AGREEMENT)\n\n");
    
    for(int i = 0; i < answer_count; i++){

        int agree = 0;
        int par_agree = 0;
        int par_dis = 0;
        int dis = 0;
        double avg = 0;

        // tabulates results per questions
        for(int j = 1; j < respondent_count; j++){


            if(strcmp(answers[j][i], "agree") == 0){
                agree++;
            } else if (strcmp(answers[j][i], "partially agree") == 0){
                par_agree++;
            } else if (strcmp(answers[j][i], "partially disagree") == 0){
                par_dis++;
            } else if (strcmp(answers[j][i], "disagree") == 0){
                dis++;
            }
            
        }

        avg = (double)(agree*4+par_agree*3+par_dis*2+dis)/(respondent_count - 1);
        
        // prints results by question
        printf("%d. %s - %.2f", i + 1, questions[i], avg);
        printf("\n");

    }
}

// Prints the relative percentual frequencies for each question
void print_relative_percents(int answer_count, int respondent_count, char answers[RESPONDENTS][MAX_ANSWERS][MAX_WORD_LEN], char questions[MAX_QUESTIONS][MAX_QUESTION_LEN]){
    
    printf("#####\n");
    printf("FOR EACH QUESTION/ASSERTION BELOW, RELATIVE PERCENTUAL FREQUENCIES ARE COMPUTED FOR EACH LEVEL OF AGREEMENT\n\n");

    // iterates through respondants and answers to tabulates counts for each question
    for(int i = 0; i < answer_count; i++){

        int agree = 0;
        int par_agree = 0;
        int par_dis = 0;
        int dis = 0;

        // tabulates results per questions
        
        for(int j = 1; j < respondent_count; j++){


            if(strcmp(answers[j][i], "agree") == 0){
                agree++;
            } else if (strcmp(answers[j][i], "partially agree") == 0){
                par_agree++;
            } else if (strcmp(answers[j][i], "partially disagree") == 0){
                par_dis++;
            } else if (strcmp(answers[j][i], "disagree") == 0){
                dis++;
            }
        }
        
        // prints results by question
        
        printf("%d. %s\n", i + 1, questions[i]);
        printf("%2.2f: disagree\n", (double)dis/(respondent_count - 1)*100);
        printf("%2.2f: partially disagree\n", (double)par_dis/(respondent_count - 1)*100);
        printf("%2.2f: partially agree\n", (double)par_agree/(respondent_count - 1)*100);
        printf("%2.2f: agree\n", (double)agree/(respondent_count - 1)*100);
        if(i != answer_count - 1) printf("\n");

    }
}

// Prints the introduction and number of respondents
void print_intro(int num_respondents){
    printf("ECS Student Survey\n");
    printf("SURVEY RESPONSE STATISTICS\n\n");
    printf("NUMBER OF RESPONDENTS: %d\n\n", num_respondents - 1);
}