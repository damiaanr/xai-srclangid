import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import urllib.parse
from .src.functions import *
import json
from typing import Tuple as T


class GoogleUnofficialTranslator:
    """
    Vendor-specific class that provides translated texts ready to be
    included in the dataset, based on existing dataset elements.

    GoogleUnofficial is a translation vendor that takes advantage of an
    API endpoint intended for a Chrome plugin. The endpoint is stable
    as of November 2022. The endpoint however queries an old, inferior
    model of Google Translate (possibly not a Transformer model).
    """
    def request(sl: str, tl: str, q: str) -> dict:
        """
        Internal method used to request the API endpoint. Note: this is
        a static method!

        In:
          @sl: Source language (note: in ISO639-1!)
          @tl: Target language (note: in ISO639-1!)
          @q:  String of text to be translated

        Out:
          @json: parsed JSON response of translation endpoint.
        """
        base_url = 'https://clients5.google.com/translate_a/single?dj=1' \
            + '&dt=t&dt=sp&dt=ld&dt=bd&client=dict-chrome-ex' \
            + '&sl={sl:s}&tl={tl:s}&q={q:s}'

        req = Request(base_url.format(sl=sl, tl=tl, q=urllib.parse.quote(q)))

        req.add_header(
            'User-Agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            + '(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        )

        try:
            response = urlopen(req)
        except HTTPError as error:
            print('Encountered an HTTP error: ', error)
            return False

        _json = response.read().decode('utf-8')
        data = json.loads(_json)

        return data

    def get_valid_languages(self) -> list:
        """
        Simple method that returns a list of all languages supported by
        the API endpoint. These are hard-coded in src/functions.py.

        In:
          - void

        Out:
          @list: of supported languages in ISO639-3
        """
        return list(iso_639_3_to_1.keys())

    def translate(self, iso_639_3_from: str, iso_639_3_to: str,
                  text: str) -> T[list, str]:
        """
        Does the `translation magic'.

        In:
          @iso_639_3_from: Source language (note: in ISO639-3!)
          @iso_639_3_to:   Target language (note: in ISO639-3!)
          @text:           String to be translated

        Out:
          @sentences:       List of individual sentences; contains
                            dicts with the original and translation
          @translated_text: Translated text
        """
        resulting_data = GoogleUnofficialTranslator.request(
            iso_639_3_to_1[iso_639_3_from],
            iso_639_3_to_1[iso_639_3_to],
            text
        )

        sentences = []
        translated_text = ""

        for sentence in resulting_data['sentences']:
            sentences.append({'original':    sentence['orig'],
                              'translation': sentence['trans']})
            translated_text += sentence['trans']

        return sentences, translated_text
