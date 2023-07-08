#define _DEFAULT_SOURCE /* herror */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <netdb.h>

#include "server.h"
#include "route.h"

#define SERVER_PORT 5555

static void resolve_host_addr(struct in_addr *addr, const char *name)
{
    struct hostent *ent = gethostbyname(name);
    if (!ent) {
        herror("gethostbyname");
        exit(1);
    }
    if (ent->h_addrtype != AF_INET) {
        fprintf(stderr, "resolve_host_addr: bad address type\n");
        exit(1);
    }
    if (ent->h_length != sizeof(*addr)) {
        fprintf(stderr, "resolve_host_addr: bad address length\n");
        exit(1);
    }
    memcpy(addr, ent->h_addr_list[0], sizeof(*addr));
}

int main()
{
    signal(SIGPIPE, SIG_IGN);

    struct route_table routes;

    route_table_init(&routes);

    struct route static_route = {
        .kind = STATIC,
        .prefix = "/static",
        .r_static = {
            .root_path = "/srv/static/",
        },
    };
    route_table_add(&routes, &static_route);

    struct route sandbox_route = {
        .kind = STATIC_SANDBOX,
        .prefix = "/sandbox",
        .r_static = {
            .root_path = "/srv/uploads/",
        },
    };
    route_table_add(&routes, &sandbox_route);

    const char *proxy_host = getenv("PROXY_HOST");
    if (!proxy_host)
        proxy_host = "localhost";

    const char *proxy_port = getenv("PROXY_PORT");
    if (!proxy_port)
        proxy_port = "80";

    struct route proxy_route = {
        .kind = PROXY,
        .prefix = "/",
        .r_proxy = {
            .port = atoi(proxy_port),
        }
    };
    resolve_host_addr(&proxy_route.r_proxy.addr, proxy_host);
    route_table_add(&routes, &proxy_route);

    server_run(SERVER_PORT, &routes);
}
