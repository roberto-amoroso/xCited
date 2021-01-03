# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : utils.py
# @Project      : xCited
#########################################################
"""
General Utils
"""
#########################################################
import os
import sys
import unicodedata
import re
from console_manager import console
import argparse


class ErrorFetchingAuthor(Exception):
    """Raise when errors occur while downloading author information"""


def positive_integer(value):
    """Check if the argument is a positive Integer."""
    positive_val = int(value)
    if not positive_val > 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return positive_val


def scholar_id_type(arg_value):
    pattern = r"[\w-]{12}"
    if not re.match(pattern, arg_value):
        raise argparse.ArgumentTypeError(
            "The Google Scholar ID is a string of 12 characters corresponding to "
            "the value of the 'user' field in the URL of your profile."
        )
    return arg_value


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        console.print(f"{question + prompt}", style="main_style", end="")
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            console.print(
                "\nPlease respond with 'yes' or 'no' (or 'y' or 'n').\n",
                style="error_style",
            )


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.

    Notes:
    ------
    - From Django documentation: https://docs.djangoproject.com/en/3.0/_modules/django/utils/text/#slugify
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def create_directory(path):
    """
    Create directory at the given path, checking for errors and if the directory
    already exists.
    """
    path = os.path.realpath(path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            console.print(
                f"The syntax of the output file name, directory or volume is incorrect: '{path}'",
                style="error_style",
            )
        else:
            console.print(
                f'Created the output directory "{path}"',
                style="main_style",
                justify="center",
            )
    else:
        console.print(
            f'The output directory "{path}" already exists',
            style="main_style",
            justify="center",
        )
