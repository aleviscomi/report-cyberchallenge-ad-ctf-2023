#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "server.h"
#include "worker.h"
#include "util.h"

#ifndef SO_REUSEPORT
#define SO_REUSEPORT 15
#endif

#define NUM_WORKERS 32
#define SOCKET_TIMEOUT 5

static int create_server_socket(int port)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0)
        PERROR_EXIT("socket");

    int optval = 1;
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)))
        PERROR_EXIT("setsockopt(SO_REUSEADDR)");
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval)))
        PERROR_EXIT("setsockopt(SO_REUSEPORT)");

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_addr = {htonl(INADDR_ANY)},
        .sin_zero = {0},
    };

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0)
        PERROR_EXIT("bind");

    if (listen(fd, SOMAXCONN) < 0)
        PERROR_EXIT("listen");

    return fd;
}

static void accept_connection(int server_fd, const struct route_table *routes)
{
    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(addr);

    int client_fd = accept(server_fd, (struct sockaddr *)&addr, &addrlen);
    if (client_fd < 0) {
        perror("accept");
        return;
    }

    struct timeval to;
    to.tv_sec = SOCKET_TIMEOUT;
    to.tv_usec = 0;
    if (setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &to, sizeof(to)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        return;
    }
    if (setsockopt(client_fd, SOL_SOCKET, SO_SNDTIMEO, &to, sizeof(to)) < 0) {
        perror("setsockopt(SO_SNDTIMEO)");
        return;
    }

    worker_connection(client_fd, routes);
}

static void server_process(int server_fd, const struct route_table *routes)
{
    while (1)
        accept_connection(server_fd, routes);
}

void server_run(int port, const struct route_table *routes)
{
    for (int i = 0; i < NUM_WORKERS; i++) {
        pid_t pid = fork();
        if (pid < 0)
            PERROR_EXIT("fork");
        if (pid == 0) {
            int server_fd = create_server_socket(port);
            server_process(server_fd, routes);
        }
    }

    int status;
    while (wait(&status) != -1) {
        if (WIFEXITED(status) && WEXITSTATUS(status) == 0)
            fprintf(stderr, "server_run: worker exited\n");
        else
            fprintf(stderr, "server_run: worker failed, status %d\n", status);
    }
}
