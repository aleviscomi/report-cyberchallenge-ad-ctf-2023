#define _POSIX_SOURCE /* fileno */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <netinet/in.h>

#include "util.h"

#define hex2int(c) (isdigit(c) ? (c) - '0' : toupper((c)) - 'A' + 10)

char *str_split(char *s, const char *delim)
{
    char *p = strstr(s, delim);
    if (!p)
        return NULL;

    size_t delim_len = strlen(delim);
    memset(p, 0, delim_len);
    return p + delim_len;
}

bool str_startswith(const char *s, const char *prefix)
{
    return !strncmp(s, prefix, strlen(prefix));
}

void urldecode(char *s)
{
    char *rptr = s, *wptr = s;
    while (*rptr) {
        if (rptr[0] == '%' && isxdigit(rptr[1]) && isxdigit(rptr[2])) {
            *wptr++ = (hex2int(rptr[1]) << 4) | hex2int(rptr[2]);
            rptr += 3;
        } else {
            *wptr++ = *rptr++;
        }
    }
    *wptr = '\0';
}

bool write_all(int fd, const void *buf, size_t size)
{
    size_t written = 0;
    while (written < size) {
        ssize_t count = write(fd, (const char *)buf + written, size - written);
        if (count < 0) {
            if (errno == EINTR)
                continue;
            perror("write");
            return false;
        }
        written += count;
    }
    return true;
}

bool write_str(int fd, const char *s)
{
    return write_all(fd, s, strlen(s));
}

char *read_file(const char *path, size_t *sizeptr, size_t max_size)
{
    char *buf = NULL;

    FILE *fp = fopen(path, "rb");
    if (!fp) {
        perror("fopen");
        return false;
    }

    struct stat st;
    if (fstat(fileno(fp), &st) < 0) {
        perror("fstat");
        goto fail;
    }

    if (!S_ISREG(st.st_mode))
        goto fail;

    if (max_size && (size_t)st.st_size > max_size)
        goto fail;

    buf = malloc(st.st_size);
    if (!buf) {
        perror("malloc");
        goto fail;
    }

    if (fread(buf, st.st_size, 1, fp) != 1) {
        perror("fread");
        goto fail;
    }

    fclose(fp);
    *sizeptr = st.st_size;
    return buf;

fail:
    fclose(fp);
    if (buf)
        free(buf);
    return NULL;
}

char *read_fd(int fd, size_t *sizeptr, size_t max_size)
{
    size_t buf_size = 128;
    if (buf_size > max_size)
        buf_size = max_size;

    char *buf = malloc(buf_size + 1);

    size_t read_size = 0;
    while (1) {
        ssize_t count = read(fd, buf + read_size, buf_size - read_size);
        if (count < 0) {
            perror("read");
            goto fail;
        }
        if (count == 0)
            break;

        read_size += count;

        if (read_size == max_size)
            break;

        if (read_size == buf_size) {
            buf_size *= 2;
            if (buf_size > max_size)
                buf_size = max_size;
            buf = realloc(buf, buf_size + 1);
        }
    }

    buf[read_size] = '\0';
    *sizeptr = read_size;

    return buf;

fail:
    free(buf);
    return NULL;
}

bool copy_fd(int dst_fd, int src_fd, size_t size)
{
    char buf[4096];

    bool copy_until_eof = !size;

    size_t done = 0;
    while (copy_until_eof || done < size) {
        size_t to_read = sizeof(buf);
        if (!copy_until_eof && to_read > size - done)
            to_read = size - done;

        ssize_t read_count = read(src_fd, buf, to_read);
        if (read_count < 0) {
            perror("read");
            return false;
        }
        if (read_count == 0)
            break;

        size_t written = 0;
        while (written < (size_t)read_count) {
            ssize_t write_count = write(dst_fd, buf, read_count - written);
            if (write_count < 0) {
                perror("write");
                return false;
            }
            written += write_count;
        }

        done += read_count;
    }

    return copy_until_eof || done == size;
}

int open_tcp_socket(const struct in_addr *addr, unsigned short port,
                    time_t timeout)
{
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct timeval to;
    to.tv_sec = timeout;
    to.tv_usec = 0;
    if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &to, sizeof(to)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        goto fail;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &to, sizeof(to)) < 0) {
        perror("setsockopt(SO_SNDTIMEO)");
        goto fail;
    }

    struct sockaddr_in saddr = {
        .sin_family = AF_INET,
        .sin_port = htons(port),
        .sin_zero = {0},
    };
    memcpy(&saddr.sin_addr, addr, sizeof(*addr));

    if (connect(fd, (struct sockaddr *)&saddr, sizeof(saddr)) < 0) {
        perror("connect");
        goto fail;
    }

    return fd;

fail:
    close(fd);
    return -1;
}
