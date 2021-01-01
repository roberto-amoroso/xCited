# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : xCited.py
# @Project      : xCited
#########################################################
"""
xCited: Download all PDFs of an author's publications given the Google Scholar ID!
"""
#########################################################

import sys

from rich.markdown import Markdown

from argument_parser import args_parser
from console_manager import console_output_setup, console
from scholarly_manager import proxy_manager, download_publications_pdf, retrieve_publications_by_author_id
from utils import ErrorFetchingAuthor


def main():
    try:
        # - Console setup
        console_output_setup()

        # - Arguments parsing
        args = args_parser()
        author_id = args.scholar_id
        verbose = args.verbose
        num_workers = args.num_workers

        # - Starting xCited program
        console.print(Markdown("# Welcome to xCited!"), style="main_style")

        # - Proxy manager
        proxy_manager()

        # - Retrieve author information
        filled_pubs = retrieve_publications_by_author_id(author_id)

        # - Download the PDFs of the author's publications
        eprinted_pubs = download_publications_pdf(author_id, filled_pubs, max_workers=num_workers, verbose=verbose)
    except (KeyboardInterrupt, ErrorFetchingAuthor):
        pass

    # - Closing xCited
    console.print("\n", Markdown("\n# Closing xCited"), style="main_style")
    sys.exit()


if __name__ == '__main__':
    main()
