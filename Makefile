CC ?= gcc
CFLAGS ?= -std=c99 -Wall -Wextra -pedantic -O2
ORIGINAL ?= ../cycle.exe

cycle: cycle.c
	$(CC) $(CFLAGS) -o $@ cycle.c

# 32-bit Windows build, like the original (needs mingw-w64)
cycle.exe: cycle.c
	i686-w64-mingw32-gcc $(CFLAGS) -o $@ cycle.c

test: cycle
	python3 -I test_cycle.py $(ORIGINAL) ./cycle

test-py:
	python3 -I test_cycle.py $(ORIGINAL) ./cycle.py

clean:
	rm -f cycle cycle.exe

.PHONY: test test-py clean
