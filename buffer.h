#ifndef BUFFER_H
#define BUFFER_H

#include <stdio.h>
#include <stdint.h>
#include <wchar.h> 
#include "file5.txt"

struct PrintData {
    const char* buffer;
    uint16_t buffer_length;
};


#endif /*buffer.h*/