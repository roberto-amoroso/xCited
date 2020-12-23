import sys

from rich import pretty
from colorama import init
from rich.console import Console

console = Console()

main_style = "bold blue"
error_style = "bold red"
list_elem_symbol = "\t[bold yellow]•[/bold yellow]"


def console_output_setup():
    """
    NOTES:
    ------
    - List of all emoji: https://www.webfx.com/tools/emoji-cheat-sheet/
    """
    # https://stackoverflow.com/questions/4374455/how-to-set-sys-stdout-encoding-in-python-3
    sys.stdout.reconfigure(encoding='utf-8')

    # https://pypi.org/project/colorama/
    init(autoreset=True)

    # https://github.com/willmcgugan/rich
    pretty.install()

    color_system = repr(console.color_system)
    is_terminal = console.is_terminal

    # https://github.com/willmcgugan/rich/issues/330
    if not is_terminal:
        console._force_terminal = True
