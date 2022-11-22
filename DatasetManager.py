import yaml
import glob
import time
import os
from yaml.loader import SafeLoader
from collections import defaultdict


class DatasetManager:
    """
    The dataset consists of a folder containing YAML files. All files
    within the folder are considered part of the dataset and loaded by
    this class. This class further provides functionality for filtering
    and merging data, and printing stats. Internally, every datasample
    is represented as a dict which can hold the following attributes:

    [*] identifier - internal ID of text sample (translated texts have
                     the same identifier as the original)
    [*] lang_ISO639_3 - language of text sample (if translated, this is
                        the translated language)
    [ ] lang_ISO639_3 - original language of the text sample (only if
        _original       the element concerns a translated sample)
    [ ] sentences     - text split into sentences with original and
                        translated versions per sentence (only when
                        element considers a translated sample using
                        specific engines (e.g., GoogleUnofficial)
    [*] source        - source of the text sample (i.e., name of the
                        platform from which the sample was scraped)
    [*] text          - the contents of the text sample (no new lines)
    [*] translated    - boolean
    [ ] translation   - Engine using which sample was translated (e.g.,
        _vendor         Google; only if element is a translated sample)
    [*] type          - Type of sample (e.g., Marketplace or Forum)

    * = mandatory

    Note: the way in which the dataset is managed is very inefficient
          and operations are slow. This is meant as a simple, initial,
          portable solution. An SQL database might be better.
    """
    def __init__(self, folder: str = 'output'):
        """
        Init (see class description above).

        In:
          @folder: relative path to dataset folder

        Out:
          n/a
        """
        self.folder = folder
        self.data = []
        self.load_data()

    def load_data(self) -> None:
        """
        Parses YAML files in dataset folder and stores their contents
        in the class instance. Folder location is set during init.

        In:
          - void

        Out:
          - void
        """
        chunks = glob.glob(self.folder + '/*.yaml')

        for file in chunks:
            with open(file) as handler:
                self.data += yaml.load(handler, Loader=SafeLoader)

    def merge(self) -> None:
        """
        Merges all YAML files in the dataset folder into a single file.

        In:
          - void

        Out:
          - void
        """
        chunks = glob.glob(self.folder + '/*.yaml')

        with open('output/' + str(time.time()) + '.yaml', 'w') as out:
            yaml.dump(self.data, out)

        for file in chunks:
            os.remove(file)

    def stats(self) -> None:
        """
        Prints a general description of the database contents.

        In:
          - void

        Out:
          - void
        """
        types = {}
        sources = {}
        original_languages = {}
        translations = 0
        total_items = len(self.data)

        for item in self.data:
            if item['translated']:
                translations += 1
                continue  # we only care about original items now

            if item['type'] not in types:
                types[item['type']] = 0

            if item['source'] not in sources:
                sources[item['source']] = 0

            if item['lang_ISO639_3'] not in original_languages:
                original_languages[item['lang_ISO639_3']] = 0

            types[item['type']] += 1
            sources[item['source']] += 1
            original_languages[item['lang_ISO639_3']] += 1

        print('The dataset contains %d texts, of which %d original texts'
              ' and %d translations, with the following characteristics:'
              % (total_items, total_items - translations, translations))

        print('Types: ', types)
        print('Sources: ', sources)
        print('Original languages: ', original_languages)

    def get_untranslated(self, lang_from: str = None, lang_to: str = None,
                         limit: int = None, type_text: str = None,
                         src_text: str = None) -> list:
        """
        Returns (original) samples that are not yet translated into (a)
        (certain) language(s).

        In:
          @lang_from: Source language of sample (ISO639-3); if not set,
                      all languages will be considered
          @lang_to:   Target language (ISO639-3), language to translate
                      into. If not set, only samples will be included
                      that have not been translated into ANY language
          @limit:     Number of samples to return; if None, no limit
          @type_text: Filter for 'type' attribute (i.e., Marketplace)
          @src_text:  Filter for 'source' attribute (i.e., Vinted)

        Out:
          @results:   List of data samples that meet the requirements
        """
        translated = {}    # languages into which a text is translated
        untranslated = {}  # holds elements with original texts

        for item in self.data:
            if item['translated']:
                if item['identifier'] not in translated:
                    translated[item['identifier']] = []
                translated[item['identifier']].append(item['lang_ISO639_3'])
                continue
            if lang_from is not None and item['lang_ISO639_3'] != lang_from:
                continue
            if type_text is not None and item['type'] != type_text:
                continue
            if src_text is not None and item['source'] != src_text:
                continue

            untranslated[item['identifier']] = item

        results = []

        i = 0

        for text_identifier in untranslated.keys():
            if limit is not None and i >= limit:
                break
            if text_identifier in translated:
                if lang_to is None or lang_to in translated[text_identifier]:
                    continue

            results.append(untranslated[text_identifier])
            i += 1

        return results

    def get_subset(self, attributes: dict = {}) -> list:
        """
        Filters the dataset by the given attributes and values.

        In:
          @attributes: Dict with attributes as its keys and the values
                       that datasamples need to match as its values

        Out:
          @results:   List of data samples that meet the requirements
        """
        subset_data = []

        for item in self.data:
            do_not_append = False

            for attribute in attributes:
                if (attribute not in item
                        or item[attribute] != attributes[attribute]):
                    do_not_append = True
                    break

            if not do_not_append:
                subset_data.append(item)

        return subset_data
