CC ?= cc
CFLAGS ?= -O2 -Wall -Wextra
CPPFLAGS ?=
LDFLAGS ?=

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

PROGRAM = build-ifo-dump
SCRIPTS = scripts/dvd-title-extract scripts/dvd-menu-extract scripts/dvd-extract

.PHONY: all clean install uninstall

all: $(PROGRAM)

$(PROGRAM): src/ifo_dump.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $< $(LDFLAGS) -ldvdread

clean:
	rm -f $(PROGRAM)

install: all
	install -d "$(DESTDIR)$(BINDIR)"
	install -m 755 $(PROGRAM) "$(DESTDIR)$(BINDIR)/dvd-ifo-dump"
	install -m 755 $(SCRIPTS) "$(DESTDIR)$(BINDIR)/"

uninstall:
	rm -f \
		"$(DESTDIR)$(BINDIR)/dvd-ifo-dump" \
		"$(DESTDIR)$(BINDIR)/dvd-title-extract" \
		"$(DESTDIR)$(BINDIR)/dvd-menu-extract" \
		"$(DESTDIR)$(BINDIR)/dvd-extract"
