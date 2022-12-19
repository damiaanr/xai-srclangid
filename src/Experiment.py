from collections import Counter
from .Languageset import Languageset
import numpy as np
import math


class Experiment:
    """
    Each Experiment() class instance performs a single experiment
    over multiple categories within a dataset (e.g., translations
    with different source languages) represented by a dynamically
    set of features. All languages are internally represented by
    instances of Languageset(), which, in turn, holds instances of
    Text() for individual samples.

    Recommended workflow:

    1. Add different languages to the experiment using add_language()
    2. Add different features for these languages using add_features()
    3. Generate a train- and test set using split_dataset()
    4. Train and test a model using means external to this class
    """

    # Warning: the list of features below should correspond to get_..()
    #          methods within the Text() class
    FEATURES = ['charngrams', 'posngrams', 'posentropy', 'predicateorder',
                'verbaspect', 'adjnounorder', 'cases', 'negations',
                'morphngram']

    def __init__(self, num_samples: int):
        """
        Init method.

        In:
          @num_samples: number of samples PER language to include in
                        the experiment
        """
        self.language_sets = {}
        self.features = {}  # dict of 2D NumPy arrays: samples*features
        self.feature_keys = []
        self.labels = []
        self.labels_index = []  # used in get_sample_by_index() too!
        self.num_samples = num_samples
        self.features_added = False  # to prevent languages added later

    def split_dataset(self, train_fraction: int = 0.8):
        """
        Generates a train- and a test set from the already stored
        features for all represented language categories. Feature names
        and class indices are returned as well.

        In:
          @train_fraction: fraction of dataset that should be used as
                           data for training

        Out:
          @train_samples: 2-D NumPy array of sample representations
          @train_labels:  int (>= 0) corresponding to a language_set
                          identifier mapped in @labels_index
          @test_samples:  see @train_samples
          @test_labels:   see @test_labels
          @labels_index:  list of language_set identifiers where each
                          ith position in the list corresponds to class
                          label i in @train_labels and @test_labels
          @feature_index: list of feature keys where each ith position
                          in the list corresponds to the ith feature in
                          the second dimension of the returned samples
                          NumpY arrays
        """

        self.splitted_fraction = train_fraction  # for index traceback

        # Note: num_... is PER language!
        num_train = math.floor(self.num_samples * train_fraction)
        num_test = self.num_samples - num_train

        # All entries will be filled, so np.empty() is not dangerous
        train_samples = np.empty((num_train * len(self.language_sets),
                                  len(self.feature_keys)))
        train_labels = np.empty((num_train * len(self.language_sets)))

        test_samples = np.empty((num_test * len(self.language_sets),
                                 len(self.feature_keys)))
        test_labels = np.empty((num_test * len(self.language_sets)))

        self.labels_index = []  # will contain category identifiers

        # Visualisation: from 'top' to 'bottom', array will be filled
        # by evenly spaced chunks (one for each language/category).
        # The features for each category (which were already stored in
        # self.features()) are themselves also split (according to the
        # given train/test ratio) and both parts added to different
        # arrays (top-to-bottom, as explained).
        for i, item in enumerate(self.features.items()):
            lang_identifier, features = item

            l_train = num_train * (i)
            h_train = num_train * (i + 1)

            train_samples[l_train:h_train, :] = features[0:num_train, :]
            train_labels[l_train:h_train] = np.array([i] * num_train)

            l_test = num_test * (i)
            h_test = num_test * (i + 1)

            hf_test = num_train+num_test

            test_samples[l_test:h_test, :] = features[num_train:hf_test, :]
            test_labels[l_test:h_test] = np.array([i] * num_test)

            self.labels_index.append(lang_identifier)

        return train_samples, train_labels, test_samples, test_labels, \
            self.labels_index, self.feature_keys

    def get_sample_by_index(self, index: int, test: bool = True):
        """
        Method that returns a Text() instance based on an index within
        the train- or test set returned by split_dataset(). Handy for
        inspections of individual datasamples after model was trained.

        In:
          @index: the index within the train or test NumPy array (>=0)
          @test:  if True, index is of test set, otherwise train set

        Out:
          @object: of type Text()
        """

        if not self.labels_index:
            raise Exception("data was not yet processed or no langs added")

        num_train = math.floor(self.num_samples * self.splitted_fraction)
        num_test = self.num_samples - num_train

        # Note: indices are 0-based and chunk sizes are not
        if test:
            langset_no = math.floor(index / num_test)
            id_sample = num_train + index % num_test
        else:
            langset_no = math.floor(index / num_train)
            id_sample = index % num_train

        lang_set = self.language_sets[self.labels_index[langset_no]]

        return lang_set.samples[id_sample]

    def add_language(self, lang: str, translated: bool,
                     lang_source: str = None) -> None:
        """
        Includes samples of a given language (optionally translated
        from a given source language) into the experiment. Samples are
        loaded directly from the scraper/translator dataset which works
        independently from this class. If samples were cached (not
        necessarily after being loaded by the DataManager (scraper/
        translator), samples are loaded from cache.

        See also add_language_set() to add a category not originating
        from the DataManager class' dataset.

        In:
          @lang:        ISO639-3 code of language to be added
          @translated:  if False, @lang is the original language; if
                        True, samples were translated from @lang_source
                        to @lang
          @lang_source: if @translated is True, this parameter speci-
                        fies the original language of the text samples;
                        if unset, samples might originate from various
                        source languages

        Out:
          - void
        """
        if self.features_added:
            raise Exception("lang should be added prior to defining features")

        language_set = Languageset(lang=lang, translated=translated,
                                   num_samples=self.num_samples,
                                   lang_source=lang_source)

        self.add_language_set(language_set)

    def add_language_set(self, language_set: Languageset) -> None:
        """
        Instead of loading samples dynamically from the DataManager
        class (the scraper/translator), language_sets can also be added
        directly.

        In:
          @language_set: the Languageset() object to be added

        Out:
          - void
        """

        # To prevent statistical mistakes from being made
        if len(language_set.samples) != self.num_samples:
            raise Exception("language set should contain "
                            + str(self.num_samples) + " samples!")

        self.language_sets[language_set.identifier] = language_set
        identifier = language_set.identifier
        self.features[identifier] = np.empty((self.num_samples, 0))

    def add_features(self, feature: str, options: dict = {},
                     top_n: int = None, ignore: list = [],
                     focus: list = None) -> None:
        """
        Convert all samples (of all languages) within the experiment
        to a specified feature representation (subsequent calls to the
        method are supported and will lead to concatenated feature
        vectors). Feature set to be calculated must be defined in the
        class global FEATURES.

        See the current class' description for more info.

        In:
          @feature: name of feature; should correspond to a get_...()
                    method within the Text() class
          @options: dict of arguments for the get_...() method call
          @top_n:   if features are simple occurrence frequencies (when
                    the method contains a list, see the class
                    description of Text()
          @ignore:  optional list of feature names that should be
                    excluded from the experiment (feature keys are
                    dict keys or list items as handled in Text().
          @focus:   if set, only the features explicitly given in this
                    list will be included in the experiment; all others
                    will be excluded (takes precedence over @ignore)

        Out:
          - void
        """
        if feature not in self.FEATURES:
            raise Exception("feature does not exist")

        self.features_added = True

        feature_keys = set()
        results = {}

        # first, we obtain the list of possible features
        for language_set in self.language_sets.values():
            results[language_set.identifier] = []

            running_results = []

            for sample in language_set.samples:
                feature_method = getattr(sample, "get_" + feature)
                result = feature_method(**options)

                if isinstance(result, dict):  # keys are feature keys
                    feature_keys.update(result.keys())
                elif isinstance(result, list):  # values = feature keys
                    running_results += result
                else:
                    raise Exception("could not construct feature list")

                results[language_set.identifier].append(result)

            if len(running_results) > 0:
                if top_n is not None:  # only most frequent = keys
                    frequency_list = Counter(running_results)

                    for value, _ in frequency_list.most_common(top_n):
                        feature_keys.add(value)
                else:
                    feature_keys.update(running_results)

        for not_wanted in ignore:
            feature_keys.remove(not_wanted)

        if focus is not None:
            if len(set(focus) - feature_keys) != 0:
                raise Exception("Not all given features were found")

            feature_keys = set(focus)

        feature_keys = list(feature_keys)

        # now we add the feature keys to the global index
        for feature_key in feature_keys:
            key = feature + "__"

            if isinstance(feature_key, list) \
                    or isinstance(feature_key, tuple):
                key += "_".join(feature_key)
            else:
                key += str(feature_key)

            self.feature_keys.append(key)

        # now we construct the feature values per sample and add to
        # the total storage of feature values (in a NumPy object)
        for lang_id, results in results.items():
            feature_vectors = np.empty((self.num_samples, len(feature_keys)))

            for i in range(len(results)):
                result = results[i]
                if isinstance(result, list):  # features are counts
                    feature_vector = -0 * np.ones(len(feature_keys))

                    for value in result:
                        if value in feature_keys:
                            feature_vector[feature_keys.index(value)] += 1

                elif isinstance(result, dict):  # other numerical vals
                    feature_vector = -1 * np.ones(len(feature_keys))

                    for key, value in result.items():
                        if key in feature_keys:
                            feature_vector[feature_keys.index(key)] = value

                feature_vectors[i, :] = feature_vector

            self.features[lang_id] = np.hstack((self.features[lang_id],
                                                feature_vectors))
