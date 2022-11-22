from .src.functions import *
from .src.AdParser import *
import glob
import os
import pickle
import time


class MarktplaatsScraper:
    """
    Platform-specific class that provides parsed advertisements texts
    ready to be included in the dataset. Handles cache to keep track of
    which ads were already parsed. The cache also contains ids of ads
    that failed to fetch due to request errors. However, most of these
    ads SHOULD fail, as the ad was simply deleted. In the case of a
    'mistake' (due to a block), it doesn't matter as there are plenty
    text  for the dataset (deliberate choice to not verify responses).

    The global class-level properties are not meant to be changed by
    the user continously; they are set on the basis of empirical obser-
    vations from rough experiments (that's why they are hard-coded).
    """
    CACHE_FOLDER = 'cache/'  # relative to current file; not workingdir
    SLEEP_TIME = 5  # time to wait (in seconds) between requests
    MAX_FAILED_REQS = 5  # maximum of failed requests before stopping
    MAX_CONSECUTIVE_ERRORS = 5  # maximum HTTP errs after which to stop

    def __init__(self, cache_file: str = None, get_new_last_id: bool = False,
                 from_last_id: int = None) -> None:
        """
        Init (see class description above).

        In:
          @cache_file:      filename (incl. extension) of pickle file
                            within hard-coded CACHE_FOLDER containing
                            previously parsed ad ids; if None, the most
                            recent file in that folder is loaded
          @get_new_last_id: if True, a new ad id is fetched from the
                            'new nearby' feed on Marktplaats; otherwise
                            last attempted id from cache forms the
                            starting point.
          @from_last_id:    if set, decrement starts from given id.

        Out:
          - void
        """
        self.cache_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), self.CACHE_FOLDER)

        self.load_cache(cache_file=cache_file)

        self.cookie_string = None

        time.sleep(self.SLEEP_TIME)

        if get_new_last_id or len(self.parsed_ids) == 0:
            self.current_id = get_recent_ad_id()
        elif from_last_id is not None:
            self.current_id = from_last_id
        else:
            self.current_id = self.parsed_ids[-1]

        self.parser = AdParser()

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
        Returns a single parsed advertisement text. Marktplaats auto-
        increments ad ids, so we simply decrement a recent ad ID to
        obtain new advertisements. No need for parsing listings or
        search result pages for advertisement ids continuously.

        In:
          - void

        Out:
          @yielded_text: Raw advertisement text (ready for dataset)
        """
        i = 0
        yielded_text = False
        consecutive_error_count = 0

        while i < self.MAX_FAILED_REQS and not yielded_text:
            i += 1

            # decreasing the ad number until id that was not yet parsed
            while self.current_id in self.parsed_ids:
                self.current_id -= 1

            time.sleep(self.SLEEP_TIME)
            self.parsed_ids.append(self.current_id)

            parsed_ad = get_ad_html_by_id(self.current_id, self.cookie_string)

            if type(parsed_ad) is not tuple:  # OK: (html,cookie_string)
                if not parsed_ad:  # False
                    consecutive_error_count += 1

                    if consecutive_error_count >= self.MAX_CONSECUTIVE_ERRORS:
                        raise Exception("Max. of consecutive errors reached")

                    continue
                elif parsed_ad == 503:  # given back explicitly
                    # (!) the below exception is read by main file
                    raise Exception("blocked")
                    break
            else:
                html, cookie_string = parsed_ad
                self.cookie_string = cookie_string  # for later calls

            consecutive_error_count = 0
            self.parser.feed(html)
            yielded_text = self.parser.yield_text()

            if yielded_text:  # convert newlines
                yielded_text = ' '.join(yielded_text.split())

        if not yielded_text:
            raise Exception("Failed to fetch an item")

        return yielded_text

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
