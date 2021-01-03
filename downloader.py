# !/usr/bin/python3
# -*- coding: utf-8 -*-
#########################################################
# {License_info}
#########################################################
# @Created By   : Roberto Amoroso
# @Creation Date: 12/31/2020 19:47
# @Filename     : downloader.py
# @Project      : xCited
#########################################################
"""
A URL downloader
"""
#########################################################

import concurrent
import time
import socket
from http.client import IncompleteRead
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os.path
import sys
from typing import List
from urllib.request import build_opener, HTTPCookieProcessor, Request, urlopen
from urllib.error import HTTPError, URLError
from tqdm import tqdm
from contextlib import nullcontext
from rich.progress import TaskID

import requests
import urllib3

from console_manager import console, progress

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def copy_url_requests(task_id: TaskID, url: str, path: str) -> int:
    """Copy data from a url to a local file.

    Notes:
    ------
    - Stream using Requests: https://2.python-requests.org/en/master/user/advanced/#body-content-workflow
    - Error 403: https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    - Timeout: https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
    - Cookie: https://stackoverflow.com/questions/29395407/enabling-cookies-with-urllib
    - Raise for status: https://requests.readthedocs.io/en/master/user/quickstart/#response-status-codes
    """

    response_code = 200
    try:
        r = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, stream=True
        )

        if r.status_code == requests.codes.ok:

            total = None

            # Avoiding break if the response doesn't contain content length
            if "Content-length" in r.headers.keys():
                total = int(r.headers["content-length"])

            progress.update(task_id, total=total)

            with open(path, "wb") as dest_file:
                progress.start_task(task_id)
                for data in r.iter_content(chunk_size=32768):
                    dest_file.write(data)
                    progress.update(task_id, advance=len(data))
        else:
            response_code = r.status_code
    except requests.exceptions.MissingSchema:
        response_code = -1
    except requests.exceptions.SSLError:
        # https://github.com/urllib3/urllib3/issues/1682
        copy_url_urllib(task_id, url, path)

    # progress.tasks[task_id].visible = False  # make invisible after the download finished
    progress.remove_task(task_id)
    return response_code


def copy_url_urllib(task_id: TaskID, url: str, path: str) -> int:
    """Copy data from a url to a local file.

    Notes:
    ------
    - Error 403: https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    - Timeout: https://requests.readthedocs.io/en/master/user/quickstart/#timeouts
    - Cookie: https://stackoverflow.com/questions/29395407/enabling-cookies-with-urllib
    """

    response_code = 200
    try:
        opener = build_opener(HTTPCookieProcessor())
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = opener.open(req, timeout=10)  # 10 seconds

        total = None

        # Avoiding break if the response doesn't contain content length
        if "Content-length" in response.info():
            total = int(response.info()["content-length"])

        progress.update(task_id, total=total)
        with open(path, "wb") as dest_file:
            progress.start_task(task_id)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task_id, advance=len(data))
    except (ValueError, IncompleteRead):
        response_code = -1
    except HTTPError as e:
        response_code = e.code
    except (URLError, socket.timeout):
        # Timeout
        response_code = 408

    # progress.tasks[task_id].visible = False  # make invisible after the download finished
    progress.remove_task(task_id)
    return response_code


def download(
        urls: List[str], dest_paths: List[str], max_workers: int = 4, verbose: bool = True
) -> int:
    """Download multiple files to the given directory.

    NOTES:
    ------
    - https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
    """

    assert len(urls) == len(
        dest_paths
    ), "There must be as many destination paths as URLs to download"

    downloaded_pubs = 0

    with progress if verbose else nullcontext():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {}

            for i, url in enumerate(urls):
                dest_path = dest_paths[i]

                assert dest_path, "Destination path cannot be None"

                filename = os.path.basename(dest_path)
                task_id = progress.add_task(
                    "download",
                    filename=f"{i}-" + ((filename[:50] + "..") if len(filename) > 50 else filename),
                    start=False,
                    visible=verbose,
                )
                future_to_url[
                    executor.submit(copy_url_urllib, task_id, url, dest_path)
                ] = url

            urls_completed = concurrent.futures.as_completed(future_to_url)

            url_iterator = range(len(urls))

            if not verbose:
                url_iterator = tqdm(url_iterator, file=sys.stdout)

            for _ in url_iterator:
                future = next(urls_completed)
                url = future_to_url[future]
                try:
                    status = future.result()
                except Exception as exc:
                    console.print(
                        "%r generated the following exception: %s" % (url, exc),
                        style="error_style",
                    )
                else:
                    if status == 200:
                        downloaded_pubs += 1
                    # console.print(f"\n-URL: {url}\n-Status: {status}\n")

    return downloaded_pubs
