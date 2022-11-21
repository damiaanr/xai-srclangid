from .vendors.GoogleUnofficial.Translator import *
from yaml.loader import SafeLoader
import yaml
import time


class Translator:
    """
    This main Translator class handles instances of specific vendor-
    specific translator classes dynamically and keeps track of IO for
    the dataset files.
    """
    PROFILES = {
        'GoogleUnofficial': {'splits_into_sentences': True},
    }

    def __init__(self, profile: str, output_folder: str = 'output'):
        """
        Init (see class description above).

        In:
          @profile:       Translation vendor (key in global PROFILES)
          @output_folder: Folder in which new samples will be stored

        Out:
          n/a
        """
        if profile not in self.PROFILES:
            raise Exception("Translation profile does not exist")

        self.output_folder = output_folder

        self.engine = globals()[profile + "Translator"]()  # dynamic load
        self.profile = profile
        self.data = []

    def translate(self, data: list, lang_from: str, lang_to: str,
                  sleep: int = 0.5) -> None:
        """
        Creates a new element (with a translation) for every given
        element and stores only the newly created translated elements
        internally in the class instance (which should be saved later).

        In:
          @data:      List of complete dataset elements (the same as
                      how they are stored internally in DatasetManager)
          @lang_from: Source language (ISO639-3)
          @lang_to:   Target language (ISO639-3)
          @sleep:     Seconds to sleep between translation requests

        Out:
          - void
        """

        i = 0
        total = len(data)

        for item in data:
            translated_element = item.copy()

            translated_sents, translated_text = self.engine.translate(
                lang_from, lang_to, item['text'])
            translated_element['lang_ISO639_3_original'] = \
                translated_element['lang_ISO639_3']
            translated_element['lang_ISO639_3'] = lang_to
            translated_element['text'] = translated_text
            translated_element['translated'] = True
            translated_element['translation_vendor'] = 'GoogleUnofficial'
            translated_element['sentences'] = translated_sents

            self.data.append(translated_element)

            print("\r" + "Translated a text! [%d/%d]" % (i+1, total), end='')

            i += 1

            time.sleep(sleep)

        print('')

    def save(self, file_name: str = None) -> None:
        """
        Writes all translated samples to a separate file in the dataset
        folder.

        In:
          @file_name: filename (excluding extension); if None, the
                      current timestamp (with decimals) will be taken

        Out:
          - void
        """
        if file_name is None:
            file_name = str(time.time())

        with open(self.output_folder + '/' + file_name + '.yaml', 'w') as out:
            documents = yaml.dump(self.data, out)
