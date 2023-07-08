#ifndef SERVER_H
#define SERVER_H

#include "route.h"

#define SERVER_NAME "CC.IT-HTTPd/1.0"

void server_run(int port, const struct route_table *routes);

#endif
