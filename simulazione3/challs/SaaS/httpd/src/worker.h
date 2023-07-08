#ifndef WORKER_H
#define WORKER_H

#include <stdbool.h>

#include "route.h"

bool worker_connection(int fd, const struct route_table *routes);

#endif
