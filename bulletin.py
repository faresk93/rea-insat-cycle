#!/usr/bin/env python3
"""Moyennes Cycle et Rangs, reimagined - INSAT CH2 2014-2015, by Fares Khiary.

A rich terminal take on cycle.py: gradient titles, large digits, animated
count-ups, class distribution charts and a final verdict. Data and ranking
come from cycle.py.

Type a student number or part of a name. Needs the `rich` package.

Environment:
  CYCLE_NO_DELAY=1   no animations or pauses (also off when stdout is not a tty)
  NO_COLOR=1         no colours
"""
import os
import random
import time
import unicodedata
from dataclasses import dataclass

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cycle import PASS_LIMIT, SPECIAL_NUMBER, load_students, tenth

console = Console(highlight=False)
ANIMATE = console.is_terminal and "CYCLE_NO_DELAY" not in os.environ
FPS = 30
CARD_WIDTH = 26

TITLE = ("#22d3ee", "#a78bfa", "#f472b6", "#fbbf24")
GOLD = ("#fde047", "#f59e0b", "#fde047")
PASS = ("#22c55e", "#a3e635", "#22d3ee")
FAIL = ("#ef4444", "#f97316")
SOFT = ("#93c5fd", "#c4b5fd")


@dataclass(frozen=True)
class Stat:
    field: str
    title: str
    digits: int
    colors: tuple
    subject: str  # used in verdict sentences


STATS = (
    Stat("cba", "MOYENNE CBA", 2, ("#34d399", "#22d3ee"), "CBA"),
    Stat("ch2", "MOYENNE CH2", 2, ("#fb7185", "#fb923c"), "CH2"),
    Stat("cycle", "MOYENNE CYCLE", 3, ("#a78bfa", "#f472b6"), "du cycle ingénieur"),
)

