"""Présentation console, sans dépendance supplémentaire."""

import os
import sys


def supports_color():
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ:
        return False
    if os.name == "nt":
        # Active les couleurs ANSI dans le terminal Windows.
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.windll.kernel32
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        handle = kernel.GetStdHandle(-11)
        mode = wintypes.DWORD()
        return bool(
            kernel.GetConsoleMode(handle, ctypes.byref(mode))
            and kernel.SetConsoleMode(handle, mode.value | 0x0004)
        )
    return os.environ.get("TERM") != "dumb"


USE_COLOR = supports_color()
COLORS = {
    "title": "1;96", "muted": "90", "cold": "96",
    "warm": "93", "error": "91", "bold": "1",
}
WIDTH = 50

try:
    "╭─╮│╰╯".encode(sys.stdout.encoding or "utf-8")
    TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, LINE, SIDE = "╭╮╰╯─│"
except UnicodeEncodeError:
    TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, LINE, SIDE = "++++-|"


def style(text, color):
    return f"\033[{COLORS[color]}m{text}\033[0m" if USE_COLOR else text


def border(position):
    left, right = (TOP_LEFT, TOP_RIGHT) if position == "top" else (BOTTOM_LEFT, BOTTOM_RIGHT)
    print(style(left + LINE * WIDTH + right, "muted"))


def row(text="", color=None):
    content = f" {text:<{WIDTH - 2}} "
    print(style(SIDE, "muted") + (style(content, color) if color else content) + style(SIDE, "muted"))


def display_header():
    print()
    border("top")
    row("M É T É O   /   FRANCE", "title")
    row("Votre bulletin des 5 prochains jours")
    row("3 villes   /   Températures en °C", "muted")
    border("bottom")
    print()
    print("  " + style("MIN / minimale", "cold") + "    " + style("MAX / maximale", "warm"))


def display_city(city, days):
    print()
    border("top")
    row(city.split(",")[0], "title")
    row("FRANCE  /  Demain à J+5", "muted")
    row()
    row(f"{'JOUR / DATE':<24}{'MIN':>11}{'MAX':>11}", "muted")
    row(LINE * (WIDTH - 2), "muted")
    weekdays = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.", "Dim."]
    for index, (date, temperatures) in enumerate(days):
        label = "Demain" if index == 0 else weekdays[date.weekday()]
        label = f"{label} {date:%d/%m}"
        if temperatures is None:
            row(f"{label:<24}{'Indisponible':>22}", "muted")
            continue
        low = f"{temperatures['temp_min']:.1f} °C".replace(".", ",")
        high = f"{temperatures['temp_max']:.1f} °C".replace(".", ",")
        content = (
            f" {label:<24}"
            + style(f"{low:>11}", "cold")
            + style(f"{high:>11}", "warm")
            + "   "
        )
        print(style(SIDE, "muted") + content + style(SIDE, "muted"))
    row()
    border("bottom")


def display_error(title, message):
    print()
    print(style(f"  ! {title}", "error"))
    print(f"    {message}")


def display_footer():
    print()
    print(style("  Source : OpenWeather / prévisions toutes les 3 h", "muted"))
    print(style("  Min/max calculés sur les créneaux disponibles.", "muted"))
    print(style("  Le dernier jour peut être partiel.", "muted"))
    print()
