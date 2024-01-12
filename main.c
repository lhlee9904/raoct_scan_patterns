#pragma warning(disable:4996)
#include <stdio.h>
#include <stdint.h>
#include <locale.h>
#include <wchar.h>
#include "buffer.h"

//extern const char* buffer;
//SAI_TransmitReceive(hsai, buffer, buffer_length);



int main(int argc, char** argv) {

    int arr_length = buffer_length * 2;
    uint16_t data_points[1060] = { 0 };
    uint16_t* buf16 = (uint16_t*)buffer; //error invalid type conversion

char* filename = "scan_patterns8.txt";

    // open the file for writing
    FILE* fp;
    fp = fopen(filename, "a");
    if (fp == NULL)
    {
        printf("Error opening the file %s", filename);
        return -1;
    }

    printf("{");
    fprintf(fp, "{");
    for (size_t i = 0; i < buffer_length; i++) {
        uint16_t x = *buf16++;
        uint16_t y = *buf16++;
        data_points[2 * i] = x;
        data_points[2 * i + 1] = y;
        fprintf(fp, "Data Point%d: ", i);

        printf("%u, ", (unsigned int)x);
        printf("%u\n", (unsigned int)y);
        fprintf(fp, "%u, ", (unsigned int)x);
        fprintf(fp, "%u\n", (unsigned int)y);
    }
    printf("}");
    fprintf(fp, "}");

    // close the file
    fclose(fp);
    return 0;
}
    /*
    static const unsigned long pattern_length = 3;
    static const char* pattern = "\u0085\u00d6\u0080\u00b2\u0082\u0000";
    static const char* pattern2= "\u00d6\u00b2\u00b2\u00d6\u00b2\u00b2";
    uint16_t data_points[6] = {0};
    for (size_t i = 0; i < pattern_length; i++) {
        uint16_t* buf16 = (uint16_t*)pattern2;//error invalid type conversion
        uint16_t x = *buf16++;
        uint16_t y = *buf16++;
        data_points[2*i] = x;
        data_points[2 * i + 1] = y; 
        printf("%u\n", (unsigned int)x);
        printf("%u\n", (unsigned int)y);

    }
    */

//if ((input = fopen("input.txt", "r")) == NULL)
//return 1;

//reference from wikipedia 
//char s2[] = "\u00C0"; 
// Two bytes with values 0xC3, 0x80, the UTF-8 encoding of U+00C0