# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : argument_parser.py
# @Project      : xCited
#########################################################
"""
Arguments parser
"""
#########################################################

import argparse
import re


def scholar_id_type(arg_value):
    pattern = r"^[\w-]{12}$"
    if not re.match(pattern, arg_value):
        raise argparse.ArgumentTypeError(
            "The Google Scholar ID is a string of 12 characters corresponding to "
            "the value of the 'user' field in the URL of your profile."
        )
    return arg_value


def positive_integer(value):
    """Check if the argument is a positive Integer."""
    positive_val = int(value)
    if not positive_val > 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return positive_val


def args_parser():
    """Argument Parser"""
    parser = argparse.ArgumentParser(
        description="Enter an author's Google Scholar ID to download all PDFs of his/her publications.\n"
                    "The downloaded PDFs will be saved in the format:\n\n"
                    "\t'./<scholar_id>/<year_publication>_<title_publication>.pdf'\n",
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "scholar_id",
        type=scholar_id_type,
        help="the Google Scholar ID is a string of 12 characters corresponding to \n"
             "the value of the 'user' field in the URL of your profile.\n",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="if set, it shows a progress bar for each downloaded file, otherwise\n"
             "it shows a single progress bar for all files.\n",
    )

    parser.add_argument(
        "-w",
        "--num_workers",
        default=4,
        type=positive_integer,
        help="number of workers (threads) used during downloads (DEFAULT 4).\n",
    )

    return parser.parse_args()
