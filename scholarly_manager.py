# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : scholarly_manager.py
# @Project      : xCited
#########################################################
"""
Manager of the Scholarly package
"""
#########################################################

import os
import time
import sys

from scholarly import scholarly, ProxyGenerator
from rich.markdown import Markdown
from tqdm import tqdm

from console_manager import console, list_elem_symbol
from utils import create_directory, slugify, query_yes_no, ErrorFetchingAuthor
from downloader import download


def download_publications_pdf(author_id, filled_pubs, max_workers, verbose, dest_base_path='.'):
    eprinted_pubs = [pub for pub in filled_pubs if 'eprint_url' in pub.keys()]
    num_eprinted = len(eprinted_pubs)

    console.print("\n", Markdown(
        f"# Download PDF{'s' if num_eprinted > 1 else ''} ({num_eprinted}/{len(filled_pubs)} available)"),
                  style="main_style")

    path = os.path.join(dest_base_path, author_id)
    create_directory(path)

    urls = []
    dest_paths = []

    print()
    for pub in eprinted_pubs:
        dest_path = f"{pub['bib']['pub_year']}_{pub['bib']['title']}" if 'pub_year' in pub[
            'bib'].keys() else f"{pub['bib']['title']}"
        dest_path = slugify(dest_path) + '.pdf'
        dest_path = os.path.join(path, dest_path)
        urls.append(pub['eprint_url'])
        dest_paths.append(dest_path)

    t1 = time.time()
    downloaded_pubs = download(urls, dest_paths, max_workers=max_workers, verbose=verbose)
    t2 = time.time()

    console.print(Markdown(f"## Successfully downloaded {downloaded_pubs} out of {num_eprinted} "
                           f"PDF{'s' if num_eprinted > 1 else ''} in {round(t2 - t1, 2)} sec"),
                  style="main_style")

    return eprinted_pubs


def retrieve_publications_by_author_id(author_id, max_num_pubs=None):
    """
    Notes:
    ------
    https://github.com/scholarly-python-package/scholarly
    """
    console.print("\n", Markdown("\n# Processing Author info"), style="main_style")
    with console.status("[bold green]Downloading author info...") as status:  # spinner='material'
        try:
            search_query = scholarly.search_author_id(author_id)
        except Exception as e:
            console.print(
                f"\nError in fetching author info. Please change Proxy server or "
                f"check the inserted Google Scholar ID: '{author_id}'\n",
                style="error_style")
            raise ErrorFetchingAuthor
        author = scholarly.fill(search_query)
        empty_pubs = author['publications']
        num_pubs = max_num_pubs if max_num_pubs else len(empty_pubs)
        filled_pubs = []
        keys_blacklisted = ['publications', 'coauthors', 'source', 'container_type', 'filled']

    # console.print("\n", Markdown("\n# Author info:"), style="main_style")
    for key, value in author.items():
        if key not in keys_blacklisted:
            console.print("{} {:15s}: {}".format(list_elem_symbol, key, value))
    console.print("{} {:15s}: {}".format(list_elem_symbol, 'publications', num_pubs))

    console.print("\n", Markdown("\n# Download all publications info"), style="main_style")
    # TODO: use a ThreadPool to speed-up. ATTENTION: risk of too many requests to Google Scholar
    for i in tqdm(range(num_pubs), file=sys.stdout):
        try:
            filled_pubs.append(scholarly.fill(empty_pubs[i]))
        except Exception as e:
            console.print(
                f"\nError in downloading publications info. Please try again using another proxy server.\n",
                style="error_style")
            raise ErrorFetchingAuthor

    return filled_pubs


def proxy_manager():
    if query_yes_no("\nDo you want to use a Proxy? ([italic underline]Recommended[/italic underline])"):
        console.print("\n", Markdown("\n# Generating Proxy"), style="main_style")
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
        console.print("\n", Markdown("\n# Continue without Proxy"), style="warning_style")
