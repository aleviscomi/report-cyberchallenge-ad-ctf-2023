#include "route.h"
#include "util.h"

void route_table_init(struct route_table *routes)
{
    routes->head = routes->tail = NULL;
}

void route_table_add(struct route_table *routes, struct route *route)
{
    route->next = NULL;
    if (routes->tail)
        routes->tail->next = route;
    else
        routes->head = route;
    routes->tail = route;
}

struct route *route_table_lookup(const struct route_table *routes,
                                 const char *path)
{
    for (struct route *route = routes->head; route; route = route->next) {
        if (str_startswith(path, route->prefix))
            return route;
    }
    return NULL;
}
