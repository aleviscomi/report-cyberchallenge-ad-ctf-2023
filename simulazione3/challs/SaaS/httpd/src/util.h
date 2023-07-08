#ifndef UTIL_H
#define UTIL_H

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <netinet/in.h>

#define PERROR_EXIT(label) do { perror((label)); exit(1); } while (0)

char *str_split(char *s, const char *delim);
bool str_startswith(const char *s, const char *prefix);

void urldecode(char *s);

bool write_all(int fd, const void *buf, size_t size);
bool write_str(int fd, const char *s);

char *read_file(const char *path, size_t *sizeptr, size_t max_size);
char *read_fd(int fd, size_t *sizeptr, size_t max_size);

bool copy_fd(int dst_fd, int src_fd, size_t size);

int open_tcp_socket(const struct in_addr *addr, unsigned short port,
                    time_t timeout);

#endif
