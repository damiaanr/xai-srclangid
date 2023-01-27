from .src.functions import *
import glob
import os
import pickle
import time


class VintedScraper:
    """
    Platform-specific class that provides parsed advertisements texts
    ready to be included in the dataset. Handles cache to keep track of
    which ads were already parsed. The cache also contains ids of ads
    that failed to fetch due to request errors.

    The Vinted scraper accepts 12 languages: lit, deu, ces, spa, nld,
    swe, eng, pol, ita, por, slk, and hun.

    The global class-level properties are not meant to be changed by
    the user continously; they are set on the basis of empirical obser-
    vations from rough experiments (that's why they are hard-coded).
    """
    CACHE_FOLDER = 'cache/'  # relative to current file; not workingdir
    SLEEP_TIME = 0.5  # time to wait (in seconds) between requests
    MAX_FAILED_REQS = 5  # maximum of failed requests before stopping
    MAX_CONSECUTIVE_ERRORS = 5  # maximum HTTP errs after which to stop

    def __init__(self, lang: str, cache_file: str = None) -> None:
        """
        Init (see class description above).

        In:
          @lang:       language (in ISO639-3) to scrape
          @cache_file: filename (incl. extension) of pickle file within
                       hard-coded CACHE_FOLDER global containing
                       previously parsed ad ids; if None, the most
                       recent file in that folder is loaded

        Out:
          - void
        """
        if lang not in vinted_lang_ISO639_3_to_country_id:
            raise Exception("language not supported by VintedScraper")

        self.cache_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), self.CACHE_FOLDER)

        self.load_cache(cache_file=cache_file)
        self.cookie_string = None
        self.max_timestamp = None
        self.current_id = None
        self.ids_to_fetch = []  # will be filled later automatically
        self.lang = lang

        country_id = vinted_lang_ISO639_3_to_country_id[lang]
        self.tld = vinted_country_id_to_tld[country_id]

        time.sleep(self.SLEEP_TIME)

    def __del__(self) -> None:
        """
        Class instance should be destructed properly to store cache.

        In:
          - void

        Out:
          - void
        """
        self.save_cache()

    def next_item(self) -> str:
        """
        Returns a single parsed advertisement text. Although Vinted
        auto-increment ads, we can not simply take an ad ID and de-
        crement it, as Vinted ad IDs are global over all platforms,
        so decrementing leads to the mixing of different languages.
        Therefore, 16 new ad IDs are fetched, whenever necessary,
        from a language-specific feed.

        In:
          - void

        Out:
          @text: Raw advertisement text (ready for dataset)
        """
        i = 0
        text = False
        consecutive_error_count = 0

        while i < self.MAX_FAILED_REQS and not text:
            i += 1

            # decreasing the ad number until id that was not yet parsed
            while not self.current_id or self.current_id in self.parsed_ids:
                if len(self.ids_to_fetch) == 0:  # fetch new IDs
                    recent_ids, max_stamp, cookie_string = get_recent_ad_ids(
                        lang=self.lang,
                        cookie_string=self.cookie_string,
                        max_timestamp=self.max_timestamp
                    )

                    self.cookie_string = cookie_string
                    self.ids_to_fetch = recent_ids
                    self.max_timestamp = max_stamp

                self.current_id = self.ids_to_fetch.pop()
                time.sleep(self.SLEEP_TIME)

            time.sleep(self.SLEEP_TIME)
            self.parsed_ids.append(self.current_id)

            parsed_ad = get_ad_text_by_id(id=self.current_id,
                                          cookie_string=self.cookie_string,
                                          tld=self.tld)

            if type(parsed_ad) is not tuple:  # OK: (html,cookie_string)
                if not parsed_ad:  # False
                    consecutive_error_count += 1

                    if consecutive_error_count >= self.MAX_CONSECUTIVE_ERRORS:
                        raise Exception("Max. of consecutive errors reached")

                    continue
            else:
                _, text, cookie_string = parsed_ad
                self.cookie_string = cookie_string  # for later calls

            consecutive_error_count = 0

        return text

    def load_cache(self, cache_file: str = None) -> None:
        """
        The cache is a pickle containing a list with attempted ad ids.
        All ids are stored in the class and updated while scraping.

        In:
          @cache_file: filename (including extension) within hard-coded
                       cache folder (see class properties); if None,
                       most recent file within the folder is loaded.

        Out:
          - void
        """
        if cache_file is None:
            latest_files = glob.glob(self.cache_path + 'ids_*.p')

            if latest_files:
                cache_file = max(latest_files, key=os.path.getctime)
            else:
                self.parsed_ids = []
        else:
            cache_file = self.cache_path + cache_file

        if cache_file:
            self.old_cache_file = cache_file
            self.parsed_ids = pickle.load(open(cache_file, "rb"))
        else:
            self.old_cache_file = None

    def save_cache(self) -> None:
        """
        After scraping, this method should be called in order to save
        the updated list of already-parsed ad ids to the cache.

        In:
          - void

        Out:
          - void
        """
        cache_file = self.cache_path + 'ids_' + str(time.time()) + '.p'
        pickle.dump(self.parsed_ids, open(cache_file, 'wb'))

        if self.old_cache_file:
            os.remove(self.old_cache_file)
