#!/usr/bin/env python3
"""Moyennes Cycle et Rangs - INSAT CH2 2014-2015, by Fares Khiary.

Python rewrite of cycle.c. Asks for a student number, then shows their CBA,
CH2 and engineering-cycle averages with ranks and a verdict, animated in the
console like the original.

Environment:
  CYCLE_NO_DELAY=1   skip every pause and letter-by-letter delay
  NO_COLOR=1         disable colours (also disabled when stdout is not a tty)
"""
import os
import struct
import sys
import time
from dataclasses import dataclass
from enum import IntEnum


class Color(IntEnum):
    """conio colour numbers, as used by the original."""
    BLACK = 0
    BLUE = 1
    GREEN = 2
    CYAN = 3
    RED = 4
    MAGENTA = 5
    BROWN = 6
    LIGHTGRAY = 7
    DARKGRAY = 8
    LIGHTBLUE = 9
    LIGHTGREEN = 10
    LIGHTCYAN = 11
    LIGHTRED = 12
    LIGHTMAGENTA = 13
    YELLOW = 14
    WHITE = 15


# (nom, prenom, Moyenne CBA, Moyenne CH2), in student-number order.
STUDENTS = [
    ('Abidi',          'Mohamed',    12.06, 11.11),  # 1
    ('Achour',         'Nadya',      12.82, 12.01),  # 2
    ('Aidoudi',        'Meriem',     12.19, 12.29),  # 3
    ('Ajlani',         'Mahdi',      11.88, 10.36),  # 4
    ('Athamna',        'Jawaher',    12.06, 12.98),  # 5
    ('Ayadi',          'Nouha',      12.30, 10.90),  # 6
    ('Baccar',         'Nada',       12.79, 12.56),  # 7
    ('Baccouche',      'Oumayma',    12.16, 11.63),  # 8
    ('Baccouche',      'Hala',       12.22, 11.70),  # 9
    ('Baraket',        'Nada',       12.90, 11.09),  # 10
    ('Barguellil',     'Sana',       11.29, 11.16),  # 11
    ('Bargui',         'Emna',       10.60, 11.14),  # 12
    ('Barraj',         'Souad',      12.32, 12.08),  # 13
    ('Bel Skander',    'Sabrine',    12.25, 10.31),  # 14
    ('Ben Abdessamad', 'Montassar',  11.34, 10.56),  # 15
    ('Ben Ali',        'Rafeh',      12.22, 11.11),  # 16
    ('Ben Bouzayen',   'Abir',       13.34, 12.12),  # 17
    ('Ben Osman',      'Yasmine',    11.91, 11.66),  # 18
    ('Ben Wannes',     'Chayma',     11.75, 10.59),  # 19
    ('Borgini',        'Ahmed',      12.60, 11.79),  # 20
    ('Bouaziz',        'Nouha',      12.14, 10.76),  # 21
    ('Boubaker',       'Samar',      11.88, 10.37),  # 22
    ('Brahmi',         'Chayma',     13.71, 11.66),  # 23
    ('Brouri',         'Rania',      10.78, 10.74),  # 24
    ('Bzainia',        'Amir',       11.98, 10.30),  # 25
    ('Chaouch',        'Feriel',     12.32, 11.56),  # 26
    ('Chermitti',      'Ahmed',      13.34, 12.63),  # 27
    ('Chtioui',        'Marwa',      12.29, 11.96),  # 28
    ('Dami',           'Sabrine',    12.20, 10.42),  # 29
    ('Fennani',        'Hassen',     13.06, 11.95),  # 30
    ('Gdoura',         'Asma',       10.96, 12.50),  # 31
    ('Ghazouani',      'Nizar',      11.77, 12.43),  # 32
    ('Hafiene',        'Taheni',     11.88, 11.32),  # 33
    ('Hammami',        'Rawia',      10.99, 10.71),  # 34
    ('Hasni',          'Zoubeir',    10.06, 10.87),  # 35
    ('Hellal',         'Yesmine',    11.70, 10.69),  # 36
    ('Jaouadi',        'Hadhami',    14.11, 12.92),  # 37
    ('Jaouadi',        'Khaoula',    13.00, 12.84),  # 38
    ('Kacem',          'Fehmi',      11.72, 11.07),  # 39
    ('Kacem',          'Souha',      11.12, 12.96),  # 40
    ('Kamoun',         'Amira',      12.20, 10.41),  # 41
    ('Khedhiri',       'Khaoula',    14.59, 14.49),  # 42
    ('Khiary',         'Fares',      13.60, 11.90),  # 43
    ('Khlifi',         'Hiba',       12.94, 11.35),  # 44
    ('Kraiem',         'Abir',       11.87, 11.03),  # 45
    ('Kridene',        'Malek',      13.86, 12.51),  # 46
    ('Lahmer',         'Feten',      13.71, 11.83),  # 47
    ('Malouche',       'Nouha',      12.60, 12.24),  # 48
    ('Meddeb',         'Yomna',      13.32, 11.23),  # 49
    ('Mhadhbi',        'Aya',        14.11, 12.35),  # 50
    ('Mighri',         'Rimeh',      11.39, 11.24),  # 51
    ('Nalouti',        'Haythem',    11.46,  8.81),  # 52
    ('Nasr',           'Emna',       11.76, 12.09),  # 53
    ('Nefzi',          'Nesrine',    12.93, 12.50),  # 54
    ('Rachdi',         'Oumeima',    13.32, 10.62),  # 55
    ('Rezgui',         'Yosra',      12.29, 11.01),  # 56
    ('Rmili',          'Meriem',     12.69, 12.06),  # 57
    ('Saidi',          'Takwa',      13.97, 13.93),  # 58
    ('Sallami',        'Nour',       12.40, 13.63),  # 59
    ('Sayadi',         'Sabrine',    12.45, 12.61),  # 60
    ('Sghaier',        'Sirine',     12.66, 11.27),  # 61
    ('Smitti',         'MajdEddine', 10.78,  2.30),  # 62
    ('Soltani',        'Sinda',      13.94, 13.79),  # 63
    ('Souissi',        'Abir',       11.54, 11.61),  # 64
    ('Tarhouni',       'Sabri',      12.28, 10.23),  # 65
    ('Tahri',          'Marwa',      12.77, 11.43),  # 66
    ('Teyeb',          'Marwa',      12.20, 11.39),  # 67
    ('Trabelsi',       'Amani',      12.68, 11.23),  # 68
    ('Trabelsi',       'Rayhane',    11.85, 10.13),  # 69
    ('Yahmadi',        'Rihab',      11.27, 10.83),  # 70
    ('Zaghouani',      'Taoufik',    11.77, 12.67),  # 71
    ('Zammel',         'Amal',       13.14, 11.75),  # 72
    ('Zarrouk',        'Cyrine',     11.75, 10.70),  # 73
    ('Zouari',         'Hela Beya',  11.75, 11.90),  # 74
]

