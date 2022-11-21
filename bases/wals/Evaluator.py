import pickle
import itertools
import math
import glob
import os
import time
from .src.Language import Language
from .src.LanguageDB import LanguageDB


class WalsEvaluator:
    """
    WalsEvaluator() is the service-class used for calculating language
    similarity scores on the basis of overlapping values for
    characteristic-parameters set within the Wals database.

    Mainly provides the evaluate_score() method to calculate
    scores.
    """
    # if below this int, similarity score (before normalisation) becomes 0
    MINIMUM_MUTUAL_CHARACTERISTICS = 30

    # factor of most similar scores to scale (0.01 means that top-1% of
    # scores is re-scaled to 0–1 (bottom-99% of similarity scores
    # becomes zero, just like the lowest score within the top-1%)
    NORMALISE_THRESHOLD = 0.0005

    CACHE_FOLDER = 'bases/wals/cache/'

    def __init__(self, load_from_cache: bool = True, cache_file: str = None):
        """
        Init (see class description above).

        In:
          @load_from_cache: if True, Similarity scores are pre-loaded
          @cache_file:      if not set, latest file in cache directory
                            will be loaded (see class global)

        Out:
          - void
        """
        self.language_db = LanguageDB()
        self.languages = {wals_code: Language(wals_code, self.language_db)
                          for wals_code in self.language_db.languages_wals}
        self.language_pairs = list(itertools.combinations(self.languages, r=2))

        if load_from_cache:
            self.load_scores_from_cache(cache_file=cache_file)
        else:
            self.populate_base_scores()
            self.normalise_base_scores()
            self.save_scores_to_cache()

    def save_scores_to_cache(self) -> None:
        """
        Collects all language pair combinations and saves individual
        scores to a pickle file in the globally denoted cache folder.
        The file name is based on the current timestamp.

        In:
          - void

        Out:
          - void
        """
        scores = []

        for l1, l2 in self.language_pairs:
            scores.append((l1, l2, self.languages[l1].similarity_scores[l2]))

        cache_file = self.CACHE_FOLDER + 'scores_' + str(time.time()) + '.p'

        pickle.dump(scores, open(cache_file, 'wb'))

    def load_scores_from_cache(self, cache_file: str = None) -> None:
        """
        Loads pickle file from cache and stores similarity scores within
        each Language() instance individually (i.e., no combinations).

        In:
          @cache_file: filename within cache_folder including extension
                       if not set, most recently modified file is loaded

        Out:
          - void
        """
        if not cache_file:
            latest_files = glob.glob(self.CACHE_FOLDER + 'scores_*.p')

            if latest_files:
                cache_file = max(latest_files, key=os.path.getctime)
            else:
                raise Exception("Cache is empty")
        else:
            cache_file = self.CACHE_FOLDER + cache_file

        cache_scores = pickle.load(open(cache_file, "rb"))

        for l1, l2, score in cache_scores:
            self.languages[l1].similarity_scores[l2] = score
            self.languages[l2].similarity_scores[l1] = score

    def calculate_base_score(self, l1: Language, l2: Language) -> None:
        """
        Calculates similarity score as the fraction of matching values
        for language-specific parameters within WALS. If the number of
        possible parameter comparisons is below the set number (i.e.,
        too less data), similarity score is set to zero.

        In:
          @l1: instance of Language()
          @l2: instance of Language()

        Out:
          @score: float representing language similarity
        """
        num_charcs = 0
        num_charcs_eq = 0

        for charc in l1.get_mutual_characteristics(l2):
            if l1.get_characteristic(charc) == l2.get_characteristic(charc):
                num_charcs_eq += 1
            num_charcs += 1

        if num_charcs < self.MINIMUM_MUTUAL_CHARACTERISTICS:
            return 0
        else:
            return num_charcs_eq / num_charcs

    def populate_base_scores(self, save_scores: bool = True) -> None:
        """
        Calculates similarity scores for each unique combination of
        languages and stores this score within each Language() instance.

        In:
          @save_scores: if True, list of scores is stored within the
                        object; needed if scores are normalised later

        Out:
          - void
        """
        if save_scores:
            self.scores = []

        for l1, l2 in self.language_pairs:
            score = self.calculate_base_score(self.languages[l1],
                                              self.languages[l2])

            self.languages[l1].similarity_scores[l2] = score
            self.languages[l2].similarity_scores[l1] = score

            if save_scores:
                self.scores.append(score)

    def normalise_base_scores(self) -> None:
        """
        Re-scales scores such that only very similar languages score
        above zero. See documentation for NORMALISE_THRESHOLD global.

        In:
          - void

        Out:
          - void
        """
        if not hasattr(self, 'scores'):
            raise Exception("Base scores were not saved locally")

        self.scores.sort(reverse=True)

        thres_item = math.floor(len(self.scores)*self.NORMALISE_THRESHOLD)
        thres_value_l = self.scores[:thres_item][-1]
        thres_value_h = self.scores[0]
        thres_factor = thres_value_h - thres_value_l

        del self.scores  # normalising should be done only once

        for l1, l2 in self.language_pairs:
            score_base = self.languages[l1].similarity_scores[l2]

            if score_base < thres_value_l:
                score_normed = 0
            else:
                score_normed = (score_base - thres_value_l) / thres_factor

            self.languages[l1].similarity_scores[l2] = score_normed
            self.languages[l2].similarity_scores[l1] = score_normed

    def evaluate_score(self, l1: str, l2: str) -> float:
        """
        Returns score for a language pair specified in ISO639-3.

        In:
          @l1: standardised ISO639-3char language code (str)
          @l2: standardised ISO639-3char language code (str)

        Out:
          @score: float representing language similarity
        """
        if not self.language_db.verify_iso639_3_code(l1) \
                or not self.language_db.verify_iso639_3_code(l2):
            raise Exception("No record for this language pair in WALS")

        l1_wals = self.language_db.get_wals_code_by_iso639_3(l1)
        l2_wals = self.language_db.get_wals_code_by_iso639_3(l2)

        score = self.languages[l1_wals].similarity_scores[l2_wals]

        return score
