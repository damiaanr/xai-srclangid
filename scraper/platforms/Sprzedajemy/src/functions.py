import gzip
import re
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Union as U


def get_ad_html_by_id(id: int) -> U[str, bool]:
    """
    Returns the full HTML document of an ad from a single request. Only
    an ID is given which Sprzedajemy auto-increments and allows us to
    simply auto-DEcrement a recent ID to obtain multiple recent ads.

    In:
      @id:            Sprzedajemy ID of ad to fetch
      @cookie_string: Contents of cookie header (if None; no Cookies
                      header will  be sent with the request)

    Out:
      @html:
      @cookie_string: Cookie string based on response headers
    """

    # Sprzedajemy reads URLs dynamically with .htaccess mod rewrites;
    # So we just leave x's and change the ad ID at the end of the URL.
    base_url = 'https://sprzedajemy.pl/x-e1-nr{id:d}'

    req = Request(base_url.format(id=id))

    # Sprzedajemy seems to be only concerned about the User Agent
    #   Note: if not set, it will block the request.
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
        + 'Gecko/20100101 Firefox/106.0'
    )

    # Less data load
    req.add_header(
        'Accept-Encoding',
        'gzip'
    )

    try:
        response = urlopen(req)
    except HTTPError as error:
        print('\r'+'Encountered an HTTP error: ', error)
        print('Occurred when requesting: ', base_url.format(id=id))
        # time.sleep(0.6)  # could be an extra anti-block measure
        return False

    html = gzip.decompress(response.read()).decode('utf-8')

    return html


def get_recent_ad_id() -> int:
    """
    Extracts a recent ad id from a main page on Sprzedajemy to provide
    a starting point for scraping.

    In:
      - void

    Out:
      @id: Integer representing a recent Sprzedajemy ad identifier
    """
    overview_req = Request('https://sprzedajemy.pl/wszystkie-ogloszenia')
    overview_html = urlopen(overview_req).read().decode('utf-8')

    recent_id_match = re.search("<li id=\"offer-([0-9]*)\"", overview_html)

    if recent_id_match is None:
        raise Exception("Could not fetch starting ID (possible block)")

    return int(recent_id_match.group(1))
