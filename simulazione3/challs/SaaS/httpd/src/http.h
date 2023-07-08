#ifndef HTTP_H
#define HTTP_H

#include <stdio.h>
#include <stdbool.h>

enum http_method {
    GET,
    POST,
};

enum http_version {
    HTTP_1_0,
    HTTP_1_1,
};

struct http_header {
    struct http_header *next;
    const char *name;
    const char *value;
};

struct http_headers {
    struct http_header *head;
    struct http_header *tail;
};

struct http_request {
    enum http_method method;
    char *headers_buf;
    char *path;
    char *query;
    enum http_version version;
    struct http_headers headers;
};

enum http_status {
    OK = 200,
    MOVED_PERMANENTLY = 301,
    FOUND = 302,
    SEE_OTHER = 303,
    TEMPORARY_REDIRECT = 307,
    PERMANENT_REDIRECT = 308,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    METHOD_NOT_ALLOWED = 405,
    REQUEST_TIMEOUT = 408,
    PAYLOAD_TOO_LARGE = 413,
    URI_TOO_LONG = 414,
    IM_A_TEAPOT = 418,
    TOO_MANY_REQUESTS = 429,
    INTERNAL_SERVER_ERROR = 500,
    NOT_IMPLEMENTED = 501,
};

struct http_response {
    enum http_version version;
    enum http_status status;
    struct http_headers headers;
    const void *body;
    size_t body_size;
};

bool http_request_read(struct http_request *req, int fd);
bool http_request_proxy(struct http_request *req, int req_fd, int dst_fd);
void http_request_print(const struct http_request *req, FILE *stream,
                        bool headers);
void http_request_destroy(struct http_request *req);

void http_response_init(struct http_response *resp, enum http_version version,
                        enum http_status status, const void *body,
                        size_t body_size);
void http_response_add_header(struct http_response *resp, const char *name,
                              const char *value);
bool http_response_send(const struct http_response *resp, int fd);
void http_response_destroy(struct http_response *resp);

struct http_header *http_headers_lookup(struct http_headers *headers,
                                        const char *name);

const char *http_method_str(enum http_method method);
const char *http_version_str(enum http_version version);
const char *http_status_str(enum http_status status);

#endif
