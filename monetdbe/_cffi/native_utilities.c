#include <stddef.h>
void initialize_string_array_from_numpy(char** restrict output, size_t size, char* restrict numpy_string_input, size_t stride_length) {
    for (size_t i = 0; i < size; i++) {
        output[i] = numpy_string_input + i*stride_length;
    }
}
