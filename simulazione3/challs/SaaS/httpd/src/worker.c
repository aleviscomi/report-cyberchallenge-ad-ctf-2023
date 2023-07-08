#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <linux/limits.h>

#include "worker.h"
#include "server.h"
#include "http.h"
#include "util.h"
#include "route.h"
#include "sandbox.h"

#define PROXY_TIMEOUT 2
#define MAX_FILE_SIZE 16384

static bool check_path(const char *path)
{
    if (path[0] != '/')
        return false;

    for (const char *p = path; *p; p++) {
        if (p[0] == '/') {
            if (p[1] == '/')
                return false;
            if (p[1] == '.') {
                if (p[2] == '/' || !p[2])
                    return false;
                if (p[2] == '.' && (p[3] == '/' || !p[3]))
                    return false;
            }
        }
    }

    return true;
}

static void add_standard_headers(struct http_response *resp)
{
    http_response_add_header(resp, "Server", SERVER_NAME);
    http_response_add_header(resp, "Connection", "close");
}

static bool respond_bad_request(int fd, enum http_version version)
{
    struct http_response resp;
    http_response_init(&resp, version, BAD_REQUEST, "No hacks!", 9);
    add_standard_headers(&resp);
    bool ret = http_response_send(&resp, fd);
    http_response_destroy(&resp);
    return ret;
}

static bool respond_not_found(int fd, enum http_version version)
{
    struct http_response resp;
    http_response_init(&resp, version, NOT_FOUND, "Not found!", 10);
    add_standard_headers(&resp);
    bool ret = http_response_send(&resp, fd);
    http_response_destroy(&resp);
    return ret;
}

static bool respond_internal_server_error(int fd, enum http_version version)
{
    struct http_response resp;
    http_response_init(&resp, version, INTERNAL_SERVER_ERROR, "Uh-oh.", 6);
    add_standard_headers(&resp);
    bool ret = http_response_send(&resp, fd);
    http_response_destroy(&resp);
    return ret;
}

static bool handle_static(int fd, enum http_version version,
                          struct route_static *route, const char *suffix,
                          bool sandbox)
{
    char path[PATH_MAX];
    int ret = snprintf(path, sizeof(path), "%s/%s", route->root_path, suffix);
    if (ret < 0 || (unsigned)ret >= sizeof(path))
        return respond_not_found(fd, version);

    size_t file_size;
    char *file_content = read_file(path, &file_size, MAX_FILE_SIZE);
    if (!file_content)
        return respond_not_found(fd, version);

    char *body;
    size_t body_size;
    if (sandbox) {
        body = sandbox_run(file_content, file_size, &body_size);
        free(file_content);
        if (!body)
            return respond_internal_server_error(fd, version);
    } else {
        body = file_content;
        body_size = file_size;
    }

    struct http_response resp;
    http_response_init(&resp, version, OK, body, body_size);
    add_standard_headers(&resp);
    bool result = http_response_send(&resp, fd);
    http_response_destroy(&resp);

    free(body);
    return result;
}

static bool handle_proxy(int fd, struct http_request *req,
                         struct route_proxy *route)
{
    int dst_fd = open_tcp_socket(&route->addr, route->port, PROXY_TIMEOUT);
    if (dst_fd < 0)
        return false;

    bool ret = http_request_proxy(req, fd, dst_fd);

    close(dst_fd);
    return ret;
}

static bool handle_request(int fd, struct http_request *req,
                           const struct route_table *routes)
{
    if (!check_path(req->path))
        return respond_bad_request(fd, req->version);

    struct route *route = route_table_lookup(routes, req->path);
    if (!route)
        return respond_not_found(fd, req->version);

    const char *suffix = req->path + strlen(route->prefix);
    switch (route->kind) {
    case STATIC:
        return handle_static(fd, req->version, &route->r_static, suffix, false);
    case STATIC_SANDBOX:
        return handle_static(fd, req->version, &route->r_static, suffix, true);
    case PROXY:
        return handle_proxy(fd, req, &route->r_proxy);
    default:
        fprintf(stderr, "handle_request: bad route kind for %s\n",
                route->prefix);
        return false;
    }
}

bool worker_connection(int fd, const struct route_table *routes)
{
    bool ret = false, have_req = false;
    struct http_request req;

    if (!http_request_read(&req, fd)) {
        respond_bad_request(fd, HTTP_1_0);
        goto cleanup;
    }
    have_req = true;

    http_request_print(&req, stderr, false);

    urldecode(req.path);

    if (!handle_request(fd, &req, routes)) {
        respond_internal_server_error(fd, req.version);
        goto cleanup;
    }

    ret = true;

cleanup:
    if (have_req)
        http_request_destroy(&req);
    close(fd);
    return ret;
}
