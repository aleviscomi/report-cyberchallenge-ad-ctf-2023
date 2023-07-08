#ifndef SANDBOX_H
#define SANDBOX_H

#include <stddef.h>

char *sandbox_run(const void *code, size_t size, size_t *out_size);

#endif
