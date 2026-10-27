#!/usr/bin/env python3
"""Check the C reconstruction against data read from the original cycle.exe.

Usage: python3 test_cycle.py [path/to/cycle.exe] [path/to/cycle]

The expected values are computed here from the tables in the original
binary's .data section, independently of cycle.c. The C program is then run
once per student number and its averages, ranks and verdicts are compared.
"""
import os
import re
import struct
import subprocess
import sys

N = 74
SPECIAL = 62

here = os.path.dirname(os.path.abspath(__file__))
exe_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "cycle.exe")
prog = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "cycle")

data = open(exe_path, "rb").read()


def file_offset(va):
    # .data: VA 0x405000 at file offset 0x3c00 (from the PE section table)
    return va - 0x405000 + 0x3C00


def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def floats(va):
    o = file_offset(va)
    return list(struct.unpack("<%df" % N, data[o:o + 4 * N]))


def names(va):
    o = file_offset(va)
    return [data[o + 20 * i:o + 20 * i + 20].split(b"\0")[0].decode() for i in range(N)]


cba = floats(0x405BE0)
ch2 = floats(0x405D20)
prenom = names(0x405600)


def cycle(i):
    a, b = cba[i], ch2[i]
    if i == 34:
        t = (b + 9.68) / 2 - 0.5
        return f32((a + 0.5 + 2 * t) / 3)
    if i == 51:
        return f32(((a + 9.89) / 2 - 0.5 + 19.38) / 3)
    if i == 69:
        return f32(((a + 9.47) / 2 - 0.5 + 21.66) / 3)
    if i in (3, 11, 33, 68):
        return f32((a + 0.5 + 2 * b) / 3)
    return f32((a + 0.5 + 2 * (b + 0.5)) / 3)


cyc = [cycle(i) for i in range(N)]


def rank(table, v):
    return 1 + sum(1 for x in table if x > v)


def band(r, first_tenth_limit):
    """Index of the tenth-of-class band: 0 = rank 1, 1 = 10%, 2 = 20%, ..."""
    if r == 1:
        return "best"
    if r <= first_tenth_limit:
        return "10%"
    for k, (lo, hi) in enumerate([(7.4, 14.8), (14.8, 22.2), (22.2, 29.6), (29.6, 37.0)], 2):
        if lo < r <= hi:
            return "%d0%%" % k
    return None


def expected_cba(r):
    b = band(r, 7)
    if b == "best":
        return "Vous avez eu la meilleure Moyenne CBA !"
    if b:
        return "Vous avez ete parmi %s des meilleures Moyennes CBA." % b
    return "Vous avez ete parmi la 2eme 50% des meilleures Moyennes CBA."


def expected_ch2(r, n):
    b = band(r, 7.4)
    if b == "best":
        return "Felicitations%s ! Vous avez la meilleure Moyenne CH2." % prenom[n - 1]
    if b:
        return "Vous etes parmi %s des meilleures Moyennes CH2." % b
    return "Vous etes parmi la 2eme 50% des meilleures Moyennes CH2."


def expected_cycle(r):
    b = band(r, 7.4)
    if b == "best":
        return "Vous avez la meilleure Moyenne Cycle Ingenieur."
    if b:
        return "Vous etes parmi %s des meilleures Moyennes Cycle Ingenieur." % b
    if 37 < r <= 44.4:
        return "Vous etes parmi 60% des meilleures Moyennes Cycle Ingenieur."
    if r <= 52:
        return "Vous etes parmi les 52 Meilleures Moyennes Cycle Ingenieur."
    return "Vous etes parmi les 21 dernieres Moyennes Cycle Ingenieur."


def run(stdin):
    env = dict(os.environ, CYCLE_NO_DELAY="1", NO_COLOR="1")
    out = subprocess.run([prog], input=stdin.encode(), capture_output=True,
                         env=env, timeout=30, check=True).stdout.decode()
    return out.replace("\b", "")


failures = []


def check(cond, what):
    if not cond:
        failures.append(what)


for n in range(1, N + 1):
    out = run("%d\nn\n" % n)
    i = n - 1
    if n == SPECIAL:
        check("Bonne Chance pour l'annee prochaine" + prenom[i] in out, "#%d special message" % n)
        check("-Moyenne" not in out, "#%d must not print results" % n)
        continue
    m = {k: re.search(r"-Moyenne %s *: ([0-9.]+)" % k, out) for k in ("CBA", "CH2", "Cycle")}
    ranks = re.findall(r"-(\d+)/74-", out)
    exp_ranks = [rank(cba, cba[i]), rank(ch2, ch2[i]), rank(cyc, cyc[i])]
    check(m["CBA"] and m["CBA"].group(1) == "%.2f" % cba[i], "#%d CBA average" % n)
    check(m["CH2"] and m["CH2"].group(1) == "%.2f" % ch2[i], "#%d CH2 average" % n)
    check(m["Cycle"] and m["Cycle"].group(1) == "%.3f" % cyc[i], "#%d cycle average" % n)
    # blink1 prints each rank string 4 times (2 passes x 2 colours)
    check([int(x) for x in ranks[::4]] == exp_ranks,
          "#%d ranks %s, expected %s" % (n, ranks[::4], exp_ranks))
    check(expected_cba(exp_ranks[0]) in out, "#%d CBA verdict" % n)
    check(expected_ch2(exp_ranks[1], n) in out, "#%d CH2 verdict" % n)
    check(expected_cycle(exp_ranks[2]) in out, "#%d cycle verdict" % n)
    if exp_ranks[2] <= 52:
        check("Passage Garanti" in out, "#%d Passage Garanti" % n)
    else:
        check("Desole" + prenom[i] in out, "#%d Desole" % n)

# Restart loop, and rejection of out-of-range and non-numeric input
out = run("0\n75\nabc\n5\nO\n6\nN\n")
check(out.count("Veuillez saisir votre nombre") == 2, "restart asks twice")
check(len(re.findall(r"-Moyenne Cycle", out)) == 2, "restart shows two results")
check("Peace !" in out, "program ends normally")

# End of input exits instead of looping forever
check("Peace !" in run(""), "EOF exits")

if failures:
    print("FAIL (%d)" % len(failures))
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("OK: %d students and input-handling cases match the original tables" % N)
