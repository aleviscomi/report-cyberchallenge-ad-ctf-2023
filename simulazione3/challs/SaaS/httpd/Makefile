TARGET := httpd

SRCDIR := src
OBJDIR := obj
BINDIR := bin

CFLAGS := -fPIE -pthread -std=c11 -Wall -Wextra -Wswitch-enum
LDFLAGS := -pie -pthread
LIBS := -lseccomp

SRCS := $(wildcard $(SRCDIR)/*.c)
OBJS := $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(SRCS))

.SUFFIXES:
.DEFAULT_GOAL := all

$(OBJDIR) $(BINDIR):
	@mkdir -p $@

$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	@echo 'CC  $@'
	@$(CC) -c $(CFLAGS) -o $@ $<

$(BINDIR)/$(TARGET): $(OBJS) | $(BINDIR)
	@echo 'LNK $@'
	@$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

all: $(BINDIR)/$(TARGET)
.PHONY: all

clean:
	rm -rf $(OBJDIR) $(BINDIR)
.PHONY: clean
