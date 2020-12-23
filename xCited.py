import codecs
import sys
import os
import re
import argparse
import time

from scholarly import scholarly, ProxyGenerator
from rich.markdown import Markdown
import click
import rich
from rich.console import Console

from tqdm import tqdm
import urllib.request
from urllib.error import HTTPError, URLError

from console_manager import console_output_setup, console, main_style, error_style, list_elem_symbol
from utils import create_directory, slugify, query_yes_no


class ErrorFetchingAuthor(Exception):
    """Raise for my specific kind of exception"""


def scholar_id_type(arg_value):
    pattern = r"[\w-]{12}"
    if not re.match(pattern, arg_value):
        raise argparse.ArgumentTypeError("The Google Scholar ID is a string of 12 characters corresponding to "
                                         "the value of the 'user' field in the URL of your profile.")
    return arg_value


def args_parser():
    """ Argument Parser
    """
    parser = argparse.ArgumentParser(
        description="Enter an author's Google Scholar ID to download all PDFs of his/her publications.\n"
                    "The downloaded PDFs will be saved in the format:\n\n"
                    "\t'./<scholar_id>/<year_publication>_<title_publication>.pdf'\n",
        epilog="",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "scholar_id",
        type=scholar_id_type,
        help="The Google Scholar ID is a string of 12 characters corresponding to \n"
             "the value of the 'user' field in the URL of your profile.\n"
    )

    return parser.parse_args()


def download_file(download_url, filename, ext='.pdf'):
    """
    Notes:
    ------
    - Error 403: https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    - Timeout: https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
    """
    # Useful
    # https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, timeout=10)  # 10 seconds
        file = open(filename + ext, 'wb')
        file.write(response.read())
        file.close()
    except HTTPError as e:
        return e.code
    except URLError:
        # console.print(f"Timeout for: {download_url}")
        return 408
    return 200


def retrieve_publications_by_author_id(author_id, max_num_pubs=None):
    """
    Notes:
    ------
    https://github.com/scholarly-python-package/scholarly
    """
    console.print("\n", Markdown("\n# Processing Author info"), style=main_style)
    with console.status("[bold green]Downloading author info...") as status:  # spinner='material'
        try:
            search_query = scholarly.search_author_id(author_id)
        except Exception as e:
            console.print(
                f"\nError in fetching author info. Please check the inserted Google Scholar ID: '{author_id}'\n",
                style=error_style)
            raise ErrorFetchingAuthor
        author = scholarly.fill(search_query)
        empty_pubs = author['publications']
        num_pubs = max_num_pubs if max_num_pubs else len(empty_pubs)
        filled_pubs = []
        keys_blacklisted = ['publications', 'coauthors', 'source', 'container_type', 'filled']

    # console.print("\n", Markdown("\n# Author info:"), style=main_style)
    for key, value in author.items():
        if key not in keys_blacklisted:
            console.print("{} {:15s}: {}".format(list_elem_symbol, key, value))
    console.print("{} {:15s}: {}".format(list_elem_symbol, 'publications', num_pubs))

    console.print("\n", Markdown("\n# Download all publications info"), style=main_style)
    for i in tqdm(range(num_pubs), file=sys.stdout):
        filled_pubs.append(scholarly.fill(empty_pubs[i]))

    return filled_pubs


def download_publications_pdf(author_id, filled_pubs):
    eprinted_pubs = [pub for pub in filled_pubs if 'eprint_url' in pub.keys()]
    num_eprinted = len(eprinted_pubs)

    console.print("\n", Markdown(
        f"# Download PDF{'s' if num_eprinted > 1 else ''} ({num_eprinted}/{len(filled_pubs)} available)"),
                  style=main_style)

    path = os.path.join(".", author_id)
    create_directory(path)

    downloaded_pubs = 0
    for pub in tqdm(eprinted_pubs, file=sys.stdout):
        filename = f"{pub['bib']['pub_year']}_{pub['bib']['title']}" if 'pub_year' in pub[
            'bib'].keys() else f"{pub['bib']['title']}"
        filename = slugify(filename)
        filename = os.path.join(path, filename)
        status = download_file(pub['eprint_url'], filename)
        if status == 200:
            downloaded_pubs += 1
    console.print(Markdown(
        f"## Successfully downloaded {downloaded_pubs} out of {num_eprinted} PDF{'s' if num_eprinted > 1 else ''}"),
        style=main_style)

    return eprinted_pubs


def proxy_manager():
    if query_yes_no("\nDo you want to use a Proxy? ([italic underline]Recommended[/italic underline])"):
        console.print("\n", Markdown("\n# Generating Proxy"), style=main_style)
        with console.status("[bold green]Looking for a proxy...") as status:  # spinner='material'
            t1 = time.time()
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)
            t2 = time.time()

        console.print("{} {:15s}: {:.2f} sec".format(list_elem_symbol, "Elapsed time:", t2 - t1))

        proxy_info = pg._session.proxies
        for key, value in proxy_info.items():
            console.print("{} {:15s}: {}".format(list_elem_symbol, key, value))
    else:
        console.print("\n", Markdown("\n# Continue without Proxy"), style=error_style)


def main():
    try:
        console_output_setup()
        args = args_parser()
        author_id = args.scholar_id

        console.print(Markdown("# Welcome to xCited!"), style=main_style)

        proxy_manager()

        filled_pubs = retrieve_publications_by_author_id(author_id)
        eprinted_pubs = download_publications_pdf(author_id, filled_pubs)
    except (KeyboardInterrupt, ErrorFetchingAuthor):
        pass
    console.print("\n", Markdown("\n# Closing xCited"), style=main_style)
    sys.exit()


if __name__ == '__main__':
    main()
