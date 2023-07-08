#define _GNU_SOURCE /* MAP_ANONYMOUS */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <seccomp.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <sys/fcntl.h>
#include <syscall.h>

#include "sandbox.h"
#include "util.h"

#define RUN_TIMEOUT 5
#define MAX_OUTPUT_SIZE 4096

static void child(const void *code, size_t size, int outfd)
{
    /* Dup outfd as stdout. */
    if (dup2(outfd, 1) < 0) {
        perror("dup2");
        _exit(1);
    }
    /* Close all other open file descriptors. */
    close(0);
    for (int fd = 2; fd < 256; fd++)
        close(fd);

    /* Copy the code in executable memory */
    void *mem = mmap(NULL, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (mem == MAP_FAILED)
        _exit(1);
    memcpy(mem, code, size);

    /* Set timeout */
    alarm(RUN_TIMEOUT);

    /* Setup seccomp sandbox */
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    if (ctx == NULL)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0) < 0)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0) < 0)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(open), 1,
                         SCMP_A1(SCMP_CMP_EQ, O_RDONLY)) < 0)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) < 0)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) < 0)
        _exit(1);
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(getdents64), 0) < 0)
        _exit(1);
    if (seccomp_load(ctx) < 0)
        _exit(1);

    /* Call the code */
    ((void (*)(void))mem)();

    _exit(0);
}

char *sandbox_run(const void *code, size_t size, size_t *out_size)
{
    char *output = NULL;

    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe");
        return NULL;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return NULL;
    }

    if (!pid) {
        close(pipefd[0]);
        child(code, size, pipefd[1]);
    }

    close(pipefd[1]);

    output = read_fd(pipefd[0], out_size, MAX_OUTPUT_SIZE);
    close(pipefd[0]);

    int status;
    if (waitpid(pid, &status, 0) < 0) {
        perror("waitpid");
        goto fail;
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        fprintf(stderr, "sandbox_run: status %d\n", status);
        goto fail;
    }

    if (!output)
        goto fail;

    return output;

fail:
    free(output);
    return NULL;
}
