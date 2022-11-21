from bases.wals.Evaluator import WalsEvaluator
from typing import Union as U
from .Scores import Scores
import time
import itertools
import glob
import pickle
import os


class Evaluator:
    """
    Main class that dynamically interacts with different evaluator
    classes that each encodes a different approach (e.g., comparing
    Wals features). Upon initiating an instance of this class, the
    scores will be evaluated (or loaded from cache) automatically and
    can be accessed through the scores property.
    """
    CACHE_FOLDER = 'scores/'
    LANGUAGES_FILE = 'languages.txt'
    METHODS = ['Wals']

    def __init__(self, method: str = 'Wals', load_from_cache: bool = False,
                 cache_file: str = None,
                 languages_of_interest: U[list, str] = None):
        """
        Init (see class description above).

        In:
          @method:          Evaluation `base' (key in global METHODS)
          @load_from_cache: if False, scores are freshly calculated and
                            saved to cache
          @cache_file:      Pickle file in global CACHE_FOLDER (incl.
                            extension); if not set, the latest file
                            in the folder is loaded
          @languages_of:    If set, either list of ISO639-3 codes or
           _interest        a string representing a relative file-path
                            with language codes seperated by newlines;
                            if None, global LANGUAGES_FILE will be
                            loaded (see load_languages_of_interest())

        Out:
          - void
        """
        if method not in self.METHODS:
            raise Exception("Given method not supported")

        self.method = method
        self.service = globals()[method + "Evaluator"]()  # dynamic class

        self.load_languages_of_interest()

        if load_from_cache:
            self.load_scores_from_cache(cache_file=cache_file)
        else:
            self.evaluate_scores()
            self.save_scores_to_cache()

    def load_scores_from_cache(self, cache_file=None) -> None:
        """
        Loads pickle file from cache and stores scores within class.

        In:
          @cache_file: if not set, latest cache file will be loaded

        Out:
          - void
        """
        if not cache_file:
            latest_files = glob.glob(self.CACHE_FOLDER + self.method + '_*.p')

            if latest_files:
                cache_file = max(latest_files, key=os.path.getctime)
            else:
                raise Exception("Cache is empty")
        else:
            cache_file = self.CACHE_FOLDER + cache_file

        self.scores = pickle.load(open(cache_file, "rb"))

    def save_scores_to_cache(self) -> None:
        """
        Stores scores in a pickle file for quicker loading on
        consecutive runs. Files are stored in the globally denoted
        cache folder. File names are based on the current timestamp.

        In:
          - void

        Out:
          - void
        """
        cache_file = self.CACHE_FOLDER + self.method + '_' \
            + str(time.time()) + '.p'
        pickle.dump(self.scores, open(cache_file, 'wb'))

    def evaluate_scores(self) -> None:
        """
        Calculates score for every possible language pair and stores it
        in the class instance. (Note: it uses combinations, not perms.)

        In:
          - void

        Out:
          - void
        """
        self.scores = Scores()

        for l1, l2 in itertools.combinations(self.languages, r=2):
            self.scores[(l1, l2)] = self.service.evaluate_score(l1, l2)

    def load_languages_of_interest(self, file: str = None) -> None:
        """
        To-be-analysed languages can be loaded directly from a file,
        instead of manually inserted upon initialisation. The file
        should contain an ISO639-3 language code per line/language.
        """
        if not file:
            file = self.LANGUAGES_FILE

        if not os.path.isfile(file):
            raise Exception("No languages of interest specified")

        handle = open(file, 'r')
        data = handle.read()
        self.languages = data.splitlines()
        handle.close()
