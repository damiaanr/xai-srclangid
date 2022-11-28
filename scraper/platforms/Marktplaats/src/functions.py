import gzip
import re
import time
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Union as U, Tuple as T


def get_ad_html_by_id(id: int, cookie_string: str = None) \
                      -> U[T[str, str], bool]:
    """
    Returns the full HTML document of an ad from a single request. Only
    an ID is given which Marktplaats auto-increments and allows us to
    simply auto-DEcrement a recent ID to obtain multiple recent ads.

    In:
      @id:            Marktplaats ID of ad to fetch
      @cookie_string: Contents of cookie header (if None; no Cookies
                      header will  be sent with the request)

    Out:
      @html:
      @cookie_string: Cookie string based on response headers
    """

    # Marktplaats reads URLs dynamically with .htaccess mod rewrites;
    # So we just leave x's and change the ad ID at the end of the URL.
    base_url = 'https://www.marktplaats.nl/v/boeken/humor/m{id:d}-x-x'

    req = Request(base_url.format(id=id))

    # Marktplaats does seem to care about the user agent...
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
        + 'Gecko/20100101 Firefox/106.0'
    )

    # ... and other headers as well
    req.add_header(
        'Sec-Fetch-Mode',
        'navigate'
    )

    req.add_header(
        'Sec-Fetch-Site',
        'same-origin'
    )

    req.add_header(
        'Sec-Fetch-Dest',
        'document'
    )

    req.add_header(
        'Sec-Fetch-User',
        '?1'
    )

    req.add_header(
        'Accept-Encoding',
        'gzip'
    )

    # ... and in addition to that some cookies
    if cookie_string is not None:
        req.add_header(
            'Cookie',
            cookie_string
        )

    try:
        response = urlopen(req)
    except HTTPError as error:
        print('\r'+'Encountered an HTTP error: ', error)
        print('Occurred when requesting: ', base_url.format(id=id))

        # Marktplaats seems to throw a 503 when temporarily blocked
        if error.code == 503:
            return 503
        return False

    html = gzip.decompress(response.read()).decode('utf-8')

    # ... of which the 'luckynumber'-cookie seems a bit secret as it is
    # sometimes set randomly, and sometimes not set at all
    cookies = re.findall('(MpSession=[a-f0-9-]{36}|luckynumber=[0-9]{10})',
                         response.getheader('set-cookie'))

    if cookies:  # else cookie_string stays same (None or old version)
        cookie_string = '; '.join(cookies)

    return html, cookie_string


def get_recent_ad_id() -> int:
    """
    Extracts a recent ad id from the 'new ads nearby'-page on the
    homepage of Marktplaats to provide a starting point for scraping.

    In:
      - void

    Out:
      @id: Integer representing a recent Marktplaats ad identifier
    """
    try:
        overview_req = Request('https://www.marktplaats.nl/hp/api/feed-items'
                               '?feedType=NEARBY&postcode=1011AB&page=0')

        # It is a simple JSON feed, so no need for complex parsers
        overview_json = urlopen(overview_req).read().decode('utf-8')

        recent_ids = json.loads(overview_json)
    except Exception:
        raise Exception("Could not fetch starting ID (possible block)")

    return int(recent_ids[0]['itemId'][1:])


def get_recent_ad_ids(category_id: int = 2600, page: int = 0) -> dict:
    """
    Quick function written for Elize (for Hackathon)

    In:
      @category_id: Marktplaats category ID to scrape
      @page: Could be incremented gradually to obtain new results (but
             in practice not necessary)

    Out:
      @recent_ids: dict with ad ID as key and title of advertisement as
                   value
    """

    print('\r\n'+'New ad ids retrieved!')

    try:
        overview_req = Request('https://www.marktplaats.nl/cp/api/feed-items'
                               '?feedType=FOR_YOU'
                               '&categoryId=' + str(category_id) +
                               '&page=' + str(page))

        # It is a simple JSON feed, so no need for complex parsers
        overview_json = urlopen(overview_req).read().decode('utf-8')
        overview_data = json.loads(overview_json)

    except Exception:
        raise Exception("Could not fetch starting IDs (possible block)")

    recent_ids = {}
    for recent_id in overview_data:
        if recent_id['itemId'][0] != 'm':
            continue

        recent_ids[int(recent_id['itemId'][1:])] = recent_id['title']

    return recent_ids
