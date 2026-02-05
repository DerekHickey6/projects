#include "dyn_survey.h"

int main(void) {
    // zero-initialize all fields
    SurveyData survey = {0};   

    // Reads input data and moves it into respective allocated arrays
    read_input(&survey);

    // prints into to survey results
    print_intro(&survey);

    // prints different sections based on binary test bits
    if (survey.test_bits[0]) {
        printf("\n");
        print_relative_percents(&survey);
    }
    if (survey.test_bits[1]) {
        printf("\n");
        print_average_stats(&survey);
    }
    if (survey.test_bits[2]) {
        printf("\n");
        print_demo_data(&survey);
    }

    // frees all allocated memory used during survey
    free_survey(&survey);
    return 0;
}
