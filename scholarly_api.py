import sys
import os
import unicodedata
import re
import argparse

from scholarly import scholarly
from tqdm import tqdm
import urllib.request
from urllib.error import HTTPError


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
        type=str,
        help="The Google Scholar ID is a string of 12 characters corresponding to \n"
             "the value of the 'user' field in the URL of your profile.\n"
    )

    return parser.parse_args()


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
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


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
            print(f"The syntax of the output file name, directory or volume is incorrect: {path}")
        else:
            print('\n# Created the output directory "{}"'.format(path))
    else:
        print('\n# The output directory "{}" already exists'.format(path))


def download_file(download_url, filename, ext='.pdf'):
    # https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping
    req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        file = open(filename + ext, 'wb')
        file.write(response.read())
        file.close()
    except HTTPError as e:
        return e.code
    return 200


def retrieve_publications_by_author_id(author_id):
    """
    Notes:
    ------
    https://github.com/scholarly-python-package/scholarly
    """
    try:
        search_query = scholarly.search_author_id(author_id)
    except Exception as e:
        sys.exit(f"Error in fetching author info. Please check the inserted Google Scholar ID: '{author_id}'")
    author = scholarly.fill(search_query)
    empty_pubs = author['publications']
    num_pubs = len(empty_pubs)
    filled_pubs = []

    print("\n# Author info:")
    print("\t- {:15s}: {}".format('Scholar ID', author['scholar_id']))
    print("\t- {:15s}: {}".format('name', author['name']))
    print("\t- {:15s}: {}".format('affiliation', author['affiliation']))
    print("\t- {:15s}: {}".format('publications', num_pubs))
    print("\t- {:15s}: {}".format('citations', author['citedby']))
    print("\t- {:15s}: {}".format('h-index', author['hindex']))
    print("\t- {:15s}: {}".format('i10-index', author['i10index']))

    print(f"\n# Download all publications info")
    for i in tqdm(range(num_pubs), file=sys.stdout):
        filled_pubs.append(scholarly.fill(empty_pubs[i]))

    return filled_pubs


def download_publications_pdf(author_id, filled_pubs):
    eprinted_pubs = [pub for pub in filled_pubs if 'eprint_url' in pub.keys()]
    num_eprinted = len(eprinted_pubs)

    path = os.path.join(".", author_id)
    create_directory(path)

    print(f"\n# Download PDF ({num_eprinted}/{len(filled_pubs)} available)")
    for pub in tqdm(eprinted_pubs, file=sys.stdout):
        filename = f"{pub['bib']['pub_year']}_{pub['bib']['title']}"
        filename = slugify(filename)
        filename = os.path.join(path, filename)
        download_file(pub['eprint_url'], filename)

    return eprinted_pubs


def main():
    args = args_parser()
    author_id = args.scholar_id
    filled_pubs = retrieve_publications_by_author_id(author_id)
    eprinted_pubs = download_publications_pdf(author_id, filled_pubs)


if __name__ == '__main__':
    main()
