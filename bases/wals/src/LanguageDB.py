import csv
from typing import Tuple as T


class LanguageDB:
    """
    LanguageDB() is a service-class that provides an interface for
    the WALS database (consisting of .csv-files).
    """

    def __init__(self, data_path: str = "bases/wals/data/"):
        """
        Init (see class description above).

        In:
          @data_path: path to WALS dataset (download from wals.info)

        Out:
          n/a
        """
        self.DATA_PATH = data_path
        self.populate_db_defaults()
        self.characteristics_populated = False

    def populate_db_defaults(self) -> None:
        """
        Parses general language data and stores on class-level in two
        different dicts: languages_wals (all data); ..._iso639_3 (only
        WALS ID (for inference)).

        In:
          - void

        Out:
          - void
        """
        with open(self.DATA_PATH + 'languages.csv') as languages_file:
            languages = csv.DictReader(languages_file)

            self.languages_wals = {}
            self.languages_iso639_3 = {}

            # small DB; so this redundancy-for-convenience is not bad
            for entry in languages:
                self.languages_wals[entry['ID']] = entry
                self.languages_iso639_3[entry['ISO639P3code']] = \
                    {'ID': entry['ID']}

    def populate_characteristics(self, explicit: bool = False,
                                 wals_codes: list = None) -> None:
        """
        Parses language-specific characteristics and adds parameters
        and values that apply to languages_wals dict (note: NOT the
        ..._iso639_3 dict). Sets a class-level boolean to True if for
        ALL languages characteristics were parsed.

        In:
          @explicit:   if True, parameter names and values are stored
                       instead of codes (important for
                       Language.get_characteristic() etc.)
          @wals_codes: list of WALS codes of languages to process; if
                       empty, all languages will be parsed.

        Out:
          - void
        """
        charc_keys, charc_values, charc_chapters = LanguageDB. \
            get_characteristics_fields(data_path=self.DATA_PATH)

        # storing the chapter ids for every parameter (as below) might
        # be useful for applications where parameters for languages
        # need to be filtered (e.g., on area (phonology etc.))
        self.params_chapter_mapping = charc_chapters

        #  doing this in p..._db_defaults() would make Ø-dicts ambiguous
        if wals_codes:
            for wals_code in wals_codes:
                self.languages_wals[wals_code]['Characteristics'] = {}
        else:
            for wals_code in self.languages_wals:
                self.languages_wals[wals_code]['Characteristics'] = {}

        file_values = self.DATA_PATH + 'values.csv'

        with open(file_values, encoding='utf8') as values_file:
            values = csv.reader(values_file)
            next(values)

            for entry in values:
                if wals_codes and entry[1] not in wals_codes:
                    continue

                if explicit:
                    entry[2] = charc_keys[entry[2]]
                    entry[4] = charc_values[entry[4]]

                self.languages_wals[entry[1]]['Characteristics'][entry[2]] = \
                    entry[4]

        if not wals_codes:
            self.characteristics_populated = True

    def verify_wals_code(self, wals_code: str) -> bool:
        """
        In:
          @wals_code: language code within WALS

        Out:
          @bool: True if language code is valid (exists in WALS DB)
        """
        return True if wals_code in self.languages_wals else False

    def verify_iso639_3_code(self, iso639_3_code: str) -> bool:
        """
        In:
          @iso639_3_code: standardised ISO639-3 language code

        Out:
          @bool: True if language code is valid (exists in WALS DB)
        """
        return True if iso639_3_code in self.languages_iso639_3 else False

    def get_wals_code_by_iso639_3(self, iso639_3_code: str) -> bool:
        """
        In:
          @iso639_3_code: standardised ISO639-3 language code

        Out:
          @wals_code: language code within WALS
        """
        return self.languages_iso639_3[iso639_3_code]['ID']

    def get_characteristics_fields(data_path: str = "bases/wals/data/") \
            -> T[dict, dict, dict]:
        """
        Provides a mapping between codes and explicit names for keys
        and values of parameters of language characteristics. Only
        used when language-specific traits are explicitly stored.
        Note: this method is very inefficient if repeatedly called.
        This is a static method.

        In:
          @data_path: path to WALS dataset (download from wals.info)

        Out:
          @charc_keys:   dict, parameter codes as keys, names as values
          @charc_values: dict, value codes as keys, desc. as values
          @charc_areas:  dict, parameter codes as keys, area code as
                         values
        """
        charc_keys = {}
        charc_chapters = {}
        charc_values = {}

        file_params = data_path + 'parameters.csv'
        file_codes = data_path + 'codes.csv'

        with open(file_params, encoding='utf8') as keys_file:
            keys = csv.reader(keys_file)
            next(keys)

            for key in keys:
                charc_keys[key[0]] = key[1]
                charc_chapters[key[0]] = key[3]

        with open(file_codes, encoding='utf8') as values_file:
            values = csv.reader(values_file)
            next(values)

            for value in values:
                charc_values[value[0]] = value[2]

        return charc_keys, charc_values, charc_chapters

    def get_chapters_fields(data_path: str = "bases/wals/data/") -> dict:
        """
        Returns a mapping between chapter IDs and their corresponding
        data fields (e.g., 'Area_ID', as listed in the CSV header of
        chapters.csv in the WALS data).

        In:
          @data_path: path to WALS dataset (download from wals.info)

        Out:
          @dict: with chapter IDs as keys and a tuple as values
        """
        fields = {}

        file_chapters = data_path + 'chapters.csv'

        with open(file_chapters, encoding='utf8') as chapters_file:
            values = csv.reader(chapters_file)
            next(values)

            for value in values:
                fields[value[0]] = tuple(value[1:])  # id is cut off !!

        return fields
