#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>

#include "http.h"
#include "util.h"

#define MAX_HEADERS_LEN 8192
#define MAX_PROXY_CONTENT_LEN 16384

static void append_header(struct http_headers *hdrs, const char *name,
                          const char *value)
{
    struct http_header *hdr = malloc(sizeof(struct http_header));
    hdr->next = NULL;
    hdr->name = name;
    hdr->value = value;

    if (hdrs->tail)
        hdrs->tail->next = hdr;
    else
        hdrs->head = hdr;
    hdrs->tail = hdr;
}

static void free_headers(struct http_headers *hdrs)
{
    struct http_header *hdr = hdrs->head;
    while (hdr) {
        struct http_header *next = hdr->next;
        free(hdr);
        hdr = next;
    }
}

static char *read_request_headers(int fd)
{
    char *buf = malloc(MAX_HEADERS_LEN + 1);
    size_t size = 0;

    while (size < MAX_HEADERS_LEN) {
        ssize_t count = read(fd, buf + size, 1);
        if (count < 0)
            perror("read");
        if (count <= 0)
            break;
        size++;

        if (!memcmp(buf + size - 4, "\r\n\r\n", 4)) {
            buf[size] = '\0';
            return buf;
        }
    }

    free(buf);
    return NULL;
}

static bool parse_request_headers(struct http_request *req)
{
    char *method = req->headers_buf;
    char *p = str_split(method, " ");
    if (!p)
        return false;
    if (!strcmp(method, "GET"))
        req->method = GET;
    else if (!strcmp(method, "POST"))
        req->method = POST;
    else
        return false;

    req->path = p;
    p = str_split(req->path, " ");
    if (!p)
        return false;

    req->query = str_split(req->path, "?");

    char *version = p;
    p = str_split(version, "\r\n");
    if (!p)
        return false;
    if (!strcmp(version, "HTTP/1.0"))
        req->version = HTTP_1_0;
    else if (!strcmp(version, "HTTP/1.1"))
        req->version = HTTP_1_1;
    else
        return false;

    req->headers.head = req->headers.tail = NULL;
    while (1) {
        char *line = p;
        p = str_split(line, "\r\n");
        if (!p)
            return false;

        if (!line[0])
            break;

        char *name = line;
        char *value = str_split(line, ": ");
        if (!value)
            return false;

        append_header(&req->headers, name, value);
    }

    return true;
}

bool http_request_read(struct http_request *req, int fd)
{
    req->headers_buf = read_request_headers(fd);
    if (!req->headers_buf)
        return false;

    if (!parse_request_headers(req))
        return false;

    return true;
}

bool http_request_proxy(struct http_request *req, int req_fd, int dst_fd)
{
    struct http_header *hdr =
        http_headers_lookup(&req->headers, "Content-Length");
    size_t content_len = hdr ? atoi(hdr->value) : 0;
    if (content_len > MAX_PROXY_CONTENT_LEN)
        return false;

    const char *method = http_method_str(req->method);
    if (!write_str(dst_fd, method) || !write_str(dst_fd, " ") ||
        !write_str(dst_fd, req->path))
        return false;

    if (req->query) {
        if (!write_str(dst_fd, "?") || !write_str(dst_fd, req->query))
            return false;
    }

    const char *version = http_version_str(req->version);
    if (!write_str(dst_fd, " ") || !write_str(dst_fd, version) ||
        !write_str(dst_fd, "\r\n"))
        return false;

    for (struct http_header *hdr = req->headers.head; hdr; hdr = hdr->next) {
        if (!strcasecmp(hdr->name, "Connection"))
            continue;
        if (!write_str(dst_fd, hdr->name) || !write_str(dst_fd, ": ") ||
            !write_str(dst_fd, hdr->value) || !write_str(dst_fd, "\r\n"))
            return false;
    }

    if (!write_str(dst_fd, "Connection: close\r\n\r\n"))
        return false;

    if (content_len && !copy_fd(dst_fd, req_fd, content_len))
        return false;

    if (!copy_fd(req_fd, dst_fd, 0))
        return false;

    return true;
}

