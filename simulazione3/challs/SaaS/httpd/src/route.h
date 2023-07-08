#ifndef ROUTE_H
#define ROUTE_H

#include <stddef.h>
#include <netinet/in.h>

enum route_kind {
    STATIC,
    STATIC_SANDBOX,
    PROXY,
};

struct route_static {
    const char *root_path;
};

struct route_proxy {
    struct in_addr addr;
    unsigned short port;
};

struct route {
    struct route *next;
    enum route_kind kind;
    const char *prefix;
    union {
        struct route_static r_static;
        struct route_proxy r_proxy;
    };
};

struct route_table {
    struct route *head;
    struct route *tail;
};

void route_table_init(struct route_table *routes);
void route_table_add(struct route_table *routes, struct route *route);

struct route *route_table_lookup(const struct route_table *routes,
                                 const char *path);

#endif
