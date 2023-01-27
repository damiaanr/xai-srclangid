import gzip
import re
import time
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import Union as U, Tuple as T


# below dicts are simple mappings that are useful for making sense of
# Vinted's many websites and corresponding dominant languages
vinted_country_id_to_lang_ISO639_3 = {
    1:  'lit', 2:  'deu', 3:  'ces', 7:  'spa',
    10: 'nld', 12: 'swe', 13: 'eng', 15: 'pol',
    18: 'ita', 21: 'por', 22: 'slk', 24: 'hun'
}


# simple key-values reversal of vinted_country_id_to_lang_ISO639_3 dict
vinted_lang_ISO639_3_to_country_id = dict(
    reversed(lang) for lang in vinted_country_id_to_lang_ISO639_3.items())


# mainly needed for fetching recent advertisement ids
vinted_country_id_to_tld = {
    1:  'lt', 2:  'de', 3:  'cz',    7:  'es',
    10: 'nl', 12: 'se', 13: 'co.uk', 15: 'pl',
    18: 'it', 21: 'pt', 22: 'sk',    24: 'hu'
}


def get_cookie_string(tld: str = 'co.uk') -> str:
    """
    Vinted strictly requires the _vinted_fr_session cookie to be set
    on all API requests. This cookie can simply be fetched from the
    main homepage.

    In:
      @tld: if None, the .co.uk version of the site will be loaded

    Out:
      @cookie_string: Cookie header containing _vinted_fr_session
    """
    base_url = 'https://www.vinted.{tld:s}'

    req = Request(base_url.format(tld=tld))

    # Otherwise 403 Forbidden
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
        + 'Gecko/20100101 Firefox/106.0'
    )

    try:
        response = urlopen(req)
    except HTTPError as error:
        print('\r'+'Encountered an HTTP error: ', error)
        print('Occurred when requesting: ', base_url.format(tld=tld))
        raise Exception("Could not load main product page")

    cookies = re.findall('(_vinted_fr_session=[^;]*);',
                         response.getheader('set-cookie'))

    if not cookies:
        raise Exception("Could not fetch secret cookie")

    cookie_string = cookies[0]  # could have used re.search as well

    return cookie_string


def get_ad_text_by_id(id: int, cookie_string: str = None,
                      tld: str = '.co.uk') -> U[T[str, str, str], bool]:
    """
    Returns the full HTML document of an ad from a single request. Only
    an ID is given which Marktplaats auto-increments and allows us to
    simply auto-DEcrement a recent ID to obtain multiple recent ads.

    In:
      @id:            Vinted ID of ad to fetch
      @cookie_string: contents of cookie header (if None; necessary
                      cookies will be fetched first)
      @tld:           TLD of Vinted website to request; this parameter
                      does only matter if the given cookie_string is
                      domain-specific, otherwise all ads will load on
                      any version of the Vinted website

    Out:
      @lang:          ISO639-3 language code of the advertisement text;
                      note that in practice this might not always
                      correspond to the real language of the ad text
      @text:          advertisement text ready to be included in the
                      dataset
      @cookie_string: updated cookie string based on response headers
    """
    if not cookie_string:
        cookie_string = get_cookie_string(tld=tld)  # required!

    # warning: do NOT add GET parameter ?localise=true to the URL,
    #          since that will auto-translate the ad using Google
    base_url = 'https://www.vinted.{tld:s}/api/v2/items/{id:d}'

    req = Request(base_url.format(id=id, tld=tld))

    req.add_header(
        'Cookie',
        cookie_string
    )

    # Otherwise 403 Forbidden
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
        + 'Gecko/20100101 Firefox/106.0'
    )

    try:
        response = urlopen(req)
    except HTTPError as error:
        print('\r'+'Encountered an HTTP error: ', error)
        print('Occurred when requesting: ', base_url.format(id=id, tld=tld))

        # if error.code == 100:  # not authorized
        #     return 100
        return False

    # extracting updated value for 'secret cookie' _vinted_fr_session
    cookies = re.findall('(_vinted_fr_session=[^;]*);',
                         response.getheader('set-cookie'))

    if cookies:
        cookie_string = cookies[0]  # could have used re.search as well

    # extracting information from the advertisement data
    json_data = response.read().decode('utf-8')

    ad = json.loads(json_data)

    if ad['item']['country_id'] not in vinted_country_id_to_lang_ISO639_3:
        raise Exception("Advertisement locale not supported by scraper")

    lang = vinted_country_id_to_lang_ISO639_3[ad['item']['country_id']]
    text = ad['item']['description'].replace('\n', ' - ')

    return lang, text, cookie_string


def get_recent_ad_ids(lang: str, cookie_string: str = None,
                      max_timestamp: int = None) -> T[list, int, str]:
    """
    Although Vinted, like many other platforms, auto increments adver-
    tisement IDs, Vinted operates on many different websites in many
    different countries; all IDs work globally on all Vinted websites.
    It is therefore better to fetch locale-specific IDs beforehand.
    In total, 16 IDs are returned per request.

    In:
      @lang:          desired language of datasamples (can not be
                      guaranteed as users can always post in another
                      language; e.g., expats writing in English)
      @cookie_string: contents of cookie header (if None; necessary
                      cookies will be fetched first)
      @max_timestamp: advertisements newer than this UNIX timestamp
                      will not be returned (acts like a sort of
                      pagination mechanism)

    Out:
      @recent_ids:    list of advertisement IDs ready to be fetched
      @max_timestamp: new value for max_timestamp such that no samples
                      will be included in the next response, that were
                      returned now
      @cookie_string: updated cookie string based on response headers
    """
    if not max_timestamp:
        max_timestamp = int(time.time()) - 600  # minus ten minutes

    country_id = vinted_lang_ISO639_3_to_country_id[lang]
    tld = vinted_country_id_to_tld[country_id]
    base_url = 'https://vinted.{tld:s}/api/v2/feed/events?max_score={time:d}'

    if not cookie_string:  # strict requirement by Vinted
        cookie_string = get_cookie_string(tld=tld)

    overview_req = Request(base_url.format(tld=tld, time=max_timestamp))

    overview_req.add_header(
        'Cookie',
        cookie_string
    )

    # Otherwise 403 Forbidden
    overview_req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
        + 'Gecko/20100101 Firefox/106.0'
    )

    try:
        overview_response = urlopen(overview_req)
        overview_json = overview_response.read().decode('utf-8')
        recent_ads = json.loads(overview_json)
    except Exception:
        raise Exception("Could not fetch starting IDs (possible block)")

    # extracting updated value for 'secret cookie' _vinted_fr_session
    cookies = re.findall('(_vinted_fr_session=[^;]*);',
                         overview_response.getheader('set-cookie'))

    if cookies:
        cookie_string = cookies[0]  # could have used re.search as well

    max_timestamp = recent_ads['max_score']
    recent_ids = []

    for ad in recent_ads['feed_events']:
        if ad['entity']['is_visible'] != 1:
            continue

        recent_ids.append(ad['entity']['id'])

    if len(recent_ids) == 0:
        raise Exception("runout")

    return recent_ids, max_timestamp, cookie_string