void http_request_print(const struct http_request *req, FILE *stream,
                        bool headers)
{
    const char *method = http_method_str(req->method);

    const char *version = http_version_str(req->version);

    fprintf(stream, "%s %s%s%s %s\n", method, req->path, req->query ? "?" : "",
            req->query ? req->query : "", version);

    if (headers) {
        for (struct http_header *hdr = req->headers.head; hdr; hdr = hdr->next)
            fprintf(stream, "%s: %s\n", hdr->name, hdr->value);
    }
}

void http_request_destroy(struct http_request *req)
{
    free(req->headers_buf);
    free_headers(&req->headers);
}

void http_response_init(struct http_response *resp, enum http_version version,
                        enum http_status status, const void *body,
                        size_t body_size)
{
    resp->version = version;
    resp->status = status;
    resp->headers.head = resp->headers.tail = NULL;
    resp->body = body;
    resp->body_size = body_size;
}

void http_response_add_header(struct http_response *resp, const char *name,
                              const char *value)
{
    append_header(&resp->headers, name, value);
}

bool http_response_send(const struct http_response *resp, int fd)
{
    const char *version = http_version_str(resp->version);
    if (!write_str(fd, version) || !write_str(fd, " "))
        return false;

    char status_code[4];
    snprintf(status_code, sizeof(status_code), "%d", (int)resp->status);
    const char *status_phrase = http_status_str(resp->status);
    if (!write_str(fd, status_code) || !write_str(fd, " ") ||
        !write_str(fd, status_phrase) || !write_str(fd, "\r\n"))
        return false;

    for (struct http_header *hdr = resp->headers.head; hdr; hdr = hdr->next) {
        if (!write_str(fd, hdr->name) || !write_str(fd, ": ") ||
            !write_str(fd, hdr->value) || !write_str(fd, "\r\n"))
            return false;
    }

    char buf[20+1];
    sprintf(buf, "%zu", resp->body_size);
    if (!write_str(fd, "Content-Length: ") || !write_str(fd, buf) ||
        !write_str(fd, "\r\n"))
        return false;

    if (!write_str(fd, "\r\n"))
        return false;

    if (resp->body_size && !write_all(fd, resp->body, resp->body_size))
        return false;

    return true;
}

void http_response_destroy(struct http_response *resp)
{
    free_headers(&resp->headers);
}

struct http_header *http_headers_lookup(struct http_headers *headers,
                                        const char *name)
{
    for (struct http_header *hdr = headers->head; hdr; hdr = hdr->next) {
        if (!strcasecmp(hdr->name, name))
            return hdr;
    }
    return NULL;
}

const char *http_method_str(enum http_method method)
{
    switch (method) {
    case GET:
        return "GET";
    case POST:
        return "POST";
    default:
        return "???";
    }
}

const char *http_version_str(enum http_version version)
{
    switch (version) {
    case HTTP_1_0:
        return "HTTP/1.0";
    case HTTP_1_1:
        return "HTTP/1.1";
    default:
        return "???";
    }
}

const char *http_status_str(enum http_status status)
{
    switch (status) {
    case OK:
        return "OK";
    case MOVED_PERMANENTLY:
        return "Moved Permanently";
    case FOUND:
        return "Found";
    case SEE_OTHER:
        return "See Other";
    case TEMPORARY_REDIRECT:
        return "Temporary Redirect";
    case PERMANENT_REDIRECT:
        return "Permanent Redirect";
    case BAD_REQUEST:
        return "Bad Request";
    case UNAUTHORIZED:
        return "Unauthorized";
    case FORBIDDEN:
        return "Forbidden";
    case NOT_FOUND:
        return "Not Found";
    case METHOD_NOT_ALLOWED:
        return "Method Not Allowed";
    case REQUEST_TIMEOUT:
        return "Request Timeout";
    case PAYLOAD_TOO_LARGE:
        return "Payload Too Large";
    case URI_TOO_LONG:
        return "URI Too Long";
    case IM_A_TEAPOT:
        return "I'm a teapot";
    case TOO_MANY_REQUESTS:
        return "Too Many Requests";
    case INTERNAL_SERVER_ERROR:
        return "Internal Server Error";
    case NOT_IMPLEMENTED:
        return "Not Implemented";
    default:
        return "???";
    }
}
