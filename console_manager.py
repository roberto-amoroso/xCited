# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : console_manager.py
# @Project      : xCited
#########################################################
"""
Console manager for Rich content
"""
#########################################################
import sys

from rich import pretty
from colorama import init
from rich.console import Console
from rich.theme import Theme
from rich.style import Style

from rich.progress import (
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    Progress,
)

# Colors: https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
custom_console_theme = Theme(
    {
        "main_style": "bold blue",
        "error_style": "bold red",
        "warning_style": Style(color="dark_orange3", bold=True),
    }
)

console = Console(theme=custom_console_theme)

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
    transient=True,
    refresh_per_second=2,
)

list_elem_symbol = "\t[bold yellow]•[/bold yellow]"


def console_output_setup():
    """
    NOTES:
    ------
    - List of all emoji: https://www.webfx.com/tools/emoji-cheat-sheet/
    """
    # https://stackoverflow.com/questions/4374455/how-to-set-sys-stdout-encoding-in-python-3
    sys.stdout.reconfigure(encoding="utf-8")

    # https://pypi.org/project/colorama/
    init(autoreset=True)

    # https://github.com/willmcgugan/rich
    pretty.install()

    color_system = repr(console.color_system)
    is_terminal = console.is_terminal

    # https://github.com/willmcgugan/rich/issues/330
    if not is_terminal:
        console._force_terminal = True