# 3-row digits drawn with box characters
GLYPHS = {
    "0": ("┏━┓", "┃ ┃", "┗━┛"),
    "1": ("╺┓ ", " ┃ ", "╺┻╸"),
    "2": ("┏━┓", "┏━┛", "┗━╸"),
    "3": ("┏━┓", "╺━┫", "┗━┛"),
    "4": ("╻ ╻", "┗━┫", "  ╹"),
    "5": ("┏━╸", "┗━┓", "┗━┛"),
    "6": ("┏━╸", "┣━┓", "┗━┛"),
    "7": ("┏━┓", "  ┃", "  ╹"),
    "8": ("┏━┓", "┣━┫", "┗━┛"),
    "9": ("┏━┓", "┗━┫", "┗━┛"),
    ".": (" ", " ", "▪"),
    "-": ("   ", "╺━╸", "   "),
    " ": ("   ", "   ", "   "),
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def big(s):
    return [" ".join(GLYPHS[c][row] for c in s) for row in range(3)]


def spaced(s):
    return " ".join(s)


def blend(stops, x):
    """Colour at position x in [0, 1] along a gradient."""
    seg = x * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    f = seg - i
    a = [int(stops[i][k:k + 2], 16) for k in (1, 3, 5)]
    b = [int(stops[i + 1][k:k + 2], 16) for k in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def gradient(lines, stops, phase=0.0, bold=True):
    """Text coloured left to right; phase slides the gradient for shimmer."""
    if isinstance(lines, str):
        lines = [lines]
    width = max(max(len(line) for line in lines) - 1, 1)
    text = Text(justify="center")
    for n, line in enumerate(lines):
        if n:
            text.append("\n")
        for col, ch in enumerate(line):
            pos = (col / width + phase) % 2
            color = blend(stops, pos if pos <= 1 else 2 - pos)
            text.append(ch, style=("bold " if bold else "") + color)
    return text


def sparkles(width, seed, stops):
    rng = random.Random(seed)
    text = Text(justify="center")
    for _ in range(width):
        ch = rng.choice("✦✧⋆·" + " " * 8)
        text.append(ch, style=blend(stops, rng.random()))
    return text


def ease(t):
    return 1 - (1 - t) ** 3


def pause(seconds):
    if ANIMATE:
        time.sleep(seconds)


def play(render, duration):
    """Animates render(t) for t from 0 to 1, leaving the last frame on screen."""
    if not ANIMATE:
        console.print(render(1.0))
        return
    frames = max(1, int(duration * FPS))
    with Live(render(0.0), console=console, auto_refresh=False) as live:
        for i in range(1, frames + 1):
            time.sleep(1 / FPS)
            live.update(render(i / frames), refresh=True)


def suspense(message, seconds):
    if ANIMATE:
        with console.status(Text(message, style="italic grey70"), spinner="dots12",
                            spinner_style="#a78bfa"):
            time.sleep(seconds)


# ---------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------

def band_label(r, total, field):
    t = tenth(r, total)
    if r == 1:
        return "★ MAJOR"
    if t <= (6 if field == "cycle" else 5):
        return "TOP %d0%%" % t
    if field == "cycle":
        return "TOP %d" % PASS_LIMIT if r <= PASS_LIMIT else "HORS TOP %d" % PASS_LIMIT
    return "2ᵉ MOITIÉ"


def sentence(stat, s, total):
    r = getattr(s, "rank_" + stat.field)
    t = tenth(r, total)
    if r == 1:
        return "Meilleure moyenne %s de la promo !" % stat.subject
    if t <= (6 if stat.field == "cycle" else 5):
        return "Parmi les %d0%% meilleures moyennes %s." % (t, stat.subject)
    if stat.field != "cycle":
        return "Dans la deuxième moitié des moyennes %s." % stat.subject
    if r <= PASS_LIMIT:
        return "Parmi les %d meilleures moyennes %s." % (PASS_LIMIT, stat.subject)
    return "Parmi les %d dernières moyennes %s." % (total - PASS_LIMIT - 1, stat.subject)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def intro():
    if ANIMATE:
        console.clear()
    console.print()

    def bismillah(t):
        color = blend(("#111111", "#fbbf24"), ease(t))
        return Group(
            Text("Au nom d'ALLAH", style="italic " + color, justify="center"),
            Text("le Tout Miséricordieux, le Très Miséricordieux",
                 style="italic " + color, justify="center"),
        )

    play(bismillah, 1.0)
    pause(0.4)
    console.print()

    def banner(t):
        phase = 2 * ease(t)
        return Panel(
            Group(
                Text(spaced("I.N.S.A.T") + "   ·   CH2", style="grey62", justify="center"),
                Text(),
                gradient(spaced("MOYENNES CYCLE") + "   &   " + spaced("RANGS"), TITLE, phase),
                Text(),
                gradient(big("2014-2015"), TITLE, phase + 0.5),
                Text(),
                Text("par Fares Khiary", style="italic grey58", justify="center"),
            ),
            box=box.ROUNDED, border_style="#7c3aed", padding=(1, 2), width=min(console.width, 78),
        )

    play(banner, 1.6)


def name_banner(s):
    full = "%s %s" % (s.prenom, s.nom)

    def render(t):
        shown = full[:round(len(full) * ease(t))]
        return Panel(
            Group(
                gradient(spaced(shown.upper()) or " ", TITLE),
                Text("N° %d  ·  CH2 2014–2015" % s.number, style="grey58", justify="center"),
            ),
            box=box.HEAVY, border_style="grey35", padding=(0, 2), width=min(console.width, 78),
        )

    play(render, 0.8)


def histogram(values, value, width, colors, t):
    """Two-row histogram of the class, the student's bar highlighted."""
    ordered = sorted(values)
    lo, hi = ordered[len(ordered) // 20], ordered[-1]  # ignore the extreme lows

    def column(v):
        return max(0, min(width - 1, int((v - lo) / (hi - lo) * width)))

    counts = [0] * width
    for v in values:
        counts[column(v)] += 1
    peak = max(counts)
    blocks = " ▁▂▃▄▅▆▇█"
    mine = column(value)
    rows = [Text(), Text()]
    for col, n in enumerate(counts):
        level = max(1, round(n / peak * 16)) if n else 0
        style = "bold white" if col == mine and t >= 1 else blend(colors, col / width) + " dim"
        rows[0].append(blocks[max(0, level - 8)], style=style)
        rows[1].append(blocks[min(8, level)], style=style)
    marker = Text(" " * round(mine * ease(t)) + "▲", style="bold white")
    scale = Text(("%.0f" % lo).ljust(width - 2) + "%.0f" % hi, style="grey42")
    return Group(*rows, marker, scale), lo


def card(stat, s, students, t):
    total = len(students)
    values = [getattr(x, stat.field) for x in students]
    value = getattr(s, stat.field)
    r = getattr(s, "rank_" + stat.field)
    inner = CARD_WIDTH - 4
    chart, lo = histogram(values, value, inner, stat.colors, t)

    e = ease(t)
    final = "%.*f" % (stat.digits, value)
    shown = ("%.*f" % (stat.digits, lo + (value - lo) * e)).rjust(len(final))
    rank_shown = total - round((total - r) * e)
    medal = {1: ("  ★", "bold #fde047"), 2: ("  ✦", "#e5e7eb"), 3: ("  ✦", "#d97706")}

    rank = Text.assemble(("RANG ", "grey58"), ("%2d" % rank_shown, "bold white"),
                         (" / %d" % total, "grey58"), medal.get(rank_shown, ("", "")))
    chip = Text(" %s " % band_label(r, total, stat.field),
                style="bold black on " + stat.colors[0]) if t >= 1 else Text(" ")
    body = Group(
        Text(stat.title, style="bold " + stat.colors[0]),
        Text(),
        Align.center(gradient(big(shown), stat.colors)),
        Text(),
        rank,
        Text(),
        chart,
        Text(),
        chip,
    )
    return Panel(body, box=box.ROUNDED, border_style=stat.colors[1],
                 width=CARD_WIDTH, padding=(0, 1))


def cards(s, students, t):
    panels = [card(stat, s, students, t) for stat in STATS]
    if console.width < CARD_WIDTH * 3:
        return Group(*panels)
    grid = Table.grid()
    for _ in panels:
        grid.add_column()
    grid.add_row(*panels)
    return Align.center(grid)


def verdict(s, total):
    r = s.rank_cycle
    first = s.prenom.split()[0]
    if r == 1:
        stops, border = GOLD, "#f59e0b"
        title = "★  " + spaced("MAJOR DE PROMO") + "  ★"
        lines = ["Félicitations %s ! Passage garanti, in sha'ALLAH." % first]
    elif r <= PASS_LIMIT:
        stops, border = PASS, "#22c55e"
        title = "✔  " + spaced("PASSAGE GARANTI")
        lines = ["Félicitations %s — in sha'ALLAH." % first]
    else:
        stops, border = FAIL, "#ef4444"
        title = spaced("DÉSOLÉ") + "  " + first.upper()
        lines = []
    lines.append(sentence(STATS[2], s, total))
    celebrate = r <= PASS_LIMIT
    width = min(console.width, 78)

    def render(t):
        frame = int(t * FPS * 2)
        parts = []
        if celebrate:
            parts += [sparkles(width - 6, frame, stops), Text()]
        parts.append(gradient(title, stops, phase=ease(t) * 2))
        parts.append(Text())
        parts += [Text(line, style="white" if n == 0 else "grey62", justify="center")
                  for n, line in enumerate(lines)]
        if celebrate:
            parts += [Text(), sparkles(width - 6, frame + 1000, stops)]
        return Panel(Group(*parts), box=box.DOUBLE, border_style=border,
                     padding=(1, 2), width=width)

    play(render, 2.0 if celebrate else 1.0)


def show_results(s, students):
    total = len(students)
    if ANIMATE:
        console.clear()
    console.print()
    console.rule(gradient("Moyennes Cycle & Rangs", TITLE), style="grey23")
    console.print()
    name_banner(s)
    console.print()
    play(lambda t: cards(s, students, t), 1.4)
    console.print()
    for stat in STATS:
        pause(0.35)
        console.print(Text.assemble(("  ● ", stat.colors[0]), (sentence(stat, s, total), "grey85")))
    console.print()
    suspense("Délibération du jury…", 1.8)
    verdict(s, total)


def show_special(s):
    console.print()

    def render(t):
        return Panel(
            Group(
                gradient("Bonne chance pour l'année prochaine", SOFT, phase=ease(t)),
                Text(),
                Text(s.prenom, style="bold #93c5fd", justify="center"),
            ),
            box=box.ROUNDED, border_style="#60a5fa", padding=(1, 2), width=min(console.width, 78),
        )

    play(render, 1.2)


def outro():
    console.print()

    def render(t):
        return Group(
            Text("Programme par", style="grey50", justify="center"),
            gradient(spaced("FARES KHIARY"), TITLE, phase=2 * ease(t)),
            Text(),
            Text("Peace ✌", style="bold white", justify="center"),
        )

    play(render, 1.4)
    console.print()


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def normalize(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def ask(prompt):
    """console.input that returns None at end of input."""
    try:
        return console.input(prompt).strip()
    except EOFError:
        console.print()
        return None


def choose_student(students):
    total = len(students)
    while True:
        answer = ask("\n[bold #22d3ee]›[/] [white]Numéro ou nom[/] [grey50](1–%d)[/] : " % total)
        if answer is None:
            return None
        if not answer:
            continue
        if answer.isdigit():
            if 1 <= int(answer) <= total:
                return students[int(answer) - 1]
            console.print("  [grey62]Le numéro doit être entre 1 et %d.[/]" % total)
            continue
        query = normalize(answer)
        found = [s for s in students if query in normalize("%s %s" % (s.prenom, s.nom))
                 or query in normalize("%s %s" % (s.nom, s.prenom))]
        if len(found) == 1:
            return found[0]
        if not found:
            console.print("  [grey62]Aucun étudiant ne correspond à « %s ».[/]" % answer)
            continue
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column(style="#22d3ee", justify="right")
        table.add_column()
        for s in found[:12]:
            table.add_row(str(s.number), "%s %s" % (s.prenom, s.nom))
        if len(found) > 12:
            table.add_row("…", "[grey50]%d autres[/]" % (len(found) - 12))
        console.print(table)


def again():
    while True:
        answer = ask("\n[white]Recommencer ?[/] [grey50]\\[o/n][/] ")
        if answer is None:
            return False
        if answer[:1].lower() in ("o", "n"):
            return answer[:1].lower() == "o"


def main():
    students = load_students()
    try:
        intro()
        while True:
            s = choose_student(students)
            if s is None:
                break
            if s.number == SPECIAL_NUMBER:
                show_special(s)
            else:
                show_results(s, students)
            if not again():
                break
        outro()
    except KeyboardInterrupt:
        console.print()


if __name__ == "__main__":
    main()