# Student who gets "Bonne Chance" instead of their results.
SPECIAL_NUMBER = 62

# Last cycle rank that passes.
PASS_LIMIT = 52


def f32(x):
    """Round to single precision, like the float tables of the original."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


def cycle_average(number, cba, ch2):
    """Moyenne Cycle = (CBA + 2 x CH2) / 3, with a 0.5 bonus on each part.

    The original hard-codes a few students, apparently resit averages.
    """
    if number == 35:
        t = (ch2 + 9.68) / 2 - 0.5
        return f32((cba + 0.5 + 2 * t) / 3)
    if number == 52:
        return f32(((cba + 9.89) / 2 - 0.5 + 19.38) / 3)
    if number == 70:
        return f32(((cba + 9.47) / 2 - 0.5 + 21.66) / 3)
    if number in (4, 12, 34, 69):  # no bonus on CH2
        return f32((cba + 0.5 + 2 * ch2) / 3)
    return f32((cba + 0.5 + 2 * (ch2 + 0.5)) / 3)


def rank(values, v):
    """Competition rank: 1 = best, ties share a rank."""
    return 1 + sum(1 for x in values if x > v)


def tenth(r, total):
    """Which tenth of the class rank r falls in: 1 for the top 10%, ..."""
    return -(-r * 10 // total)


@dataclass
class Student:
    number: int
    nom: str
    prenom: str
    cba: float
    ch2: float
    cycle: float
    rank_cba: int = 0
    rank_ch2: int = 0
    rank_cycle: int = 0

    @property
    def full_name(self):
        return " %s %s " % (self.prenom, self.nom)


def load_students():
    students = []
    for number, (nom, prenom, cba, ch2) in enumerate(STUDENTS, 1):
        cba, ch2 = f32(cba), f32(ch2)
        students.append(Student(number, nom, prenom, cba, ch2,
                                cycle_average(number, cba, ch2)))
    for field in ("cba", "ch2", "cycle"):
        values = [getattr(s, field) for s in students]
        for s in students:
            setattr(s, "rank_" + field, rank(values, getattr(s, field)))
    return students


class Console:
    """Coloured, animated output (stands in for the original's conio2)."""

    CENTER = 40  # middle of an 80-column console

    def __init__(self, out=sys.stdout):
        self.out = out
        self.colors = "NO_COLOR" not in os.environ and out.isatty()
        self.delays = "CYCLE_NO_DELAY" not in os.environ
        if self.colors and os.name == "nt":
            os.system("")  # enables ANSI escape codes in the Windows console

    def write(self, s):
        self.out.write(s)

    def pause(self, ms):
        self.out.flush()
        if self.delays:
            time.sleep(ms / 1000)

    def color(self, fg=None, bg=None):
        if not self.colors:
            return
        # conio order is BGR, ANSI order is RGB
        ansi = (0, 4, 2, 6, 1, 5, 3, 7)
        if fg is not None:
            self.write("\033[%dm" % (ansi[fg & 7] + (90 if fg & 8 else 30)))
        if bg is not None:
            self.write("\033[%dm" % (ansi[bg & 7] + (100 if bg & 8 else 40)))

    def reset(self):
        if self.colors:
            self.write("\033[0m")
        self.out.flush()

    def center(self, s):
        self.write(" " * max(self.CENTER - len(s) // 2, 1))

    def back(self, s):
        self.write("\b" * len(s))

    def type(self, s, ms=30, center=False):
        """Types s one character at a time, ms milliseconds per character."""
        if center:
            self.center(s)
        for c in s:
            self.write(c)
            self.pause(ms)

    def blink(self, s, c1, c2, times, center=False):
        """Prints s alternating colours c1/c2, overwriting itself."""
        if center:
            self.center(s)
        for i in range(times):
            if i:
                self.back(s)
            for c in (c1, c2):
                if c == c2:
                    self.back(s)
                self.color(c)
                self.write(s)
                self.pause(550)

    def type_blink(self, s, c1, c2, times, center=False):
        """Like blink but types the text; ends with the cursor rewound."""
        if center:
            self.center(s)
        for _ in range(times):
            for c in (c1, c2):
                self.color(c)
                self.type(s)
                self.pause(50)
                self.back(s)

    def invert_blink(self, s, times, center=False):
        """Alternates s between white-on-black and black-on-white."""
        if center:
            self.center(s)
        for _ in range(times):
            for fg, bg in ((Color.WHITE, Color.BLACK), (Color.BLACK, Color.WHITE)):
                self.color(fg, bg)
                self.write(s)
                self.pause(600)
                self.back(s)

    def dots(self):
        """'Thinking' dots before a verdict."""
        self.pause(800)
        for i in range(4):
            self.write("\n .")
            if i < 3:
                self.pause(600)
        self.write("\n\n ")
        self.pause(1000)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def header(con):
    con.write("\n")
    con.color(Color.GREEN)
    con.type("* Au nom d'ALLAH *\n", 40, center=True)
    con.pause(500)
    con.type("** le Tout Misericordieux, le Tres Misericordieux **", 40, center=True)
    con.write("\n\n")
    con.pause(700)
    con.color(Color.RED, Color.BLACK)
    con.type("-I.N.S.A.T-\n", center=True)
    con.pause(400)
    con.color(Color.MAGENTA)
    con.type("-CH2 |2014-2015|-\n\n", center=True)
    con.pause(600)
    con.color(Color.LIGHTRED)
    con.blink("-\\_Moyennes Cycle et Rangs_/-", Color.RED, Color.LIGHTRED, 3, center=True)
    con.write("\n\n")
    con.type_blink("-Fares Khiary-", Color.DARKGRAY, Color.LIGHTGRAY, 2, center=True)
    con.write("\n")
    con.type("--------------", 5, center=True)
    con.write("\n\n")
    con.pause(600)
    con.color(Color.WHITE, Color.BLACK)


def footer(con):
    con.write("\n" * 25 + " " * 42)
    con.type("Programme par : ")
    con.pause(500)
    con.type_blink("-Fares Khiary-", Color.DARKGRAY, Color.LIGHTGRAY, 3)
    con.invert_blink("-Fares Khiary-", 1)
    con.color(bg=Color.BLACK)
    con.write("\n\n" + " " * 42)
    con.pause(1000)
    con.color(Color.WHITE)
    con.type("Peace !\n\n")
    con.pause(1000)
    con.reset()


def say_name(con, s, after=Color.WHITE):
    con.color(Color.LIGHTCYAN, Color.BLACK)
    con.type(" " + s.prenom)
    con.color(after)


def average_line(con, label, value, digits, rank_label, rank_value, total,
                 light, dark):
    con.color(light, Color.BLACK)
    con.type(label)
    con.color(Color.WHITE)
    con.write("%.*f" % (digits, value))
    con.color(dark)
    con.pause(700)
    con.type(rank_label)
    con.color(light)
    con.write(": ")
    con.color(Color.BLACK, dark)
    con.blink("-%d/%d-" % (rank_value, total), Color.BLACK, Color.WHITE, 2)
    con.color(bg=Color.BLACK)


def passage_garanti(con, s, blinks, greeting=" Felicitations", ms=50):
    con.dots()
    con.type(greeting, ms)
    say_name(con, s)
    con.pause(800)
    con.type(" ----> ", 60)
    con.pause(400)
    con.type("in sha'ALLAH ", 60)
    con.pause(300)
    con.color(Color.GREEN, Color.LIGHTGREEN)
    con.blink(" Passage Garanti ", Color.WHITE, Color.BLACK, blinks)
    con.color(Color.WHITE, Color.BLACK)


def verdict_cba(con, r, total):
    con.color(Color.WHITE)
    t = tenth(r, total)
    if r == 1:
        con.type("\n Vous avez eu la meilleure Moyenne CBA !")
    elif t <= 5:
        con.type("\n Vous avez ete parmi %d0%% des meilleures Moyennes CBA." % t)
    else:
        con.type("\n Vous avez ete parmi la 2eme 50% des meilleures Moyennes CBA.")
    con.write("\n")


def verdict_ch2(con, s, total):
    con.color(Color.WHITE)
    t = tenth(s.rank_ch2, total)
    if s.rank_ch2 == 1:
        con.type("\n Felicitations")
        say_name(con, s)
        con.type(" ! Vous avez la meilleure Moyenne CH2.")
    elif t <= 5:
        con.type("\n Vous etes parmi %d0%% des meilleures Moyennes CH2." % t)
    else:
        con.type("\n Vous etes parmi la 2eme 50% des meilleures Moyennes CH2.")
    con.write("\n")


def verdict_cycle(con, s, total):
    con.color(Color.WHITE)
    r = s.rank_cycle
    t = tenth(r, total)
    if r == 1:
        con.type("\n Felicitations")
        say_name(con, s)
        con.type(" ! Vous avez la meilleure Moyenne Cycle Ingenieur.")
        passage_garanti(con, s, 6, " Felicitations encore", 30)
    elif t <= 6:
        con.type("\n Vous etes parmi %d0%% des meilleures Moyennes Cycle Ingenieur." % t)
        passage_garanti(con, s, 6)
    elif r <= PASS_LIMIT:
        con.type("\n Vous etes parmi les %d Meilleures Moyennes Cycle Ingenieur."
                 % PASS_LIMIT)
        passage_garanti(con, s, 3)
    else:
        con.dots()
        con.type(" Desole", 50)
        say_name(con, s, after=Color.RED)
        con.pause(1000)
        con.type(" Vous etes parmi les %d dernieres Moyennes Cycle Ingenieur."
                 % (total - PASS_LIMIT - 1), 50)
    con.color(Color.BLACK)


def show_results(con, s, total):
    con.write("\n\n")
    con.invert_blink(s.full_name, 3, center=True)
    con.write("\n\n")
    con.pause(1000)

    average_line(con, "\n-Moyenne CBA   : ", s.cba, 2, "  | Rang CBA   ",
                 s.rank_cba, total, Color.LIGHTGREEN, Color.GREEN)
    verdict_cba(con, s.rank_cba, total)
    con.pause(1000)

    average_line(con, "\n-Moyenne CH2   : ", s.ch2, 2, "  | Rang CH2   ",
                 s.rank_ch2, total, Color.LIGHTRED, Color.RED)
    verdict_ch2(con, s, total)
    con.pause(500)

    con.write("\n\n")
    con.pause(1000)
    average_line(con, "-Moyenne Cycle : ", s.cycle, 3, " | Rang Cycle ",
                 s.rank_cycle, total, Color.LIGHTMAGENTA, Color.MAGENTA)
    verdict_cycle(con, s, total)
    con.pause(800)


def show_special(con, s):
    con.type("\n\nBonne Chance pour l'annee prochaine")
    say_name(con, s, after=Color.BLACK)
    con.pause(500)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def tokens(stream):
    for line in stream:
        yield from line.split()


def ask_number(con, words, total):
    """Reads a student number, silently skipping invalid input.

    Returns None at end of input.
    """
    con.color(Color.WHITE)
    con.write("\n\n\n")
    con.pause(1000)
    con.type(" Veuillez saisir votre nombre : ")
    con.out.flush()
    for word in words:
        if word.isdigit() and 1 <= int(word) <= total:
            return int(word)
    return None


def ask_again(con, words):
    con.color(Color.WHITE)
    con.write("\n\n\n")
    con.pause(2000)
    con.type("Recommencer ?")
    con.pause(500)
    con.type("\nOui : O")
    con.type("\nNon : N     ")
    con.out.flush()
    for word in words:
        answer = word[0].lower()
        if answer in "on":
            return answer == "o"
    return False


def main():
    students = load_students()
    total = len(students)
    con = Console()
    words = tokens(sys.stdin)
    try:
        header(con)
        while True:
            number = ask_number(con, words, total)
            if number is None:
                break
            s = students[number - 1]
            if number == SPECIAL_NUMBER:
                show_special(con, s)
            else:
                show_results(con, s, total)
            if not ask_again(con, words):
                break
        footer(con)
    except KeyboardInterrupt:
        con.reset()
        print()
    if os.name == "nt" and sys.stdout.isatty():
        input("Appuyez sur Entree pour quitter...")


if __name__ == "__main__":
    main()
